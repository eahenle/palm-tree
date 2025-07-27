"""Proxy module for backwards compatibility."""
from importlib import import_module
import sys
_module = import_module("publishing.github_utils")
sys.modules[__name__] = _module

