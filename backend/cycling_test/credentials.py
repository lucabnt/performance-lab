"""Preserve existing vault names and the Android adapter."""

from cycling_suite.credentials import account, backend as system_backend, Secrets

_mobile = None


def backend():
    return _mobile if _mobile is not None else system_backend()


def save(root, password):
    Secrets('Fuorigiri.WebDAV', backend).save(account(root), password)


def read(root):
    value = Secrets('Fuorigiri.WebDAV', backend).read(account(root))
    if not value:
        raise ValueError('Password WebDAV non presente: riconfigurare la connessione.')
    return value
