"""Build on the target OS. Run npm ci && npm run build in frontend first."""
import os
import subprocess
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
if not (root/'frontend/dist/index.html').exists():
    raise SystemExit('Compilare prima frontend: npm ci && npm run build')
command=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--name','CicloTest',
         '--paths',str(root/'backend'),'--add-data',f'{root / "frontend/dist"}{os.pathsep}frontend/dist',
         '--collect-data','matplotlib','--collect-data','reportlab',
         '--hidden-import','uvicorn.logging','--hidden-import','uvicorn.loops.auto',
         '--hidden-import','uvicorn.protocols.http.auto','--hidden-import','uvicorn.protocols.websockets.auto',
         '--hidden-import','uvicorn.lifespan.on']
if sys.platform=='win32':command.append('--windowed')
command.append(str(root/'desktop_entry.py'))
subprocess.run(command,cwd=root,check=True)
import shutil
for name in ('LICENSE','README.md','THIRD_PARTY.md'):
    shutil.copy2(root/name,root/'dist/CicloTest'/name)
