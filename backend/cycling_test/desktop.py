import argparse
import os
import secrets
import socket
import sys
import threading
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
        from .reports import report
        from .fit import decode_fit
        from PySide6.QtWebEngineWidgets import QWebEngineView
        (root/'smoke-ok.txt').write_text('Ciclo Test 0.1.0: import e risorse disponibili.',encoding='utf-8')
        return
    sock = socket.socket()
    sock.bind(("127.0.0.1",args.port))
    port = sock.getsockname()[1]
    config = uvicorn.Config(app,host="127.0.0.1",port=port,log_level="warning")
    server = uvicorn.Server(config)
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
    thread = threading.Thread(target=lambda:server.run(sockets=[sock]),daemon=True)
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
    timer.timeout.connect(ready)
    timer.start(100)
    qt.exec()
    server.should_exit = True
    thread.join(timeout=5)
    sock.close()


if __name__ == "__main__":
    main()
