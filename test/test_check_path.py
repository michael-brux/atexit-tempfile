import unittest
from pathlib import Path
import tempfile
import os
import sys

from src.atexit_tempfile.cleanup_classes import check_path, TEMP_DIR

test_temp_dir = Path.home() / "temp"
if not test_temp_dir.exists():
    os.mkdir(test_temp_dir)

class TestCheckPath(unittest.TestCase):

    def setUp(self):
        # Create a temp file inside TEMP_DIR
        self.temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False)
        self.temp_file_path = Path(self.temp_file.name)
        self.temp_file.close()

        # Create a temp directory inside TEMP_DIR
        self.temp_dir = tempfile.TemporaryDirectory(dir=TEMP_DIR)
        self.temp_dir_path = Path(self.temp_dir.name)

        # Path outside TEMP_DIR
        self.outside_file = tempfile.NamedTemporaryFile(delete=False, dir=test_temp_dir )
        self.outside_file_path = Path(self.outside_file.name)
        self.outside_file.close()

    def tearDown(self):
        os.unlink(self.temp_file_path)
        self.temp_dir.cleanup()
        os.unlink(self.outside_file_path)

    def test_valid_path(self):
        result = check_path(self.temp_file_path)
        self.assertEqual(result, self.temp_file_path)

    def test_empty_path(self):
        with self.assertRaises(ValueError):
            check_path("")

    def test_none_path(self):
        with self.assertRaises(ValueError):
            check_path(None)

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            check_path(123)

    def test_nonexistent_file(self):
        fake_path = Path(TEMP_DIR) / "nonexistent.txt"
        with self.assertRaises(FileNotFoundError):
            check_path(fake_path)

    def test_not_a_file(self):
        with self.assertRaises(ValueError):
            check_path(self.temp_dir_path)

    def test_path_outside_tempdir(self):
        with self.assertRaises(ValueError):
            check_path(self.outside_file_path)

if __name__ == "__main__":
    unittest.main()
