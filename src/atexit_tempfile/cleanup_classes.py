"""
This module provides classes and utilities for managing temporary file cleanup
using different strategies, such as `__del__` and `weakref.finalize`. It also
integrates with `atexit` to ensure cleanup at interpreter shutdown.

Classes:
    - Cleanup: Abstract base class for cleanup implementations.
    - CleanupWithDel: Cleanup implementation using `__del__`.
    - CleanupWithFinalize: Cleanup implementation using `weakref.finalize`.

Functions:
    - check_path: Validates a given path to ensure it is a file within the temp directory.
    - _on_finalize: Finalizer function to clean up delayed objects.
    - _at_exit: Atexit handler to trigger finalization.

Constants:
    - TEMP_DIR: The system's temporary directory path.
"""

from ._cleanup_module import _cleanup
from tempfile import gettempdir
from pathlib import Path
from weakref import finalize
from atexit import register
from abc import ABC, abstractmethod
from sys import modules

# The system's temporary directory path
TEMP_DIR = gettempdir()


def check_path(path: Path | str):
    """
    Validates the given path to ensure it meets the following criteria:
    - It is not empty.
    - It is a string or Path object.
    - It exists and is a file.
    - It is located within the system's temporary directory.

    Args:
        path (Path | str): The path to validate.

    Returns:
        Path: The validated Path object.

    Raises:
        ValueError: If the path is empty or not a file.
        TypeError: If the path is not a string or Path object.
        FileNotFoundError: If the path does not exist.
    """
    if path is None or path == "" or path == Path(""):
        raise ValueError("path cannot be empty")
    if not isinstance(path, str) and not isinstance(path, Path):
        raise TypeError("path must be a string or Path")
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    if not path.is_relative_to(TEMP_DIR):
        raise ValueError(f"Path is not in temp directory: {path}")
    return path


class Cleanup(ABC):
    """
    Abstract base class for cleanup implementations.

    Attributes:
        _delay_till_exit (list): Class-level list to store objects for delayed cleanup.
    """

    _delay_till_exit = list()

    def __init__(self, path: Path | str, delay_till_exit: bool = False):
        """
        Initializes the Cleanup object.

        Args:
            path (Path | str): The path to the file to be cleaned up.
            delay_till_exit (bool): Whether to delay cleanup until interpreter exit.

        Raises:
            ValueError, TypeError, FileNotFoundError: If the path is invalid.
        """
        self._initialized = False
        self._path = check_path(path)  # raises exceptions on errors
        if delay_till_exit:
            Cleanup._delay_till_exit.append(self)
        self._init()
        self._initialized = True  # safeguard for partially initialized instances

    @abstractmethod
    def _init(self):
        """
        Abstract method for initialization logic in subclasses.
        """
        pass

    @property
    def path(self):
        """
        Returns the path associated with the Cleanup object.

        Returns:
            Path: The path to the file.
        """
        return self._path


class CleanupWithDel(Cleanup):
    """
    Cleanup implementation using the `__del__` method for cleanup.

    Attributes:
        _cleaned_up (bool): Tracks whether cleanup has been performed.
    """

    _cleaned_up = None

    def _init(self):
        """
        Initializes the CleanupWithDel object.
        """
        self._cleaned_up = False

    def cleanup(self) -> Exception | None:
        """
        Performs cleanup if it has not already been done.

        Returns:
            Exception | None: The exception raised during cleanup, if any.
        """
        if not self._cleaned_up:
            # This may run during interpreter shutdown
            # --> avoid raising new exceptions
            exc = _cleanup(self.path)
            self._cleaned_up = True
            return exc
        return None

    def __del__(self):
        """
        Destructor method to ensure cleanup is performed.
        """
        if not hasattr(self, "_initialized") or not self._initialized:
            # __del__ may be called when __init__ fails (e.g., raises exception)
            return  # safeguard for partially initialized instances
        self.cleanup()
        return


class CleanupWithFinalize(Cleanup):
    """
    Cleanup implementation using `weakref.finalize` for cleanup.

    Attributes:
        _finalizer (weakref.finalize): Finalizer object for cleanup.
    """

    _finalizer = None

    def _init(self):
        """
        Initializes the CleanupWithFinalize object and sets up the finalizer.
        """
        self._finalizer = finalize(self, _cleanup, self.path)

    def cleanup(self) -> Exception | None:
        """
        Performs cleanup by invoking the finalizer.

        Returns:
            Exception | None: The exception raised during cleanup, if any.
        """
        # Finalizer avoids double cleanup
        # No extra cleaned_up flag needed
        return self._finalizer.__call__()


def _on_finalize(*args, **kwargs):
    """
    Finalizer function to clean up objects marked for delayed cleanup.
    """
    delay_till_exit = Cleanup._delay_till_exit
    for ret in list(delay_till_exit):
        ret.cleanup()
    delay_till_exit.clear()


# Register a finalizer for the module to clean up delayed objects
finalize(modules[__name__], _on_finalize)


@register
def _at_exit(*args, **kwargs):
    """
    Atexit handler to trigger finalization at interpreter shutdown.
    """
    _on_finalize(*args, **kwargs)
