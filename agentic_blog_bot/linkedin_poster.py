"""Proxy module for backwards compatibility."""

from importlib import import_module
import sys

_module = import_module("linkedin_poster")
sys.modules[__name__] = _module
