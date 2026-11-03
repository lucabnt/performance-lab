import base64
import csv
import hashlib
import io
import struct
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from android_native_tools import elf_info, modules_in_zip, native_wheel


def elf(machine=62, alignment=16384, address=0):
    data = bytearray(120)
    data[:6] = b'\x7fELF\x02\x01'
    struct.pack_into('<H',data,18,machine)
    struct.pack_into('<QQ',data,32,64,0)
    struct.pack_into('<HHHH',data,54,56,1,64,0)
    struct.pack_into('<IIQQQQQQ',data,64,1,5,0,address,address,120,120,alignment)
    return bytes(data)


def test_elf_alignment_requires_congruence_not_just_flag():
    assert elf_info(elf())['aligned_16k']
    assert not elf_info(elf(address=4096))['aligned_16k']
    assert not elf_info(elf(alignment=4096))['aligned_16k']


@pytest.mark.parametrize('data',[b'not ELF',elf()[:90]])
def test_rejects_invalid_or_truncated_elf(data):
    with pytest.raises(ValueError):
        elf_info(data)


def test_audits_native_objects_in_all_imy_containers(tmp_path):
    inner = io.BytesIO()
    with zipfile.ZipFile(inner,'w') as z:
        z.writestr('_ssl.so',elf())
    apk = tmp_path/'app.apk'
    with zipfile.ZipFile(apk,'w') as z:
        z.writestr('lib/x86_64/libpython.so',elf())
        z.writestr('assets/chaquopy/stdlib-x86_64.imy',inner.getvalue())
        z.writestr('assets/chaquopy/requirements-x86_64.imy',inner.getvalue())
    assert len(list(modules_in_zip(apk))) == 3


def test_native_wheel_has_complete_record_and_preserves_binary(tmp_path):
    binary = elf()
    p = native_wheel(tmp_path,'chaquopy_freetype','2.15.0','x86_64','libfreetype.so',binary,{'LICENSE':b'notice'})
    with zipfile.ZipFile(p) as z:
        assert z.read('chaquopy/lib/libfreetype.so') == binary
        record = next(n for n in z.namelist() if n.endswith('/RECORD'))
        rows = list(csv.reader(io.StringIO(z.read(record).decode())))
        assert {r[0] for r in rows} == set(z.namelist())
        for name,digest,size in rows:
            if digest:
                data = z.read(name)
                expected = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode()
                assert digest == 'sha256='+expected
                assert int(size) == len(data)
    with pytest.raises(FileExistsError):
        native_wheel(tmp_path,'chaquopy_freetype','2.15.0','x86_64','libfreetype.so',binary,{})


@pytest.mark.parametrize('binary',[elf(machine=183),elf(alignment=4096)])
def test_rejects_wrong_abi_or_alignment_before_writing_wheel(tmp_path,binary):
    with pytest.raises(ValueError):
        native_wheel(tmp_path,'package','1.0','x86_64','libtest.so',binary,{})
    assert not list(tmp_path.iterdir())
