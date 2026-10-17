"""OS-released archive lock: never delete another process's lock file."""
import os
from pathlib import Path


class InstanceLock:
    def __init__(self,root):
        root=Path(root);root.mkdir(parents=True,exist_ok=True)
        self.stream=(root/'fuorigiri-instance.lock').open('a+b')
        if self.stream.tell()==0:self.stream.write(b'\0');self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            raise ValueError('Questo archivio è già aperto in un’altra istanza di Fuorigiri. Chiudere quella finestra prima di riaprirlo.') from None

    def close(self):
        if self.stream.closed:return
        self.stream.seek(0)
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(self.stream.fileno(),msvcrt.LK_UNLCK,1)
        else:
            import fcntl
            fcntl.flock(self.stream.fileno(),fcntl.LOCK_UN)
        self.stream.close()
