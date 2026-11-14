"""Find Fuorigiri builder paths in wheels, APKs, bundles and nested archives.

Release gate for PUB-ALPHA-01: distributed binaries, SBOMs and metadata must not
carry our builders' home directories or the developer checkout. ZIP members are
read recursively (APK -> Chaquopy .imy -> files). Output never prints account
names. Upstream wheels may keep historical paths of their own builders: they are
outside this gate. A clean result covers only the listed patterns.
"""
import argparse
import io
import re
import sys
import zipfile
from pathlib import Path

# Fedora Atomic/Kinoite homes identify our own Toolbox builder.
KINOITE = re.compile(rb'/var/home/([A-Za-z0-9._-]+)')
ARCHIVES = ('.zip', '.whl', '.apk', '.imy', '.jar', '.aar')
LIMIT = 64 * 1024 * 1024
SLASH = rb'[\\/]{1,2}'
# Strict mode, for wheels built by the project: any home directory is a finding.
STRICT = [rb'/(?:var/)?home/[A-Za-z0-9._-]+', rb'/Users/[A-Za-z0-9._-]+', rb'/root/',
          rb'[A-Za-z]:' + SLASH + rb'Users' + SLASH + rb'[A-Za-z0-9._ -]+']


def patterns(accounts, extra, strict=False):
    items = list(STRICT) if strict else [rb'/var/home/[A-Za-z0-9._-]+']
    for name in sorted(accounts):
        account = re.escape(name.encode('utf-8'))
        items.append(rb'/home/' + account + rb'\b')
        items.append(SLASH + rb'Users' + SLASH + account + rb'\b')
    for text in extra:
        for variant in {text, text.replace('\\', '/'), text.replace('/', '\\')}:
            items.append(re.escape(variant.encode('utf-8')))
    return re.compile(b'|'.join(items), re.I)


def members(data, label, depth=0):
    """Yield (label, bytes) for a file and, recursively, its ZIP members."""
    if depth < 4 and data[:4] == b'PK\x03\x04':
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                for info in archive.infolist():
                    if not info.is_dir() and info.file_size <= LIMIT:
                        yield from members(archive.read(info), f'{label}!{info.filename}', depth + 1)
            return
        except zipfile.BadZipFile:
            pass
    yield label, data


def redact(value):
    text = value.decode('utf-8', 'replace')
    return re.sub(r'((?:home|Users)[\\/]{1,2})[^\\/]+', r'\1<account>', text, flags=re.I)


def files(paths):
    for path in paths:
        for item in [path] if path.is_file() else sorted(p for p in path.rglob('*') if p.is_file()):
            if item.stat().st_size <= LIMIT or item.suffix.lower() in ARCHIVES:
                yield item


def scan(paths, extra=(), accounts=(), strict=False):
    """Return {member: redacted matches}. Accounts seen under /var/home are also
    searched as /home/<account> and Users/<account> in every scanned member."""
    contents = [m for item in files(paths) for m in members(item.read_bytes(), str(item))]
    known = {a for a in accounts if a} | {Path.home().name}
    for _, data in contents:
        known.update(m.decode('utf-8') for m in KINOITE.findall(data))
    regex, findings = patterns(known, extra, strict), {}
    for label, data in contents:
        for match in regex.finditer(data):
            findings.setdefault(label, set()).add(redact(match.group()))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--forbid', action='append', default=[],
                        help='Additional literal path, e.g. the source checkout used for the build')
    parser.add_argument('--account', action='append', default=[],
                        help='Builder account name to search under home directories (not printed)')
    parser.add_argument('--strict', action='store_true',
                        help='Any home directory is a finding (for wheels built by the project)')
    args = parser.parse_args(argv)
    findings = scan(args.paths, args.forbid, args.account, args.strict)
    for label, values in sorted(findings.items()):
        print(f'{label}: ' + ', '.join(sorted(values)[:5]) + (' …' if len(values) > 5 else ''))
    if findings:
        print(f'{len(findings)} file con percorsi di compilazione da neutralizzare.', file=sys.stderr)
        return 1
    print('Nessun percorso del builder o del checkout trovato nei pattern controllati.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
