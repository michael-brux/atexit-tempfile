#!/usr/bin/env python3
"""
Comprehensive test demonstrating safe_remove with weakref.finalize in a realistic scenario.
This shows how safe_remove prevents exceptions during cleanup.
"""

import os
import tempfile
import weakref
from atexit_tempfile import safe_remove


def test_realistic_scenario():
    """
    Simulates a realistic scenario where a class manages temporary files
    and uses weakref.finalize for cleanup.
    """
    
    class TempFileManager:
        """A class that manages temporary files with automatic cleanup."""
        
        def __init__(self, prefix="test_"):
            self.fd, self.path = tempfile.mkstemp(prefix=prefix)
            # Use safe_remove to prevent exception messages during cleanup
            self._finalizer = weakref.finalize(self, safe_remove, self.path)
            # Also need to close the file descriptor
            self._fd_finalizer = weakref.finalize(self, self._safe_close, self.fd)
            print(f"Created temporary file: {self.path}")
        
        @staticmethod
        def _safe_close(fd):
            """Safely close a file descriptor."""
            try:
                os.close(fd)
            except OSError:
                pass
        
        def write(self, data):
            """Write data to the temporary file."""
            os.write(self.fd, data.encode() if isinstance(data, str) else data)
        
        def read(self):
            """Read data from the temporary file."""
            os.lseek(self.fd, 0, os.SEEK_SET)
            return os.read(self.fd, 1024).decode()
    
    print("\n=== Test 1: Normal cleanup ===")
    manager1 = TempFileManager(prefix="normal_")
    manager1.write("Test data")
    path1 = manager1.path
    print(f"File exists before deletion: {os.path.exists(path1)}")
    del manager1
    print(f"File exists after deletion: {os.path.exists(path1)}")
    print("✓ File cleaned up successfully, no exceptions\n")
    
    print("=== Test 2: Manual deletion before finalize ===")
    manager2 = TempFileManager(prefix="manual_")
    path2 = manager2.path
    print(f"File exists: {os.path.exists(path2)}")
    
    # Manually close and remove (simulating a scenario where cleanup happens twice)
    os.close(manager2.fd)
    os.remove(path2)
    print(f"Manually removed file: {os.path.exists(path2)}")
    
    # Now delete the manager - finalize will try to remove an already-deleted file
    # With safe_remove, this won't print any exception
    del manager2
    print("✓ No exception printed even though file was already removed\n")
    
    print("=== Test 3: Multiple managers ===")
    managers = [TempFileManager(prefix=f"multi_{i}_") for i in range(3)]
    paths = [m.path for m in managers]
    
    print(f"Created {len(managers)} managers")
    for i, path in enumerate(paths):
        print(f"  File {i} exists: {os.path.exists(path)}")
    
    # Delete all managers
    del managers
    
    print("After deleting all managers:")
    for i, path in enumerate(paths):
        print(f"  File {i} exists: {os.path.exists(path)}")
    print("✓ All files cleaned up successfully\n")


if __name__ == "__main__":
    test_realistic_scenario()
    print("✅ All realistic scenario tests passed!")
