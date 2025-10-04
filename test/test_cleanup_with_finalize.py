
import unittest
from pathlib import Path
import tempfile
import os

from src.atexit_tempfile.cleanup_classes import CleanupWithFinalize, TEMP_DIR

class TestCleanupWithFinalize(unittest.TestCase):

    def setUp(self):
        # Create a temp file inside TEMP_DIR
        self.temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False)
        self.temp_file_path = Path(self.temp_file.name)
        self.temp_file.close()

    def tearDown(self):
        if self.temp_file_path.exists():
            os.unlink(self.temp_file_path)

    def test_init_valid_path(self):
        obj = CleanupWithFinalize(self.temp_file_path)
        self.assertEqual(obj.path, self.temp_file_path)

    def test_init_invalid_path(self):
        with self.assertRaises(ValueError):
            CleanupWithFinalize("")

    def test_cleanup_deletes_file(self):
        obj = CleanupWithFinalize(self.temp_file_path)
        obj.cleanup()
        self.assertFalse(self.temp_file_path.exists())

    def test_cleanup_twice_safe(self):
        obj = CleanupWithFinalize(self.temp_file_path)
        obj.cleanup()
        # Second call should not raise
        obj.cleanup()

    def test_delete_file_on_del(self):
        obj = CleanupWithFinalize(self.temp_file_path)
        del obj
        self.assertFalse(self.temp_file_path.exists())

    def test_delete_on_leave(self):
        def subroutine():
            obj = CleanupWithFinalize(self.temp_file_path)
        subroutine()
        self.assertFalse(self.temp_file_path.exists())

    def test_delete_on_subprocess(self):
        from textwrap import dedent
        script = dedent(f"""
        import sys
        from pathlib import Path
        from src.atexit_tempfile.cleanup_classes import CleanupWithFinalize
        
        temp_file = Path(sys.argv[1])
        obj = CleanupWithFinalize(temp_file)
        """)
        # Write the temp file path to pass to subprocess
        import subprocess
        subprocess.run(
            ["python", "-c", script, str(self.temp_file_path)],
            check=True
        )
        self.assertFalse(self.temp_file_path.exists())



if __name__ == "__main__":
    unittest.main()
