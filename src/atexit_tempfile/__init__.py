# Public API re-exports for convenient imports
from .atexit_cleanup import register_tempfile
from .atexit_mkstemp import atexit_mkstemp

__all__ = ["register_tempfile", "atexit_mkstemp"]