"""Source integrity and non-destructive behavior of the experimental builder."""
import hashlib
import importlib.util
import io
import sys
import tarfile
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location('pillow_builder', Path(__file__).resolve().parents[1] / 'scripts/build_android_pillow.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def archive_at(path, name):
    with tarfile.open(path, 'w:gz') as archive:
        item = tarfile.TarInfo(name)
        item.size = 3
        archive.addfile(item, io.BytesIO(b'abc'))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_source_digest_before_extraction(tmp_path):
    archive = tmp_path / 'source.tar.gz'
    archive_at(archive, 'source/file.txt')
    with pytest.raises(ValueError, match='checksum'):
        builder.unpack(archive, tmp_path / 'extracted', '0' * 64)
    assert not (tmp_path / 'extracted').exists()


def test_source_cannot_escape_destination(tmp_path):
    archive = tmp_path / 'source.tar.gz'
    digest = archive_at(archive, '../escaped.txt')
    with pytest.raises(tarfile.FilterError):
        builder.unpack(archive, tmp_path / 'extracted', digest)
    assert not (tmp_path / 'escaped.txt').exists()


def test_valid_source_unpack(tmp_path):
    archive = tmp_path / 'source.tar.gz'
    digest = archive_at(archive, 'source/file.txt')
    root = builder.unpack(archive, tmp_path / 'extracted', digest)
    assert (root / 'file.txt').read_bytes() == b'abc'


def test_existing_build_preserved(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'linux')
    output = tmp_path / 'old-build'
    output.mkdir()
    sentinel = output / 'keep'
    sentinel.write_bytes(b'previous candidate')
    with pytest.raises(SystemExit, match='already exists'):
        builder.build(tmp_path / 'kit', output, 'x86_64')
    assert sentinel.read_bytes() == b'previous candidate'
