"""Build on the target OS. Run npm ci && npm run build in frontend first."""
import os
import subprocess
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
if not (root/'frontend/dist/index.html').exists():
    raise SystemExit('Compilare prima frontend: npm ci && npm run build')
command=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--name','Fuorigiri',
         '--paths',str(root/'backend'),'--add-data',f'{root / "frontend/dist"}{os.pathsep}frontend/dist',
         '--collect-data','matplotlib','--collect-data','reportlab',
         '--hidden-import','uvicorn.logging','--hidden-import','uvicorn.loops.auto',
         '--hidden-import','uvicorn.loops.asyncio','--hidden-import','uvicorn.protocols.http.h11_impl',
         '--hidden-import','uvicorn.protocols.http.auto','--hidden-import','uvicorn.protocols.websockets.auto',
         '--hidden-import','uvicorn.lifespan.on']
if sys.platform=='win32':command.append('--windowed')
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
    shutil.copy2(root/name,root/'dist/Fuorigiri'/name)
(root/'dist/Fuorigiri/docs').mkdir(exist_ok=True)
for path in (root/'docs').glob('*.md'):
    shutil.copy2(path,root/'dist/Fuorigiri/docs'/path.name)
shutil.copytree(root/'examples',root/'dist/Fuorigiri/examples',dirs_exist_ok=True)
