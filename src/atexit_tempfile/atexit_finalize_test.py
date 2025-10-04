#!/usr/bin/env python3

from atexit import register
from sys import modules
from weakref import finalize

#
#
#

def print_args(function=None, *args, **kwargs):
    print(f"*** {function}:")
    print(f"    args: ", args)
    print(f"    kwargs: ", kwargs)

def at_exit(*args, **kwargs):
    print_args(at_exit,*args, **kwargs)
register(at_exit, "first", "register", at="atexit")

def at_finalize(*args, **kwargs):
    print_args(at_finalize, *args, **kwargs)
finalize(modules[__name__], at_finalize, "first", "module", at="finalize")

class OnDel:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        # this is executed as second finalizer
        # finalizers are executed before __del__
        self._finalizer = finalize(self, print_args, OnDel, *self.args, at="finalize")
    def __del__(self):
        # this is executed after finalizers and after atexit
        print_args( self, *self.args, at="__del__")
# create object (and activate finalizer)
obj = OnDel("third", "OnDel Object", at1="del", at2="finalize")

# second finalizer is executed
finalize(modules[__name__], at_finalize, "second", "module", at="finalize")

# second atexit to check execution order
register(at_exit, "second", "register", at="atexit")

# last finalizer is executed first
finalize(modules[__name__], at_finalize, "third", "module", at="finalize")

print("*** Done")