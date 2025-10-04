import unittest
import tempfile
import os
from pathlib import Path
from atexit_tempfile._cleanup_module import _cleanup
from tempfile import gettempdir

not_in_temp_dir = Path.home() / "not_in_temp_dir.tmp"

class TestCleanup(unittest.TestCase):
    def test_empty_path(self):
        exc = _cleanup(Path(""))
        self.assertIsInstance(exc, ValueError)

    def test_nonexistent_file(self):
        nonexistent_file = Path(gettempdir()) / "nonexistent_file.tmp"
        exc = _cleanup(nonexistent_file)
        self.assertFalse(nonexistent_file.exists())
        self.assertIsInstance(exc, FileNotFoundError)

    def test_permission_error(self):
        # Simulate permission error by opening file and removing write permission
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            path = Path(tmp.name)
            os.chmod(path, 0o400)  # read-only
        try:
            exc = _cleanup(path)
            self.assertIsInstance(exc, PermissionError)
        finally:
            os.chmod(path, 0o600)
            os.remove(path)

    def test_successful_cleanup(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            path = Path(tmp.name)

        # make sure tha file is closed before testing _cleanup
        exc = _cleanup(path)
        self.assertIsNone(exc)
        self.assertFalse(os.path.exists(path))

    def test_not_in_temp_dir(self):
        exc = _cleanup(not_in_temp_dir)
        self.assertIsInstance(exc, ValueError)

if __name__ == "__main__":
    unittest.main()
