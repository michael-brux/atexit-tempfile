from tempfile import mkstemp
from .atexit_cleanup import register_tempfile

SUFFIX = ".atexit"  # default tempfile suffix
PREFIX = "atexit_"  # default tempfile prefix

def atexit_mkstemp(
        suffix: str = SUFFIX,
        prefix: str = PREFIX,
        dir: str | None = None,
        text: bool = True):
    """
        Create a temporary file that is automatically cleaned up at program exit.

        This function wraps `tempfile.mkstemp` to create a temporary file and
        registers it for cleanup using `add_tempfile`. The temporary file will
        be deleted when the program exits.

        Args:
            suffix (str): Suffix for the temporary file. Defaults to ".atexit".
            prefix (str): Prefix for the temporary file. Defaults to "atexit_".
            dir (str | None): Directory where the file will be created. If None,
                the default temporary directory is used. Defaults to None.
            text (bool): If True, the file is opened in text mode. Defaults to True.

        Returns:
            tuple[int, str]: A tuple containing the file descriptor and the
            absolute path of the created temporary file.
        """
    fd, filename = mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)
    register_tempfile(fd, filename)
    return fd, filename

def atexit_write_tempfile(
        temp_data: bytes|str,
        suffix: str = SUFFIX,
        prefix: str = PREFIX,
        dir: str | None = None,
        text: bool = True):
    fd, filename = atexit_mkstemp(suffix=suffix, prefix=prefix, dir=dir)
    if isinstance(temp_data, str) and text:
        with open(filename, "w") as f:
            f.write(temp_data)
    elif isinstance(temp_data, bytes) and not text:
        with open(filename, "wb") as f:
            f.write(temp_data)
    else:
        raise ValueError("temp_data must be str if text is True, bytes if text is False")
    return fd, filename