#!/usr/bin/env python3

import sys
from pathlib import Path
from atexit_tempfile import atexit_mkstemp, atexit_write_tempfile

def test_mkstemp():
    fd, filename = atexit_mkstemp()
    assert fd >= 0
    import tempfile
    expected_dir = Path(tempfile.gettempdir())
    assert Path(filename).parent == expected_dir
    assert Path(filename).name.startswith("atexit_")
    assert Path(filename).name.endswith(".atexit")

def test_write_tempfile():
    fd, filename = atexit_write_tempfile("Hello World!")
    with open(filename, "r") as f:
        assert f.read() == "Hello World!"

def print_tempfiles():
    import tempfile
    tempfile_dir = Path(tempfile.gettempdir())
    for path in tempfile_dir.iterdir():
        if path.name.startswith("atexit_") and path.name.endswith(".atexit"):
            print(path)

print("Temporary files before tests:")
print_tempfiles()
test_mkstemp()
test_write_tempfile()
print("Temporary files after tests:")
print_tempfiles()