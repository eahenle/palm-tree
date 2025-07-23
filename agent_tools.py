# agent_tools.py
try:
    from llama_index.core.tools.types import BaseTool
except Exception:
    from llama_index.tools.types import BaseTool

try:
    from llama_index.core.tools.tool_spec.base import ToolMetadata
except Exception:
    from llama_index.tools.tool_spec.base import ToolMetadata
from github import Github
import os
import re

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
REPO = None
if GITHUB_TOKEN and GITHUB_REPO:
    try:
        REPO = Github(GITHUB_TOKEN).get_repo(GITHUB_REPO)
    except Exception:
        REPO = None

class FixPostTool(BaseTool):
    def __init__(self, pr_number: int):
        self.name = "FixPostTool"
        self.description = "Fixes blog post content in the PR."
        self.pr_number = pr_number

    @property
    def metadata(self):
        return ToolMetadata(name=self.name, description=self.description)

    def __call__(self, file_name: str, new_content: str) -> str:
        pr = REPO.get_pull(self.pr_number)
        branch = pr.head.ref

        contents = REPO.get_contents(file_name, ref=branch)
        REPO.update_file(contents.path, f"fix: updated {file_name}", new_content, contents.sha, branch=branch)
        return f"✅ Updated `{file_name}` in PR #{self.pr_number}"

class SuggestTitleTool(BaseTool):
    def __init__(self):
        self.name = "SuggestTitleTool"
        self.description = "Suggests an improved title for a blog post."

    @property
    def metadata(self):
        return ToolMetadata(name=self.name, description=self.description)

    def __call__(self, content: str) -> str:
        match = re.search(r"# (.+)", content)
        if not match:
            return "❌ No H1 title found."
        original = match.group(1)
        suggestion = (
            original.title()
            .replace(" And ", " and ")
            .replace(" Of ", " of ")
            .replace(" A ", " a ")
        )
        return f"💡 Suggested title: {suggestion}"
