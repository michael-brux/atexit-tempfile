"""
A module to automatically clean up temporary files and file descriptors at exit.

This module provides a mechanism to register temporary files and file descriptors
for cleanup when the Python interpreter exits. It uses the `atexit` module
to ensure that cleanup operations are performed.
"""
from atexit import register
from pathlib import Path
import os

SILENT = False
USE_PROC_FILESYSTEM = True

_fd_set = set()
_file_set = set()

def _has_proc_filesystem() -> bool:
    """
    Check if the system has a proc filesystem with file descriptor info.

    This is typically true on Linux systems. It is used to automatically
    determine the path of a file from its file descriptor.

    Returns:
        bool: True if /proc/self/fd exists, False otherwise.
    """
    if USE_PROC_FILESYSTEM:
        if os.name != "posix":
            return False
        return os.path.isdir("/proc/self/fd")
    else:
        return False

def register_fd(fd:int, register_file_too:bool = True):
    try:
        stat = os.fstat(fd)
    except OSError:
        if not SILENT:
            raise ValueError("Invalid file descriptor")
    _fd_set.add(fd)
    if register_file_too and _has_proc_filesystem():
        try:
            path = os.readlink(f"/proc/self/fd/{fd}")
            register_file(path)
        except OSError:
            if not SILENT:
                print(f"Warning: Could not resolve path for fd {fd}")

def register_file(path:Path|str):
    try:
        stat = os.stat(path)
    except OSError:
        if not SILENT:
            raise ValueError("Invalid file path")
    _file_set.add(path)

def register_tempfile(fd:int, path:Path|str):
    register_fd(fd, register_file_too=False)
    register_file(path)

@register
def _cleanup_tempfiles():
    for fd in _fd_set:
        try:
            os.close(fd)
        except OSError:
            if not SILENT:
                print(f"Warning: Failed to close fd {fd}")
    for path in _file_set:
        try:
            os.remove(path)
        except OSError:
            if not SILENT:
                print(f"Warning: Failed to remove file {path}")