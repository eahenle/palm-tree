# agent_tools.py
from llama_index.core.tools.types import BaseTool, ToolMetadata
from github import Github
import os
import re

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
REPO = Github(GITHUB_TOKEN).get_repo(GITHUB_REPO) if GITHUB_TOKEN and GITHUB_REPO else None

class FixPostTool(BaseTool):
    def __init__(self, pr_number: int):
        self.pr_number = pr_number
        self._metadata = ToolMetadata(
            name="FixPostTool",
            description="Fixes blog post content in the PR."
        )

    @property
    def metadata(self) -> ToolMetadata:
        return self._metadata

    def __call__(self, file_name: str, new_content: str) -> str:
        pr = REPO.get_pull(self.pr_number)
        branch = pr.head.ref

        contents = REPO.get_contents(file_name, ref=branch)
        REPO.update_file(contents.path, f"fix: updated {file_name}", new_content, contents.sha, branch=branch)
        return f"✅ Updated `{file_name}` in PR #{self.pr_number}"

class SuggestTitleTool(BaseTool):
    def __init__(self):
        self._metadata = ToolMetadata(
            name="SuggestTitleTool",
            description="Suggests an improved title for a blog post."
        )

    @property
    def metadata(self) -> ToolMetadata:
        return self._metadata

    def __call__(self, content: str) -> str:
        match = re.search(r"# (.+)", content)
        if not match:
            return "❌ No H1 title found."
        original = match.group(1)
        suggestion = original.title()
        suggestion = re.sub(r"\b(And|Of|The|A|An)\b", lambda m: m.group(0).lower(), suggestion)
        return f"💡 Suggested title: {suggestion}"
