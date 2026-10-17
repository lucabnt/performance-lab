"""No plaintext fallback. Android installs its Keystore adapter at bootstrap."""
import hashlib
from pathlib import Path

_mobile = None


def account(root):return hashlib.sha256(str(Path(root).resolve()).encode()).hexdigest()


def backend():
    if _mobile is not None:return _mobile
    import sys
    if sys.platform=='win32':
        from keyring.backends.Windows import WinVaultKeyring
        return WinVaultKeyring()
    from keyring.backends.SecretService import Keyring
    return Keyring()


def save(root,password):
    try:backend().set_password('Fuorigiri.WebDAV',account(root),password)
    except Exception:raise ValueError('Portachiavi di sistema non disponibile o bloccato. Nessuna password salvata; sbloccare il portachiavi e riprovare.') from None


def read(root):
    try:value=backend().get_password('Fuorigiri.WebDAV',account(root))
    except Exception:raise ValueError('Impossibile aprire il portachiavi di sistema.') from None
    if not value:raise ValueError('Password WebDAV non presente: riconfigurare la connessione.')
    return value
