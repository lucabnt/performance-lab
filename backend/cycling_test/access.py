"""Route-level authorization markers (RT-20)."""


def viewer_allowed(endpoint):
    """Mark a write route that viewers and revoked operators may still call.

    Use it for device-local actions (sync, preferences, backups, previews,
    society management) that never add a signed revision to the archive.
    Every other POST/PUT/DELETE route is refused to read-only identities by
    the API middleware, so a new route is protected unless marked here.
    """
    endpoint.viewer_allowed = True
    return endpoint
