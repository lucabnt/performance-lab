import argparse
import os
import secrets
import socket
import sys
import threading
import logging
import time
from pathlib import Path

import uvicorn
from .api import create_app


def main():
    parser = argparse.ArgumentParser(description="Fuorigiri Performance Lab")
    parser.add_argument("--data",type=Path)
    parser.add_argument("--browser",action="store_true",help="Apri il browser di sistema al posto della finestra Qt")
    parser.add_argument("--port",type=int,default=0)
    parser.add_argument("--smoke-test",action="store_true",help="Verifica le dipendenze del pacchetto senza aprire finestre")
    args = parser.parse_args()
    base = Path(os.environ.get("LOCALAPPDATA" if sys.platform=='win32' else 'XDG_DATA_HOME', Path.home()/".local"/"share"))
    from .compatibility import default_data_root
    root = args.data or default_data_root(base)
    from .instance import InstanceLock
    try:instance=InstanceLock(root)
    except ValueError as exc:
        if args.smoke_test or args.browser:raise SystemExit(str(exc)) from None
        from PySide6.QtWidgets import QApplication,QMessageBox
        qt=QApplication(sys.argv[:1]);QMessageBox.information(None,'Fuorigiri già aperto',str(exc))
        return
    token = secrets.token_urlsafe(32)
    dist = Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parents[2]))/"frontend"/"dist"
    if not dist.is_dir():
        raise SystemExit("Interfaccia non compilata. Eseguire npm run build nella cartella frontend.")
    app = create_app(root,token,dist)
    if args.smoke_test:
        (root/'smoke-ok.txt').unlink(missing_ok=True)
        from .reports import report
        from .fit import decode_fit
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from .branding import logo_path
        from .branding import icon_path
        from .credentials import backend as credential_backend
        credential_backend()
        if not logo_path().read_bytes().startswith(b'\x89PNG'):
            raise SystemExit('Logo del prodotto mancante nel bundle.')
        if not icon_path().read_bytes().startswith(b'\x89PNG'):
            raise SystemExit('Icona Fuorigiri mancante nel bundle.')
    sock = socket.socket()
    sock.bind(("127.0.0.1",args.port))
    port = sock.getsockname()[1]
    # Windowed executables have no stdout/stderr. Keep diagnostics in a local
    # file and use explicit built-in protocols for predictable frozen imports.
    handler=logging.FileHandler(root/'server.log',encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger=logging.getLogger('uvicorn');logger.addHandler(handler)
    config = uvicorn.Config(app,host="127.0.0.1",port=port,log_level="warning",log_config=None,
                            access_log=False,loop='asyncio',http='h11',ws='none')
    server = uvicorn.Server(config)
    failed=threading.Event()
    def serve():
        try:server.run(sockets=[sock])
        except BaseException:
            logger.exception('Avvio backend non riuscito');failed.set()
    if args.smoke_test:
        from urllib.request import urlopen
        thread=threading.Thread(target=serve,daemon=True);thread.start()
        deadline=time.monotonic()+15
        try:
            while not server.started:
                if failed.is_set() or not thread.is_alive() or time.monotonic()>deadline:
                    raise RuntimeError('Backend non avviato: consultare server.log.')
                time.sleep(.05)
            with urlopen(f'http://127.0.0.1:{port}/health',timeout=5) as response:
                if response.status!=200:raise RuntimeError('Health check non riuscito.')
            (root/'smoke-ok.txt').write_text('Fuorigiri Performance Lab '+__import__('cycling_test').__version__+': import, logo e backend HTTP verificati.',encoding='utf-8')
        finally:
            server.should_exit=True;thread.join(timeout=5);sock.close();handler.close();logger.removeHandler(handler);instance.close()
        return
    url = f"http://127.0.0.1:{port}/#token={token}"
    if args.browser:
        import webbrowser
        threading.Timer(1,lambda:webbrowser.open(url)).start()
        try:server.run(sockets=[sock])
        finally:instance.close()
        return
    from cycling_suite.desktop import run_window
    from .branding import icon_path
    thread=threading.Thread(target=serve,daemon=True);thread.start()
    run_window(url,'Fuorigiri Performance Lab',icon_path(),port,
               lambda:server.started,lambda:failed.is_set() or not thread.is_alive(),
               'Fuorigiri.PerformanceLab')
    server.should_exit = True
    thread.join(timeout=5)
    sock.close()
    handler.close();logger.removeHandler(handler)
    instance.close()


if __name__ == "__main__":
    main()
