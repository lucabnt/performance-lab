"""Verify the vendored shared UI without requiring a sibling repository."""
import base64
import hashlib
import io
import json
import tarfile
from pathlib import Path


def verify(root):
    vendor=root/'frontend/vendor'
    metadata=json.loads((vendor/'suite-ui-provenance.json').read_text(encoding='utf-8'))
    filename=metadata['artifact']
    if Path(filename).name!=filename or not filename.endswith('.tgz'):
        raise ValueError('Nome artefatto UI non valido.')
    raw=(vendor/filename).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=metadata['sha256']:
        raise ValueError('Checksum UI diverso dalla provenienza registrata.')
    expected='file:vendor/'+filename
    package=json.loads((root/'frontend/package.json').read_text(encoding='utf-8'))
    lock=json.loads((root/'frontend/package-lock.json').read_text(encoding='utf-8'))
    name=metadata['package'];version=metadata['version']
    if package['dependencies'].get(name)!=expected:
        raise ValueError('Dipendenza UI diversa dall’artefatto registrato.')
    locked=lock['packages']['node_modules/'+name]
    sri='sha512-'+base64.b64encode(hashlib.sha512(raw).digest()).decode()
    if (locked['version'],locked['resolved'],locked['integrity'])!=(version,expected,sri):
        raise ValueError('Lockfile UI non coerente: ripetere installazione e verifica.')
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
        entries=set(archive.getnames())
        required={'package/src/Dialog.tsx', 'package/src/time.tsx', 'package/dist/application.css', 'package/dist/Dialog.js', 'package/package.json','package/LICENSE','package/NOTICE.md',
                  'package/src/index.ts','package/src/branding.tsx',
                  'package/scripts/copy-assets.mjs','package/tsconfig.json',
                  'package/dist/index.js','package/dist/index.d.ts',
                  'package/dist/theme.css','package/dist/components.css'}
        if not required<=entries:raise ValueError('Pacchetto UI incompleto: sorgenti o risorse mancanti.')
        info=json.load(archive.extractfile('package/package.json'))
        if (info['name'],info['version'],info['license'])!=(name,version,'GPL-3.0-or-later'):
            raise ValueError('Identità del pacchetto UI incoerente.')
        logo=archive.extractfile('package/dist/assets/progetto-ciclismo.png').read()
        if logo!=(root/'frontend/public/branding/progetto-ciclismo.png').read_bytes():
            raise ValueError('Il logo UI condiviso non coincide con l’originale societario.')
    print(f'UI condivisa verificata: {name} {version}, sorgenti/licenza/logo e lockfile coerenti.')


if __name__=='__main__':
    verify(Path(__file__).resolve().parents[1])
