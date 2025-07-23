import importlib
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

_modules = [
    "agent_tools",
    "github_utils",
    "config",
    "notifier",
    "linkedin_poster",
]

for _m in _modules:
    module = importlib.import_module(_m)
    sys.modules[f"agentic_blog_bot.{_m}"] = module
    setattr(sys.modules[__name__], _m, module)

__all__ = _modules
