"""Stub shim for pyarrow top-level package.

The installed pyarrow/__init__.pyi already declares `__getattr__` so that any
attribute access returns `Any`.  This file mirrors that declaration so that
pyright does not lose it when this project's stubPath takes precedence for the
pyarrow package (because stubs/pyarrow/compute.pyi exists).
"""

from typing import Any

def __getattr__(name: str) -> Any: ...
