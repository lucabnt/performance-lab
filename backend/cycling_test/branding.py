"""Product branding is immutable configuration shipped with the application."""
from pathlib import Path
import sys

ATTRIBUTION = 'Sviluppato da Luca Bontempi per Progetto CIclismo - Rodengo Saiano A.S.D.'


def logo_path():
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[2]))
    path = base/'frontend'/'dist'/'branding'/'progetto-ciclismo.png'
    return path if path.exists() else base/'frontend'/'public'/'branding'/'progetto-ciclismo.png'
