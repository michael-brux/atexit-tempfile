#!/usr/bin/env python3
"""
Test for safe_remove wrapper function.
"""

import os
import tempfile
import weakref
from pathlib import Path
from atexit_tempfile import safe_remove


def test_safe_remove_existing_file():
    """Test that safe_remove successfully removes an existing file."""
    fd, filepath = tempfile.mkstemp()
    os.close(fd)
    
    assert os.path.exists(filepath), "File should exist before removal"
    safe_remove(filepath)
    assert not os.path.exists(filepath), "File should not exist after safe_remove"
    print("✓ test_safe_remove_existing_file passed")


def test_safe_remove_nonexistent_file():
    """Test that safe_remove does not raise exception for non-existent file."""
    filepath = "/tmp/nonexistent_file_12345.tmp"
    
    # Ensure file doesn't exist
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # This should not raise any exception
    safe_remove(filepath)
    print("✓ test_safe_remove_nonexistent_file passed")


def test_safe_remove_with_weakref_finalize():
    """Test that safe_remove works with weakref.finalize without printing exceptions."""
    fd, filepath = tempfile.mkstemp()
    os.close(fd)
    
    class TestObject:
        pass
    
    obj = TestObject()
    finalizer = weakref.finalize(obj, safe_remove, filepath)
    
    assert os.path.exists(filepath), "File should exist before finalize"
    
    # Delete object, triggering finalize
    del obj
    
    assert not os.path.exists(filepath), "File should be removed by finalize"
    print("✓ test_safe_remove_with_weakref_finalize passed")


def test_safe_remove_with_weakref_finalize_nonexistent():
    """Test that safe_remove with weakref.finalize doesn't print errors for non-existent files."""
    filepath = "/tmp/nonexistent_file_67890.tmp"
    
    # Ensure file doesn't exist
    if os.path.exists(filepath):
        os.remove(filepath)
    
    class TestObject:
        pass
    
    obj = TestObject()
    # This should not print any exception message when obj is deleted
    finalizer = weakref.finalize(obj, safe_remove, filepath)
    
    # Delete object - should not print exception
    del obj
    
    print("✓ test_safe_remove_with_weakref_finalize_nonexistent passed (no exception printed)")


def test_safe_remove_with_path_object():
    """Test that safe_remove works with Path objects."""
    fd, filepath_str = tempfile.mkstemp()
    os.close(fd)
    filepath = Path(filepath_str)
    
    assert filepath.exists(), "File should exist before removal"
    safe_remove(filepath)
    assert not filepath.exists(), "File should not exist after safe_remove"
    print("✓ test_safe_remove_with_path_object passed")


if __name__ == "__main__":
    test_safe_remove_existing_file()
    test_safe_remove_nonexistent_file()
    test_safe_remove_with_weakref_finalize()
    test_safe_remove_with_weakref_finalize_nonexistent()
    test_safe_remove_with_path_object()
    print("\n✅ All tests passed!")
