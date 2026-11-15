"""Preserve the existing lock identity; use the shared OS primitive."""

from cycling_suite.instance import InstanceLock as SharedLock


class InstanceLock(SharedLock):
    def __init__(self, root):
        super().__init__(root, filename='fuorigiri-instance.lock', product='Fuorigiri')
