# atexit-tempfile
Generate Python temporary files with atexit cleanup

## Features

- **atexit_mkstemp**: Create temporary files that are automatically cleaned up at program exit
- **CleanupResource**: Manage temporary resources with automatic cleanup
- **safe_remove**: A wrapper for `os.remove` that suppresses exceptions, designed for use with `weakref.finalize`

## Installation

```bash
pip install atexit-tempfile
```

## Usage

### Basic temporary file creation

```python
from atexit_tempfile import atexit_mkstemp, atexit_write_tempfile

# Create a temporary file
fd, filename = atexit_mkstemp()

# Write to a temporary file
fd, filename = atexit_write_tempfile("Hello World!")
```

### Using safe_remove with weakref.finalize

The `safe_remove` function is a wrapper around `os.remove` that suppresses `OSError` exceptions. This is particularly useful when using `weakref.finalize` for cleanup, as it prevents exception messages from being printed to stderr during finalization.

```python
import weakref
from atexit_tempfile import safe_remove

class MyResource:
    def __init__(self, filename):
        self.filename = filename
        # Use safe_remove to prevent exception messages during cleanup
        self._finalizer = weakref.finalize(self, safe_remove, filename)

# When the object is garbage collected, safe_remove will be called
# without printing exceptions if the file doesn't exist
```

**Why use safe_remove?**

When using `os.remove` directly with `weakref.finalize`, if the file doesn't exist or can't be removed, an exception message is printed to stderr:

```
Exception ignored in: <finalize object at 0x...>
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/file'
```

Using `safe_remove` prevents these messages from appearing, providing cleaner output during cleanup.
