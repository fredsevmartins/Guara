"""Cooperating-process locks, released by the OS if a process exits."""

import hashlib
import os
import stat
import threading
import time
from functools import wraps
from pathlib import Path


class WorkspaceBusy(TimeoutError):
    """A cooperating client holds the workspace operation lock."""


class WorkspaceLock:
    def __init__(self, workspace, data_dir, timeout=5):
        if not isinstance(timeout, (int, float)) or not 0 <= timeout <= 60:
            raise ValueError("Lock timeout must be between 0 and 60 seconds")
        name = hashlib.sha256(os.path.normcase(Path(data_dir).as_posix()).encode()).hexdigest()[:24]
        self.path = Path(workspace) / f".opentruth-lock-{name}"
        self.timeout = timeout
        self.mutex = threading.RLock()
        self.depth = 0
        self.descriptor = None

    def __enter__(self):
        if not self.mutex.acquire(timeout=self.timeout):
            raise WorkspaceBusy("Workspace busy; retry after the current operation finishes")
        try:
            if self.depth:
                self.depth += 1
                return self
            if self.path.is_symlink():
                raise ValueError("Unsafe workspace lock path")
            flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
            self.descriptor = os.open(self.path, flags, 0o600)
            if not stat.S_ISREG(os.fstat(self.descriptor).st_mode):
                raise ValueError("Workspace lock must be a regular file")
            if os.fstat(self.descriptor).st_size == 0:
                os.write(self.descriptor, b"0")
            deadline = time.monotonic() + self.timeout
            while True:
                try:
                    if os.name == "nt":
                        import msvcrt

                        os.lseek(self.descriptor, 0, os.SEEK_SET)
                        msvcrt.locking(self.descriptor, msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl

                        fcntl.flock(self.descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.depth = 1
                    return self
                except BlockingIOError:
                    pass
                except OSError as error:
                    if os.name != "nt" or error.errno not in (13, 36):
                        raise
                if time.monotonic() >= deadline:
                    raise WorkspaceBusy(
                        "Workspace busy; retry after the current operation finishes"
                    )
                time.sleep(0.025)
        except BaseException:
            if self.descriptor is not None:
                os.close(self.descriptor)
                self.descriptor = None
            self.mutex.release()
            raise

    def __exit__(self, *args):
        self.depth -= 1
        try:
            if not self.depth:
                os.close(self.descriptor)
                self.descriptor = None
        finally:
            self.mutex.release()


def operation(method):
    @wraps(method)
    def guarded(self, *args, **kwargs):
        with self._operation_lock:
            return method(self, *args, **kwargs)

    return guarded
