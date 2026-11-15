"""Exports and backups of the selected archive."""

from pathlib import Path

from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .access import viewer_allowed


def install(app, store, require, download):
    @app.get("/api/v1/export/{organization_id}")
    def export(organization_id: str):
        from .reports import export_csv

        require(organization_id, "organization")
        return download(export_csv(store, organization_id), "application/zip", "storico-csv.zip")

    @app.get('/api/v1/backup/scalable')
    def scalable_backup():
        from .backup_stream import write_backup
        from starlette.background import BackgroundTask
        import tempfile, shutil

        stage = Path(tempfile.mkdtemp(prefix='fuorigiri-download-'))
        try:
            file = write_backup(store, stage / 'fuorigiri-backup-v3.zip')
            return FileResponse(
                file, media_type='application/zip', filename=file.name, background=BackgroundTask(shutil.rmtree, stage)
            )
        except Exception:
            shutil.rmtree(stage)
            raise

    class EncryptedBackup(BaseModel):
        # Password in the body, never in the URL or logs.
        password: str = Field(min_length=12, max_length=1000)

    @app.post('/api/v1/backup/scalable/encrypted')
    @viewer_allowed
    def encrypted_scalable_backup(data: EncryptedBackup):
        from .backup_stream import write_backup
        from .backup_crypto import encrypt_file
        from starlette.background import BackgroundTask
        import tempfile, shutil

        stage = Path(tempfile.mkdtemp(prefix='fuorigiri-download-'))
        try:
            plain = write_backup(store, stage / 'fuorigiri-backup-v3.zip')
            file = encrypt_file(plain, stage / 'fuorigiri-backup-v3.fgbak', data.password)
            plain.unlink()
            return FileResponse(
                file,
                media_type='application/octet-stream',
                filename=file.name,
                background=BackgroundTask(shutil.rmtree, stage),
            )
        except Exception:
            shutil.rmtree(stage)
            raise

    @app.get("/api/v1/backup")
    def backup():
        from .recovery import backup_bytes

        return download(backup_bytes(store), 'application/zip', 'fuorigiri-backup-dati.zip')
