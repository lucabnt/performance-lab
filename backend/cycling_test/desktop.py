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
    parser = argparse.ArgumentParser(description="Ciclo Test")
    parser.add_argument("--data",type=Path)
    parser.add_argument("--browser",action="store_true",help="Apri il browser di sistema al posto della finestra Qt")
    parser.add_argument("--port",type=int,default=0)
    parser.add_argument("--smoke-test",action="store_true",help="Verifica le dipendenze del pacchetto senza aprire finestre")
    args = parser.parse_args()
    base = Path(os.environ.get("LOCALAPPDATA", Path.home()/".local"/"share"))
    root = args.data or base/"CicloTest"
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
        if not logo_path().read_bytes().startswith(b'\x89PNG'):
            raise SystemExit('Logo del prodotto mancante nel bundle.')
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
            (root/'smoke-ok.txt').write_text('Ciclo Test 0.2.0: import, logo e backend HTTP verificati.',encoding='utf-8')
        finally:
            server.should_exit=True;thread.join(timeout=5);sock.close();handler.close();logger.removeHandler(handler)
        return
    url = f"http://127.0.0.1:{port}/#token={token}"
    if args.browser:
        import webbrowser
        threading.Timer(1,lambda:webbrowser.open(url)).start()
        server.run(sockets=[sock])
        return
    from PySide6.QtCore import QUrl, QTimer
    from PySide6.QtWidgets import QApplication
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEnginePage
    thread = threading.Thread(target=serve,daemon=True)
    thread.start()
    qt = QApplication(sys.argv[:1])
    class LocalPage(QWebEnginePage):
        def acceptNavigationRequest(self,url,type,is_main):
            if url.scheme() in ('http','https') and url.host() != '127.0.0.1':
                from PySide6.QtGui import QDesktopServices
                QDesktopServices.openUrl(url)
                return False
            return url.scheme() in ("blob", "data") or (url.host() == "127.0.0.1" and url.port() == port)
    view = QWebEngineView()
    view.setPage(LocalPage(view))
    def external_window(request):
        from PySide6.QtGui import QDesktopServices
        url=request.requestedUrl()
        if url.scheme() in ('http','https') and url.host()!='127.0.0.1':
            QDesktopServices.openUrl(url)
    view.page().newWindowRequested.connect(external_window)
    view.setWindowTitle("Ciclo Test")
    view.resize(1440,960)
    from PySide6.QtWidgets import QFileDialog
    def save_download(item):
        filename,_ = QFileDialog.getSaveFileName(view,"Salva",item.downloadFileName())
        if filename:
            item.setDownloadDirectory(str(Path(filename).parent))
            item.setDownloadFileName(Path(filename).name)
            item.accept()
        else:
            item.cancel()
    view.page().profile().downloadRequested.connect(save_download)
    timer = QTimer()
    def ready():
        if server.started:
            timer.stop()
            view.load(QUrl(url))
            view.show()
        elif failed.is_set() or not thread.is_alive():
            timer.stop()
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(view,'Avvio non riuscito',f'Consultare il file {root / "server.log"}')
            qt.quit()
    timer.timeout.connect(ready)
    timer.start(100)
    qt.exec()
    server.should_exit = True
    thread.join(timeout=5)
    sock.close()
    handler.close();logger.removeHandler(handler)


if __name__ == "__main__":
    main()
