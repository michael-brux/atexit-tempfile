"""
A module to ensure temporary files are cleaned up on program exit.

This module provides functions to register file descriptors and paths
for automatic cleanup when the Python interpreter exits. It uses the
`atexit` module to schedule the cleanup operations.
"""
from sys import modules
from pathlib import Path
import os
from threading import Lock
import weakref

USE_ATEXIT = True

if USE_ATEXIT:
    from atexit import register
else:
    from weakref import finalize

_fd_list = list()
_file_list = list()
_lock = Lock()


def register_fd(fd: int) -> bool:
    """
    Register a file descriptor for cleanup at exit.

    Args:
        fd: The file descriptor to close at exit.

    Returns:
        True if registration was successful, False otherwise.
    """
    try:
        os.fstat(fd)
    except OSError:
        return False
    with _lock:
        _fd_list.append(fd)
    return True


def register_file(path: Path | str) -> bool:
    """
    Register a file path for cleanup at exit.

    Args:
        path: The file path to remove at exit.

    Returns:
        True if registration was successful, False otherwise.
    """
    try:
        os.stat(path)
    except OSError:
        return False
    with _lock:
        _file_list.append(path)
    return True


def register_tempfile(fd: int, path: Path | str) -> bool:
    """
    Register a file descriptor and path for cleanup at exit.

    Args:
        fd: The file descriptor to close.
        path: The file path to remove.
    """
    result_fd = register_fd(fd)
    result_file = register_file(path)
    return result_fd and result_file

def _cleanup_tempfiles():
    """
    Close all registered file descriptors and remove all registered files.
    This function is registered to be called at program exit.
    """
    with _lock:
        # It's safer to work on copies of the lists
        fds_to_close = list(_fd_list)
        paths_to_remove = list(_file_list)
        _fd_list.clear()
        _file_list.clear()

    for fd in fds_to_close:
        try:
            os.close(fd)
        except OSError:
            pass
    for path in paths_to_remove:
        try:
            os.remove(path)
        except OSError:
            pass


class TempfileCleaner:
    """
    Class to manage cleanup of temporary files and file descriptors for all instances.
    """
    _instances = []

    def __init__(self, fd: int = None, path: Path | str = None):
        self.fd = fd
        self.path = path
        # Add a weak reference to this instance
        self_ref = weakref.ref(self, self._remove_dead_ref)
        TempfileCleaner._instances.append(self_ref)

    def cleanup(self):
        """
        Cleanup the file descriptor and/or file path for this instance.
        """
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.fd = None
        if self.path is not None:
            try:
                os.remove(self.path)
            except OSError:
                pass
            self.path = None

    @classmethod
    def _atexit(cls):
        """
        Classmethod to cleanup all living instances at program exit.
        """
        for ref in cls._instances:
            inst = ref()
            if inst is not None:
                inst.cleanup()
        cls._instances.clear()

    @classmethod
    def _remove_dead_ref(cls, ref):
        """
        Remove dead weak references from the _instances list.
        """
        try:
            cls._instances.remove(ref)
        except ValueError:
            pass

    def __del__(self):
        # Remove this instance's weakref from the list if it's being deleted
        # (handled by weakref callback, but __del__ is a fallback)
        for ref in list(self._instances):
            if ref() is self:
                self._instances.remove(ref)
                break

# Register the classmethod with atexit
if USE_ATEXIT:
    register(TempfileCleaner._atexit)
else:
    # Using finalize on the module object for cleanup at shutdown
    this_module = modules[__name__]
    finalize(this_module, _cleanup_tempfiles)
