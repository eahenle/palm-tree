import importlib
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

_modules_map = {
    "agent_tools": "authorship.agent_tools",
    "github_utils": "publishing.github_utils",
    "config": "config",
    "notifier": "publishing.notifier",
    "linkedin_poster": "publishing.linkedin_poster",
}

for name, path in _modules_map.items():
    module = importlib.import_module(path)
    sys.modules[f"agentic_blog_bot.{name}"] = module
    setattr(sys.modules[__name__], name, module)

__all__ = list(_modules_map.keys())
