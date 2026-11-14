"""Build on the target OS. Run npm ci && npm run build in frontend first."""
import os
import argparse
import json
import shutil
from importlib.metadata import distributions
import subprocess
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Build desktop Fuorigiri con dipendenze incluse')
parser.add_argument('--output-root',type=Path,help='Nuova directory isolata per bundle/work/spec; rifiuta destinazioni esistenti')
args=parser.parse_args()
bundle=root/'dist/Fuorigiri'
extra=[]
if args.output_root:
    output=args.output_root.resolve()
    output.mkdir(parents=True,exist_ok=False)
    (output/'work').mkdir()
    bundle=output/'bundle/Fuorigiri'
    extra=['--distpath',str(output/'bundle'),'--workpath',str(output/'work'),'--specpath',str(output/'work')]

from verify_versions import verify
verify(root)
subprocess.run([sys.executable,str(root/'scripts/verify_suite_ui.py')],check=True)
subprocess.run([sys.executable,str(root/'scripts/verify_core.py')],check=True)
if not (root/'frontend/dist/index.html').exists():
    raise SystemExit('Compilare prima frontend: npm ci && npm run build')
# Qt/Chromium notices are version-specific: refuse a bundle whose runtime differs.
qt_notices=root/'packaging/licenses/qt'
expected=json.loads((qt_notices/'PROVENIENZA.json').read_text(encoding='utf-8'))['runtime']
probe=('import json,PySide6;from PySide6 import QtCore,QtWebEngineCore as w;'
       'print(json.dumps({"pyside6":PySide6.__version__,"qt":QtCore.qVersion(),'
       '"qtwebengine":w.qWebEngineVersion(),"chromium":w.qWebEngineChromiumVersion()}))')
found=json.loads(subprocess.check_output([sys.executable,'-c',probe],text=True))
mismatch={k:(v,expected[k]) for k,v in found.items() if expected.get(k)!=v}
if mismatch:
    raise SystemExit('Avvisi Qt/Chromium non aggiornati per il runtime installato (trovato, atteso): '+repr(mismatch)
                     +'. Rigenerare packaging/licenses/qt con scripts/collect_qtwebengine_notices.py.')
command=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--name','Fuorigiri',
         '--paths',str(root/'backend'),'--add-data',f'{root / "frontend/dist"}{os.pathsep}frontend/dist',
         '--collect-data','matplotlib','--collect-data','reportlab',
         '--collect-all','keyring',
         '--hidden-import','uvicorn.logging','--hidden-import','uvicorn.loops.auto',
         '--hidden-import','uvicorn.loops.asyncio','--hidden-import','uvicorn.protocols.http.h11_impl',
         '--hidden-import','uvicorn.protocols.http.auto','--hidden-import','uvicorn.protocols.websockets.auto',
         '--hidden-import','uvicorn.lifespan.on']
if sys.platform=='win32':command.extend(['--windowed','--icon',str(root/'frontend/public/branding/fuorigiri.ico')])
command.extend(extra)
command.append(str(root/'desktop_entry.py'))
env=os.environ.copy()
if sys.platform=='win32':
    # Build-time DLL discovery must not resolve Windows ICU against unrelated
    # tools (for example Poppler's different, versioned icuuc.dll on PATH).
    windows=Path(env.get('SystemRoot',r'C:\Windows'))
    env['PATH']=os.pathsep.join([str(Path(sys.executable).parent),sys.base_prefix,
                                str(windows/'System32'),str(windows),str(windows/'System32/Wbem')])
subprocess.run(command,cwd=root,check=True,env=env)
for name in ('LICENSE','README.md','THIRD_PARTY.md','ARCHITETTURA_PROPOSTA.md','CHANGELOG.md'):
    shutil.copy2(root/name,bundle/name)
# Only reviewed repository files belong in the end-user bundle.
manifest = root / 'bundle-resources.json'
if manifest.is_file() and not (root / '.git').exists():
    names = json.loads(manifest.read_text(encoding='utf-8'))
else:
    names = subprocess.check_output(
        ['git', 'ls-files', '-z', '--', 'docs', 'examples'], cwd=root
    ).decode('utf-8').split('\0')
for name in filter(None, names):
    source = root / name
    allowed = any(source.resolve().is_relative_to(root / folder) for folder in ('docs', 'examples'))
    if not allowed or Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError('Percorso risorsa non valido: ' + name)
    if source.is_file():
        target = bundle / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

# Retain original notices available in the builder's installed distributions.
# Some binary components need additional upstream sources and notices (THIRD_PARTY.md).
notices = bundle / 'licenses'
for dist in distributions():
    for entry in dist.files or ():
        parts = entry.parts
        if not parts or not parts[0].endswith('.dist-info') or len(parts) < 2:
            continue
        if parts[1] != 'licenses' and not entry.name.upper().startswith(('LICENSE', 'COPYING', 'NOTICE')):
            continue
        if '..' in parts or entry.is_absolute():
            raise ValueError('Percorso di licenza non valido.')
        source = Path(dist.locate_file(entry))
        if source.is_file():
            target = notices / 'python' / entry
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

for source in sorted(qt_notices.iterdir()):
    if source.is_file():
        target = notices / 'qt' / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

for package in ('react', 'react-dom', 'scheduler', 'lucide-react', 'plotly.js-dist-min', '@cycling-suite/ui'):
    directory = root / 'frontend/node_modules' / package
    for source in [directory / 'LICENSE', *directory.glob('NOTICE*')]:
        if source.is_file():
            target = notices / 'frontend' / package / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
