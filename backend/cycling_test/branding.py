"""Product branding is immutable configuration shipped with the application."""
from pathlib import Path
import sys

ATTRIBUTION = 'Sviluppato da Luca Bontempi per Progetto CIclismo - Rodengo Saiano A.S.D.'
MOBILE_ASSETS = None


def icon_path():
    base=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parents[2]))
    built=base/'frontend/dist/branding/fuorigiri-256.png'
    return built if built.exists() else base/'frontend/public/branding/fuorigiri-256.png'


def logo_path():
    if MOBILE_ASSETS is not None:return MOBILE_ASSETS/'branding'/'progetto-ciclismo.png'
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[2]))
    path = base/'frontend'/'dist'/'branding'/'progetto-ciclismo.png'
    return path if path.exists() else base/'frontend'/'public'/'branding'/'progetto-ciclismo.png'
