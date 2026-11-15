"""Product adapters; implementation is delivered by cycling-suite-core."""

from cycling_suite.transports import MAX_PACKET, MAX_INVENTORY, MAX_FILES, safe_name, NoRedirect, validate_url
from cycling_suite.transports import FolderTransport as SharedFolder, WebDAVTransport as SharedWebDAV
from .compatibility import channel_directory
from . import __version__


class FolderTransport(SharedFolder):
    def __init__(self, folder, channel, store_root):
        super().__init__(folder, channel, store_root, channel_directory=channel_directory)


class WebDAVTransport(SharedWebDAV):
    def __init__(self, url, username, password, channel, *, allow_loopback=False, timeout=25):
        super().__init__(
            url,
            username,
            password,
            channel,
            allow_loopback=allow_loopback,
            timeout=timeout,
            prefix='fuorigiri',
            user_agent='Fuorigiri/' + __version__,
        )
