"""Read Android ELF64 objects and produce traceable native-only wheels."""
import base64
import csv
import hashlib
import io
import struct
import zipfile
from pathlib import Path


def elf_info(data):
    if len(data) < 64 or data[:6] != b'\x7fELF\x02\x01':
        raise ValueError('Expected little-endian ELF64')
    def read(fmt, offset):
        if offset < 0 or offset + struct.calcsize(fmt) > len(data):
            raise ValueError('Truncated ELF table')
        return struct.unpack_from(fmt, data, offset)
    machine = read('<H', 18)[0]
    if machine not in (62, 183):
        raise ValueError(f'Unsupported Android machine: {machine}')
    phoff, shoff = read('<QQ', 32)
    phsize, phcount, shsize, shcount = read('<HHHH', 54)
    if phsize < 56 or (shcount and shsize < 64):
        raise ValueError('Invalid ELF table entry size')
    loads, dynamic = [], None
    for i in range(phcount):
        typ, flags, off, va, _, size, _, align = read('<IIQQQQQQ', phoff+i*phsize)
        if off+size > len(data):
            raise ValueError('Truncated ELF segment')
        if typ == 1:
            loads.append({'offset':off,'address':va,'size':size,'alignment':align,
                          'congruent_16k':(off-va)%16384 == 0})
        if typ == 2:
            dynamic = (off, size)
    entries = []
    if dynamic:
        for pos in range(dynamic[0], sum(dynamic), 16):
            tag, value = read('<qQ', pos)
            if tag == 0:
                break
            entries.append((tag, value))
    def cstring(start):
        try:
            end = data.index(b'\0', start)
        except ValueError:
            raise ValueError('Unterminated ELF string') from None
        return data[start:end].decode('utf-8')
    needed, soname = [], None
    strva = next((value for tag,value in entries if tag == 5), None)
    if strva is not None:
        stroff = next((p['offset']+strva-p['address'] for p in loads
                       if p['address'] <= strva < p['address']+p['size']), None)
        if stroff is None:
            raise ValueError('ELF dynamic string table outside LOAD segments')
        needed = [cstring(stroff+v) for t,v in entries if t == 1]
        soname = next((cstring(stroff+v) for t,v in entries if t == 14), None)
    sections = [read('<IIQQQQIIQQ', shoff+i*shsize) for i in range(shcount)]
    imports, exports = set(), set()
    for section in sections:
        if section[1] != 11:  # SHT_DYNSYM
            continue
        off, size, link, entry_size = section[4],section[5],section[6],section[9]
        if link >= len(sections) or entry_size < 24:
            raise ValueError('Invalid ELF symbol table')
        strings = sections[link][4]
        for pos in range(off, off+size, entry_size):
            name, info, other, index, value, size = read('<IBBHQQ', pos)
            if name and info >> 4 in (1, 2):
                symbol = cstring(strings+name)
                (imports if index == 0 else exports).add(symbol)
    return {'machine':machine,'needed':needed,'soname':soname,'loads':loads,
            'aligned_16k':bool(loads) and all(p['alignment'] >= 16384 and p['congruent_16k'] for p in loads),
            'imports':sorted(imports),'exports':sorted(exports)}


def modules_in_zip(path):
    """Include Chaquopy .imy containers as well as APK lib/ and wheel modules."""
    with zipfile.ZipFile(path) as archive:
        if archive.testzip():
            raise ValueError('ZIP CRC failure')
        for name in archive.namelist():
            if name.endswith('.so'):
                yield name, archive.read(name)
            elif name.endswith('.imy'):
                for inner, data in modules_in_zip(io.BytesIO(archive.read(name))):
                    yield name+'/'+inner, data


def native_wheel(output, package, version, abi, library_name, binary, notices):
    """A py3-none Android wheel holding an actual new-version shared library."""
    info = elf_info(binary)
    if not info['aligned_16k'] or info['machine'] != (183 if abi == 'arm64_v8a' else 62):
        raise ValueError('Native library fails ABI/16KB gate')
    tag = f'py3-none-android_26_{abi}'
    dist = f'{package}-{version}.dist-info'
    entries = {
        f'chaquopy/lib/{library_name}':binary,
        f'{dist}/METADATA':f'Metadata-Version: 2.1\nName: {package.replace("_", "-")}\nVersion: {version}\nSummary: Fuorigiri Android native dependency, source-built and pending runtime qualification\n'.encode(),
        f'{dist}/WHEEL':f'Wheel-Version: 1.0\nGenerator: Fuorigiri native builder\nRoot-Is-Purelib: false\nTag: {tag}\n'.encode(),
    }
    for name, contents in notices.items():
        if Path(name).name != name:
            raise ValueError('Invalid license filename')
        entries[f'{dist}/licenses/{name}'] = contents
    record = io.StringIO(newline='')
    writer = csv.writer(record, lineterminator='\n')
    for name,data in sorted(entries.items()):
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode()
        writer.writerow([name,'sha256='+digest,len(data)])
    writer.writerow([f'{dist}/RECORD','',''])
    entries[f'{dist}/RECORD'] = record.getvalue().encode()
    target = output / f'{package}-{version}-{tag}.whl'
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as archive:
        for name,data in sorted(entries.items()):
            archive.writestr(name,data)
    return target
