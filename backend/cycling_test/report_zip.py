"""Deterministic ZIP containers for exported reports (REPORT-ZIP-01).

``ZipFile.writestr`` with a plain name stamps the current local time, and
``ZipFile.write`` copies the file's mtime and permissions: two exports of the same
report a second apart then differ byte for byte, and so does the ``file_sha256``
recorded by ``save_report``. Members written through :class:`ReportZip` carry a
fixed timestamp, fixed permissions, a fixed creator system and the archive's own
compression, so the bytes depend only on member names, order and contents.
Names, order and contents are left to the callers and are not changed here.
"""

import zipfile
from pathlib import Path

# 1980-01-01 00:00:00, the earliest date the ZIP format can represent; the usual
# choice for reproducible archives.
FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o600  # what ZipFile.writestr already used for plain names
CREATE_SYSTEM = 3  # Unix: the mode in external_attr is a Unix mode on every platform


class ReportZip(zipfile.ZipFile):
    """ZipFile whose members do not depend on the clock, the platform or file metadata."""

    def writestr(self, zinfo_or_arcname, data, compress_type=None, compresslevel=None):
        if not isinstance(zinfo_or_arcname, zipfile.ZipInfo):
            info = zipfile.ZipInfo(zinfo_or_arcname, date_time=FIXED_DATE_TIME)
            info.create_system = CREATE_SYSTEM
            info.external_attr = FILE_MODE << 16
            info.compress_type = self.compression
            zinfo_or_arcname = info
            # ZipInfo.compress_level exists only from Python 3.13 (3.12 has a private
            # slot): pass the archive's level through writestr, which sets it on every
            # supported version.
            if compresslevel is None:
                compresslevel = self.compresslevel
        super().writestr(zinfo_or_arcname, data, compress_type, compresslevel)

    def write(self, filename, arcname=None, compress_type=None, compresslevel=None):
        self.writestr(arcname or Path(filename).name, Path(filename).read_bytes(), compress_type, compresslevel)


def report_zip(out):
    """Open ``out`` for writing a deflated report ZIP with deterministic member metadata."""
    return ReportZip(out, 'w', zipfile.ZIP_DEFLATED)
