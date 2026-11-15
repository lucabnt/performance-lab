"""Create source archive + checksums; never sign, publish or upload automatically."""

import hashlib
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from package_candidate import write_source_archive
from verify_versions import verify

root = Path(__file__).resolve().parents[1]
version = verify(root)
release = root / 'dist/release'
release.mkdir(parents=True, exist_ok=True)
sources = release / f'Fuorigiri-{version}-sources.zip'
# Finish the snapshot before replacing the developer's previous staging file.
with TemporaryDirectory(dir=release) as staging:
    candidate = Path(staging) / sources.name
    write_source_archive(root, candidate, f'Fuorigiri-{version}')
    candidate.replace(sources)
files = {
    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(release.iterdir())
    if p.name.startswith(f'Fuorigiri-{version}-') and p.is_file() and p.suffix in ('.exe', '.zip', '.flatpak', '.apk')
}
(release / 'SHA256SUMS.txt').write_text(
    ''.join(f'{digest}  {name}\n' for name, digest in files.items()), encoding='utf-8'
)
(release / 'release.json').write_text(
    json.dumps(
        {
            'product': 'Fuorigiri Performance Lab',
            'version': version,
            'files': files,
            'signed': False,
            'source_archive': sources.name,
            'source_snapshot': 'working_tree',
            'git_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
            'working_tree_dirty': bool(
                subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip()
            ),
        },
        indent=2,
    )
    + '\n',
    encoding='utf-8',
)
print(f'Preparati sorgenti e checksum in {release}. Nessun caricamento eseguito.')
