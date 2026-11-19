"""Optional password protection for v3 backups (RT-11, format in docs/BACKUP_CIFRATO.md).

The encrypted file wraps an unchanged v3 ZIP64 backup:

    MAGIC | u32 header length | header JSON | chunk*

Each chunk is ``u32 ciphertext length | AES-256-GCM ciphertext`` of at most
CHUNK plaintext bytes. The key comes from scrypt with the parameters stored in
the header. Nonce = 12-byte chunk index; associated data binds every chunk to
the header digest, its index and a final flag, so truncation, reordering,
splicing or header changes are rejected. Files are processed on disk, one chunk
at a time. A lost password cannot be recovered.
"""

import base64
import hashlib
import json
import os
import struct
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

MAGIC = b'FGBAKENC'
FORMAT = 'fuorigiri-backup-encrypted'
VERSION = 1
CHUNK = 1_048_576
SCRYPT_N = 2**17
SCRYPT_R = 8
SCRYPT_P = 1
# Bounds accepted when reading, so a crafted header cannot demand huge memory.
SCRYPT_N_RANGE = (2**14, 2**20)
MIN_PASSWORD = 12
MAX_PASSWORD = 1000
MAX_HEADER = 4096
SUFFIX = '.fgbak'


class WrongPassword(ValueError):
    pass


def check_password(password):
    if not isinstance(password, str) or len(password) < MIN_PASSWORD:
        raise ValueError(f'Usare una password di almeno {MIN_PASSWORD} caratteri per proteggere il backup.')
    if len(password) > MAX_PASSWORD:
        raise ValueError('Password troppo lunga.')


def is_encrypted(path):
    with Path(path).open('rb') as stream:
        return stream.read(len(MAGIC)) == MAGIC


def _key(password, kdf):
    salt = base64.b64decode(kdf['salt'], validate=True)
    return Scrypt(salt=salt, length=32, n=kdf['n'], r=kdf['r'], p=kdf['p']).derive(password.encode('utf-8'))


def _aad(header_digest, index, final):
    return header_digest + struct.pack('>QB', index, 1 if final else 0)


def _nonce(index):
    return index.to_bytes(12, 'big')


def encrypt_file(source, destination, password, *, n=SCRYPT_N):
    """Write a new encrypted file; never replaces an existing destination."""
    check_password(password)
    source, destination = Path(source), Path(destination)
    kdf = {'name': 'scrypt', 'n': n, 'r': SCRYPT_R, 'p': SCRYPT_P, 'salt': base64.b64encode(os.urandom(16)).decode()}
    header = json.dumps(
        {
            'format': FORMAT,
            'version': VERSION,
            'content': 'backup-v3-zip',
            'cipher': 'AES-256-GCM',
            'chunk_size': CHUNK,
            'kdf': kdf,
        },
        sort_keys=True,
        separators=(',', ':'),
    ).encode('utf-8')
    aes = AESGCM(_key(password, kdf))
    digest = hashlib.sha256(header).digest()
    with source.open('rb') as reader:
        # Cleanup only ever removes the file this call created (never a pre-existing one).
        try:
            out = destination.open('xb')
        except FileExistsError:
            raise ValueError('Il file di destinazione esiste già: nessun backup sovrascritto.') from None
        try:
            with out:
                out.write(MAGIC + struct.pack('>I', len(header)) + header)
                index = 0
                while True:
                    plain = reader.read(CHUNK)
                    final = not reader.peek(1)  # an empty source still produces one final chunk
                    sealed = aes.encrypt(_nonce(index), plain, _aad(digest, index, final))
                    out.write(struct.pack('>I', len(sealed)) + sealed)
                    index += 1
                    if final:
                        break
        except BaseException:
            destination.unlink(missing_ok=True)
            raise
    return destination


def write_encrypted_backup(store, destination, password):
    """Desktop save: v3 backup encrypted next to the destination, published without overwriting."""
    import tempfile
    from .backup_stream import write_backup

    check_password(password)
    destination = Path(destination)
    if destination.exists():
        raise ValueError('Il file di destinazione esiste già: nessun backup sovrascritto.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.fuorigiri-backup-', dir=destination.parent) as tmp:
        plain = write_backup(store, Path(tmp) / 'backup.zip')
        sealed = encrypt_file(plain, Path(tmp) / ('backup' + SUFFIX), password)
        plain.unlink()
        if os.name == 'nt':
            sealed.rename(destination)  # fails if the destination appeared meanwhile
        else:
            os.link(sealed, destination)
    return destination


def read_header(stream):
    if stream.read(len(MAGIC)) != MAGIC:
        raise ValueError('File non riconosciuto come backup protetto da password.')
    raw_length = stream.read(4)
    if len(raw_length) != 4:
        raise ValueError('Backup protetto incompleto.')
    (length,) = struct.unpack('>I', raw_length)
    if not 0 < length <= MAX_HEADER:
        raise ValueError('Intestazione del backup protetto non valida.')
    header = stream.read(length)
    if len(header) != length:
        raise ValueError('Backup protetto incompleto.')
    try:
        data = json.loads(header)
        kdf = data['kdf']
        valid = (
            data['format'] == FORMAT
            and data['content'] == 'backup-v3-zip'
            and data['cipher'] == 'AES-256-GCM'
            and data['chunk_size'] == CHUNK
            and kdf['name'] == 'scrypt'
            and type(kdf['n']) is int
            and SCRYPT_N_RANGE[0] <= kdf['n'] <= SCRYPT_N_RANGE[1]
            and kdf['n'] & (kdf['n'] - 1) == 0
            and (kdf['r'], kdf['p']) == (SCRYPT_R, SCRYPT_P)
            and len(base64.b64decode(kdf['salt'], validate=True)) == 16
        )
    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError('Intestazione del backup protetto non valida.') from exc
    if not valid:
        raise ValueError('Intestazione del backup protetto non valida.')
    if data['version'] != VERSION:
        raise ValueError('Backup protetto creato con una versione più recente: aggiornare Fuorigiri.')
    return header, data


def decrypt_file(source, destination, password):
    """Decrypt to a new file; any authentication failure leaves no output behind."""
    if not isinstance(password, str) or not password:
        raise WrongPassword('Backup protetto da password: inserire la password.')
    destination = Path(destination)
    with Path(source).open('rb') as reader:
        header, data = read_header(reader)
        aes = AESGCM(_key(password, data['kdf']))
        digest = hashlib.sha256(header).digest()
        try:
            out = destination.open('xb')
        except FileExistsError:
            raise ValueError('Il file di destinazione esiste già: nessun file sovrascritto.') from None
        try:
            with out:
                _decrypt_chunks(reader, out, aes, digest)
        except BaseException:
            destination.unlink(missing_ok=True)
            raise
    return destination


def _decrypt_chunks(reader, out, aes, digest):
    index = 0
    while True:
        raw_length = reader.read(4)
        if len(raw_length) != 4:
            raise ValueError('Backup protetto incompleto o troncato.')
        (length,) = struct.unpack('>I', raw_length)
        if not 16 <= length <= CHUNK + 16:
            raise ValueError('Blocco del backup protetto non valido.')
        sealed = reader.read(length)
        if len(sealed) != length:
            raise ValueError('Backup protetto incompleto o troncato.')
        final = not reader.peek(1)
        try:
            plain = aes.decrypt(_nonce(index), sealed, _aad(digest, index, final))
        except InvalidTag:
            if index == 0:
                raise WrongPassword('Password errata o backup protetto alterato.') from None
            raise ValueError('Backup protetto alterato o troncato.') from None
        out.write(plain)
        index += 1
        if final:
            return index
