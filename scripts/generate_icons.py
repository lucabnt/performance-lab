"""Deterministic icon exports from the maintained vector. No image service."""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PIL import Image

root = Path(__file__).resolve().parents[1]
assets = root / 'frontend/public/branding'
renderer = QSvgRenderer(str(assets / 'fuorigiri.svg'))
for size in (32, 48, 64, 128, 192, 256, 512):
    canvas = QImage(size, size, QImage.Format.Format_ARGB32)
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    renderer.render(painter)
    painter.end()
    canvas.save(str(assets / f'fuorigiri-{size}.png'))
Image.open(assets / 'fuorigiri-256.png').save(
    assets / 'fuorigiri.ico', sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)]
)
