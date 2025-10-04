import unittest
from pathlib import Path
import tempfile
import os

from atexit_tempfile.cleanup_classes import CleanupWithDel, TEMP_DIR

class TestCleanupWithDel(unittest.TestCase):

    def setUp(self):
        # Create a temp file inside TEMP_DIR
        self.temp_file = tempfile.NamedTemporaryFile(dir=TEMP_DIR, delete=False)
        self.temp_file_path = Path(self.temp_file.name)
        self.temp_file.close()

    def tearDown(self):
        if self.temp_file_path.exists():
            os.unlink(self.temp_file_path)

    def test_init_valid_path(self):
        obj = CleanupWithDel(self.temp_file_path)
        self.assertEqual(obj.path, self.temp_file_path)
        self.assertFalse(obj._cleaned_up)
        self.assertTrue(obj._initialized)

    def test_init_invalid_path(self):
        with self.assertRaises(ValueError):
            CleanupWithDel("")

    def test_cleanup_returns_none(self):
        obj = CleanupWithDel(self.temp_file_path)
        self.assertTrue(self.temp_file_path.exists())
        result = obj.cleanup()
        self.assertIsNone(result)
        self.assertFalse(self.temp_file_path.exists())
        #self.assertEqual(len(result), 1)
        self.assertTrue(obj._cleaned_up)


    def test_cleanup_twice_returns_none(self):
        obj = CleanupWithDel(self.temp_file_path)
        self.assertTrue(self.temp_file_path.exists())
        obj.cleanup()
        self.assertFalse(self.temp_file_path.exists())
        result = obj.cleanup()
        self.assertIsNone(result)

    def test_del_safeguard(self):
        # Simulate partially initialized instance
        obj = object.__new__(CleanupWithDel)
        obj._initialized = False
        # __del__ should not raise
        try:
            obj.__del__()
        except Exception as e:
            self.fail(f"__del__ raised exception: {e}")
        self.assertTrue(Path(self.temp_file_path).exists())

    def test_blank_instance(self):
        # create a blank instance
        obj = object.__new__(CleanupWithDel)
        self.assertFalse(hasattr(obj, "_initialized"))
        try:
            obj.__del__()  # del should do nothing
        except Exception as e:
            self.fail(f"__del__ raised exception: {e}")
        self.assertTrue(Path(self.temp_file_path).exists())

    def test_del_deletes_file(self):
        obj = CleanupWithDel(self.temp_file_path)
        self.assertTrue(Path(self.temp_file_path).exists())
        del obj
        self.assertFalse(Path(self.temp_file_path).exists())

    def test_delete_on_leave(self):
        def subroutine():
            obj = CleanupWithDel(self.temp_file_path)
        subroutine()
        self.assertFalse(self.temp_file_path.exists())

    def test_delete_on_subprocess(self):
        from textwrap import dedent
        script = dedent(f"""
        import sys
        from pathlib import Path
        from src.atexit_tempfile.cleanup_classes import CleanupWithDel

        temp_file = Path(sys.argv[1])
        obj = CleanupWithDel(temp_file)
        """)
        # Write the temp file path to pass to subprocess
        import subprocess
        subprocess.run(
            ["python", "-c", script, str(self.temp_file_path)],
            check=True
        )
        self.assertFalse(self.temp_file_path.exists())

    def test_delayed_deleting(self):
        from textwrap import dedent
        script = dedent(f"""
                import sys
                from pathlib import Path
                from src.atexit_tempfile.cleanup_classes import CleanupWithDel

                temp_file = Path(sys.argv[1])
                def subroutine():
                    obj = CleanupWithDel(temp_file, delay_till_exit=True)
                subroutine()
                assert temp_file.exists()
                """)
        # Write the temp file path to pass to subprocess
        import subprocess
        subprocess.run(
            ["python", "-c", script, str(self.temp_file_path)],
            check=True
        )
        self.assertFalse(self.temp_file_path.exists())

    def test_non_delayed_deleting(self):
        from textwrap import dedent
        script = dedent(f"""
                import sys
                from pathlib import Path
                from src.atexit_tempfile.cleanup_classes import CleanupWithDel

                temp_file = Path(sys.argv[1])
                def subroutine():
                    obj = CleanupWithDel(temp_file, delay_till_exit=False)
                subroutine()
                assert not temp_file.exists()
                """)
        # Write the temp file path to pass to subprocess
        import subprocess
        subprocess.run(
            ["python", "-c", script, str(self.temp_file_path)],
            check=True
        )
        self.assertFalse(self.temp_file_path.exists())


    def test_run_example(self):
        import subprocess
        import re
        from pathlib import Path

        result = subprocess.run(
            ["python", "test/test_example_with_delay.py"],
            capture_output=True,
            text=True,
            check=True
        )
        # Find all Filepath outputs
        matches = re.findall(r"Filepath: (.+)", result.stdout)
        assert len(matches) == 2, "Expected two Filepath outputs"
        first_path = Path(matches[0].strip())
        second_path = Path(matches[1].strip())

        # First file should have been deleted
        self.assertFalse(first_path.exists(), f"{first_path} should have been deleted on function exit")
        # Second file should have been deleted on program exit
        self.assertFalse(second_path.exists(), f"{second_path} should have been deleted on program exit")


if __name__ == "__main__":
    unittest.main()
