from pathlib import Path
import os
from ._SETTINGS import _USE_LOGGING, _PRINT_DEBUG_LOG
from tempfile import gettempdir

# Get the system's temporary directory path
TEMP_DIR = gettempdir()

def debug_log(msg):
    """
    Logs a debug message to the console if debug logging is enabled.

    Args:
        msg (str): The debug message to log.
    """
    if _PRINT_DEBUG_LOG:
        print(f"[DEBUG] {msg}")

def _cleanup(path: Path) -> None | TypeError | ValueError | OSError:
    """
    Cleans up (deletes) a file at the specified path, ensuring the path is valid and within the temporary directory.

    Args:
        path (Path): The path of the file to be deleted.

    Returns:
        None: If the file was successfully deleted.
        TypeError: If the provided path is not of type `Path`.
        ValueError: If the path is empty or not within the temporary directory.
        OSError: If an error occurs during file deletion (e.g., file not found, permission error).

    Note:
        This function does not raise exceptions; it returns the exception instance if an error occurs.
    """
    if not isinstance(path, Path):
        # Only Path objects are allowed
        return TypeError(f"path must be type Path: is {type(path)}")
    if path == Path(""):
        # Empty path "." is not allowed
        return ValueError(f"path cannot be empty")
    if not path.is_relative_to(TEMP_DIR):
        # Path must be within the temporary directory
        return ValueError(f"path is not in temp directory: {path}")
    try:
        # Attempt to delete the file
        os.remove(path)
        return None  # None indicates no error occurred
    except (TypeError,  # Already captured by the TypeError check above
            IsADirectoryError,  # Raised if the path is a directory
            PermissionError,  # Raised if the file cannot be accessed
            FileNotFoundError,  # Raised if the file does not exist
            OSError) as exc:  # General OS-related errors
        return exc
