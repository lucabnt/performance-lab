"""Discover previous archives and channels without moving data or changing keys.

The split spelling describes a retired brand, solely for on-disk compatibility.
All current product identifiers use Fuorigiri.
"""

from pathlib import Path

LEGACY_BRAND_PARTS = ('Ciclo', 'Test')


def default_data_root(base: Path) -> Path:
    current = base / 'Fuorigiri'
    previous = base / ''.join(LEGACY_BRAND_PARTS)
    # Registry entries contain absolute paths: renaming their parent would
    # orphan archives. Reuse the original location when upgrading in place.
    return current if current.exists() or not previous.exists() else previous


def channel_directory(folder: Path, channel: str) -> Path:
    previous = folder / ('-'.join(p.lower() for p in LEGACY_BRAND_PARTS) + '-' + channel)
    current = folder / ('fuorigiri-' + channel)
    if previous.exists() and current.exists():
        raise ValueError('Due cartelle di scambio per la stessa chiave: riconciliare i canali prima di continuare.')
    return previous if previous.exists() else current
