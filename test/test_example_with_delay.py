#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tempfile import NamedTemporaryFile
from pathlib import Path
from atexit_tempfile import CleanupWithDel, CleanupWithFinalize

def with_no_delay():
    with NamedTemporaryFile(delete=False) as tmp:
        filename = tmp.name
        filepath = Path(filename)
        obj = CleanupWithDel(filepath, delay_till_exit=False)
    assert filepath.exists(), "File should exist"
    return filepath

tmp_path = with_no_delay()
print(f"Filepath: {tmp_path}")
assert not tmp_path.exists(), "File should have been deleted on function exit"

def with_delay():
    with NamedTemporaryFile(delete=False) as tmp:
        filename = tmp.name
        filepath = Path(filename)
        obj = CleanupWithDel(filepath, delay_till_exit=True)
    assert filepath.exists(), "File should exist"
    return filepath

tmp_path = with_delay()
print(f"Filepath: {tmp_path}")
assert tmp_path.exists(), "File should still exist till end of program"

print("the first Filepath should have been deleted, the second one should delete on program exit")