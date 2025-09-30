
import atexit_tempfile
from tempfile import mkstemp
import os
import subprocess
import sys
import tempfile
from time import sleep
import gc

def test1():

    fd, filename = mkstemp(suffix=".atexit", prefix='test_', text=True)

    c = atexit_tempfile.CleanupResource(fd, filename)
    assert c.fd == fd
    assert c.path == filename

    c.cleanup()
    assert os.path.exists(filename) == False

def test2():

    fd, filename = mkstemp(suffix=".atexit", prefix='test_', text=True)

    c = atexit_tempfile.CleanupResource(fd, filename)
    assert c.fd == fd
    assert c.path == filename

    # file should be deleted when the object is garbage collected
    del c
    #gc.collect()
    #sleep(0.05)
    assert os.path.exists(filename) == False

def test3():

    fd, filename = mkstemp(suffix=".atexit", prefix='test_', text=True)

    c = atexit_tempfile.CleanupResource(fd, filename)
    assert c.fd == fd
    assert c.path == filename

    return fd, filename
    # file should be deleted when the object is garbage collected

def test_cleanup_via_atexit_or_finalize():
    """
    Test that CleanupResource deletes the file via atexit or weakref.finalize
    when the process exits, without explicit cleanup or deletion.
    """
    fd, filename = tempfile.mkstemp(suffix=".atexit", prefix='test_', text=True)
    os.close(fd)  # Close in parent, child will manage

    # Write a Python script to run in a subprocess
    script = f"""
import atexit_tempfile
import os
fd = os.open(r'{filename}', os.O_RDWR)
c = atexit_tempfile.CleanupResource(fd, r'{filename}')
# Do not call cleanup or delete c
"""
    # Run the script in a subprocess
    result = subprocess.run([sys.executable, "-c", script])
    # After subprocess exits, file should be deleted
    assert not os.path.exists(filename), f"File {filename} was not deleted by atexit/finalize"

test1()
test2()
fd, filename = test3()
#gc.collect()
#sleep(0.05)
assert os.path.exists(filename) == False
test_cleanup_via_atexit_or_finalize()
