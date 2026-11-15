"""Reset must preserve the entire old demo and reject unsafe or open targets."""

import json
import sys
from pathlib import Path

import pytest
from cycling_test.instance import InstanceLock

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
from demo_reset import reset_demo


def test_reset_retains_original_and_does_not_follow_registry(tmp_path):
    base = tmp_path / '.local'
    root = base / 'ui-test'
    root.mkdir(parents=True)
    outside = tmp_path / 'operational'
    outside.mkdir()
    (outside / 'sentinel').write_text('keep')
    (root / 'workspaces.json').write_text(json.dumps([{'path': str(outside)}]))
    (root / 'archive.sqlite').write_bytes(b'old database, not opened by reset')
    (root / 'objects').mkdir()
    (root / 'objects/attachment').write_bytes(b'original')
    backup = reset_demo(root, allowed_root=base)
    assert backup.parent == base / 'demo-backups' and not root.exists()
    assert (backup / 'archive.sqlite').read_bytes() == b'old database, not opened by reset'
    assert (backup / 'objects/attachment').read_bytes() == b'original'
    assert (outside / 'sentinel').read_text() == 'keep'
    root.mkdir()
    (root / 'new').write_text('new')
    second = reset_demo(root, allowed_root=base)
    assert second != backup and (backup / 'objects/attachment').exists()


def test_reset_refuses_roots_nested_paths_files_and_links(tmp_path):
    base = tmp_path / '.local'
    base.mkdir()
    for path in (base, tmp_path, tmp_path / 'outside', base / 'demo-backups', base / 'workspaces' / 'athlete'):
        with pytest.raises(ValueError):
            reset_demo(path, allowed_root=base)
    file = base / 'file'
    file.write_text('keep')
    with pytest.raises(ValueError):
        reset_demo(file, allowed_root=base)
    assert file.read_text() == 'keep'
    target = base / 'new-demo'
    assert reset_demo(target, allowed_root=base) is None
    assert not target.exists()


@pytest.mark.parametrize('nested', [False, True])
def test_reset_rejects_running_archive_and_releases_own_locks(tmp_path, nested):
    base = tmp_path / '.local'
    root = base / 'ui-test'
    root.mkdir(parents=True)
    child = root / 'repliche/admin' if nested else root
    child.mkdir(parents=True, exist_ok=True)
    lock = InstanceLock(child)
    try:
        with pytest.raises(ValueError, match='già aperto'):
            reset_demo(root, allowed_root=base)
        assert root.exists() and not (base / 'demo-backups').exists()
    finally:
        lock.close()
    assert reset_demo(root, allowed_root=base).exists()


def test_reset_refuses_symlink_without_touching_destination(tmp_path):
    base = tmp_path / '.local'
    root = base / 'demo'
    root.mkdir(parents=True)
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'original').write_text('keep')
    try:
        (root / 'linked').symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip('Symlink non disponibili per questo account Windows.')
    with pytest.raises(ValueError, match='collegamenti'):
        reset_demo(root, allowed_root=base)
    assert (outside / 'original').read_text() == 'keep' and root.exists()


def test_reset_retries_transient_windows_directory_handle(tmp_path, monkeypatch):
    import demo_reset

    base = tmp_path / '.local'
    root = base / 'demo'
    root.mkdir(parents=True)
    (root / 'original').write_text('keep')
    original = Path.rename
    attempts = []

    def rename(path, destination):
        attempts.append(destination)
        if len(attempts) == 1:
            raise PermissionError('Transient indexer handle')
        return original(path, destination)

    monkeypatch.setattr(Path, 'rename', rename)
    monkeypatch.setattr(demo_reset.time, 'sleep', lambda _: None)
    backup = reset_demo(root, allowed_root=base)
    assert len(attempts) == 2 and attempts[0] == attempts[1]
    assert (backup / 'original').read_text() == 'keep' and not root.exists()
