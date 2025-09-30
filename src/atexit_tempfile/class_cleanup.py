import os
from pathlib import Path
from weakref import finalize
import weakref
from atexit import register

USE_ATEXIT = False
USE_FINALIZE = False
USE_LOGGING = False
DEBUG_LOG = False

if USE_LOGGING:
    import logging
    logger = logging.getLogger("atexit_tempfile")
    logging.basicConfig(level=logging.DEBUG)

def debug_log(msg):
    if DEBUG_LOG:
        print(f"[DEBUG] {msg}")
    if USE_LOGGING:
        logger.debug(msg)

class CleanupResource:
    """
    Manages a single temporary resource (file descriptor and path),
    ensuring cleanup when the object is no longer in use.
    """
    if USE_ATEXIT:
        _instances = []

    def __init__(self, fd: int, path: Path | str, delete: bool = True):
        self.fd = fd
        self.path = str(path)
        self.delete = delete
        self._cleaned_up = False
        debug_log(f"Initialized CleanupResource: fd={fd}, path={path}, delete={delete}")

        if USE_FINALIZE:
            self_ref = weakref.ref(self)
            finalize(self, cleanup, self_ref)
            debug_log("Registered finalize callback for CleanupResource.")

        if USE_ATEXIT:
            self_ref = weakref.ref(self, CleanupResource._remove_dead_ref)
            CleanupResource._instances.append(self_ref)
            debug_log("Added weakref to CleanupResource._instances.")

    @property
    def cleaned_up(self):
        return self._cleaned_up

    @staticmethod
    def _finalize(self_ref: weakref.ref):
        debug_log("Finalize callback triggered for CleanupResource.")
        instance = self_ref()
        if instance is not None:
            if not instance._cleaned_up:
                instance.cleanup()

    @classmethod
    def _remove_dead_ref(cls, ref):
        """
        Remove dead weak references from the _instances list.
        """
        try:
            cls._instances.remove(ref)
            debug_log("Removed dead weakref from CleanupResource._instances.")
        except ValueError:
            pass


    def cleanup(self):
        """Closes the file descriptor and removes the file."""
        if self._cleaned_up:
            debug_log("CleanupResource already cleaned up; skipping.")
            return

        try:
            os.close(self.fd)
            debug_log(f"Closed file descriptor: {self.fd}")
        except OSError:
            debug_log(f"Failed to close file descriptor: {self.fd}")

        if self.delete:
            try:
                os.remove(self.path)
                debug_log(f"Removed file: {self.path}")
            except OSError:
                debug_log(f"Failed to remove file: {self.path}")

        self._cleaned_up = True
        debug_log("CleanupResource marked as cleaned up.")

    def cleanup2(self):
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
        debug_log("Called cleanup2 on CleanupResource.")

    def close(self):
        """Explicitly cleans up the resource."""
        debug_log("Explicit close called on CleanupResource.")
        self.cleanup()

    def __del__(self):
        """Fallback cleanup when the object is garbage collected."""
        debug_log("CleanupResource __del__ called.")
        self.cleanup()
        if USE_ATEXIT:
            for ref in list(self._instances):
                if ref() is self:
                    self._instances.remove(ref)
                    debug_log("Removed weakref from CleanupResource._instances in __del__.")
                    break

    @classmethod
    def on_atexit(cls):
        """
        Class method to clean up all living instances at program exit.
        """
        debug_log("on_atexit called for CleanupResource.")
        for ref in list(cls._instances):
            inst = ref()
            if inst is not None:
                inst.cleanup()
        cls._instances.clear()
        debug_log("CleanupResource._instances cleared in on_atexit.")


def cleanup(self_ref: weakref.ref):
    debug_log("Finalize callback triggered for CleanupResource.")
    instance = self_ref()
    if instance is not None:
        if not instance.cleaned_up:
            instance.cleanup()


# Register the classmethod with atexit
if USE_ATEXIT:
    register(CleanupResource.on_atexit)
    debug_log("Registered CleanupResource.on_atexit with atexit.")
