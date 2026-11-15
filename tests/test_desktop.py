import sys
import pytest


def test_smoke_starts_http_without_console(tmp_path, monkeypatch):
    pytest.importorskip('PySide6.QtWebEngineWidgets')
    from cycling_test.desktop import main

    monkeypatch.setattr(sys, 'argv', ['fuorigiri', '--smoke-test', '--data', str(tmp_path)])
    with monkeypatch.context() as context:
        context.setattr(sys, 'stdout', None)
        context.setattr(sys, 'stderr', None)
        main()
    assert 'backend HTTP verificati' in (tmp_path / 'smoke-ok.txt').read_text()


def test_archive_lock_released_without_removing_file(tmp_path):
    from cycling_test.instance import InstanceLock

    first = InstanceLock(tmp_path)
    with pytest.raises(ValueError, match='già aperto'):
        InstanceLock(tmp_path)
    first.close()
    second = InstanceLock(tmp_path)
    second.close()
    assert (tmp_path / 'fuorigiri-instance.lock').exists()
