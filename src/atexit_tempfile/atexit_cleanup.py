"""
A module to automatically clean up temporary files and file descriptors at exit.

This module provides a mechanism to register temporary files and file descriptors
for cleanup when the Python interpreter exits. It uses the `atexit` module
to ensure that cleanup operations are performed.
"""
from atexit import register
from pathlib import Path
import os

_tempfile = list()

@register
def _cleanup_tempfiles():
    """
    Clean up all registered temporary files and file descriptors.

    This function is registered with `atexit` to be called on program exit.
    It iterates through a list of registered (fd, path) tuples, closes the
    file descriptor if it's not None, and removes the file at the given path
    if it's not None.
    """
    for fd, path in _tempfile:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if path is not None:
            try:
                os.remove(path)
            except OSError:
                pass
    _tempfile.clear()

def _has_proc_filesystem() -> bool:
    """
    Check if the system has a proc filesystem with file descriptor info.

    This is typically true on Linux systems. It is used to automatically
    determine the path of a file from its file descriptor.

    Returns:
        bool: True if /proc/self/fd exists, False otherwise.
    """
    if os.name != "posix":
        return False
    return os.path.isdir("/proc/self/fd")

def register_tempfile(fd:int = None, path:Path|str = None, check:bool= True):
    """
    Register a temporary file for cleanup at exit.

    At least one of `fd` or `path` must be provided.

    If only `fd` is provided, the function will attempt to determine the path
    from the file descriptor using the proc filesystem (if available).

    Args:
        fd (int, optional): The file descriptor of the temporary file. Defaults to None.
        path (Path | str, optional): The path to the temporary file. Defaults to None.
        check (bool, optional): If True, raise ValueError for invalid inputs.
                                Defaults to True.

    Raises:
        ValueError: If `check` is True and `fd` is invalid, or if both `fd`
                    and `path` are None.
    """
    if fd is not None:
        try:
            os.fstat(fd)
        except OSError:
            if check:
                raise ValueError("Invalid file descriptor")
            fd = None
    if fd is None and path is None:
        if check:
            raise ValueError("Either fd or path must be provided")
        return # do nothing
    if fd is not None and path is None:
        if _has_proc_filesystem():
            try:
                path = os.readlink(f"/proc/self/fd/{fd}")
            except OSError:
                pass
    _tempfile.append((fd, path))

if __name__ == "__main__":
    import tempfile as tf
    # Example usage
    fd, path = tf.mkstemp()
    print(f"Created temp file: {path} with fd: {fd}")
    register_tempfile(fd, path)
    # The temp file will be cleaned up automatically on program exit