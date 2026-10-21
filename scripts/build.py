"""Build on the target OS. Run npm ci && npm run build in frontend first."""
import os
import argparse
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
import shutil
for name in ('LICENSE','README.md','THIRD_PARTY.md','ARCHITETTURA_PROPOSTA.md','CHANGELOG.md'):
    shutil.copy2(root/name,bundle/name)
shutil.copytree(root/'docs',bundle/'docs',dirs_exist_ok=True)
shutil.copytree(root/'examples',bundle/'examples',dirs_exist_ok=True)
