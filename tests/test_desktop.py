import sys
import pytest


def test_smoke_starts_http_without_console(tmp_path,monkeypatch):
    pytest.importorskip('PySide6.QtWebEngineWidgets')
    from cycling_test.desktop import main
    monkeypatch.setattr(sys,'argv',['fuorigiri','--smoke-test','--data',str(tmp_path)])
    with monkeypatch.context() as context:
        context.setattr(sys,'stdout',None)
        context.setattr(sys,'stderr',None)
        main()
    assert 'backend HTTP verificati' in (tmp_path/'smoke-ok.txt').read_text()
