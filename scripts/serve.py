"""Headless local server for GUI verification and Vite development."""
import argparse
import secrets
from pathlib import Path
import uvicorn
from cycling_test.api import create_app
from cycling_test.instance import InstanceLock


def main():
    parser=argparse.ArgumentParser(description='Server locale di test per la GUI Fuorigiri')
    parser.add_argument('--data',type=Path,default=Path('.local/ui-test'))
    parser.add_argument('--port',type=int,default=8766)
    args=parser.parse_args()
    try:instance=InstanceLock(args.data)
    except ValueError as exc:raise SystemExit(str(exc)) from None
    token=secrets.token_urlsafe(32)
    print(f'GUI compilata: http://127.0.0.1:{args.port}/#token={token}',flush=True)
    print(f'Vite sviluppo: http://127.0.0.1:5173/#token={token}',flush=True)
    print(f'Archivio di test: {args.data.resolve()}',flush=True)
    print('Aprire uno degli URL completi sopra. Ctrl+C per arrestare il server.',flush=True)
    try:uvicorn.run(create_app(args.data,token),host='127.0.0.1',port=args.port,log_level='warning')
    finally:instance.close()


if __name__=='__main__':main()
