# agent_tools.py
from llama_index.core.tools import BaseTool, ToolMetadata
from github import Github
import os
import re

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")


def get_repo():
    """Return the GitHub repo object when needed.

    Instantiating the repository lazily avoids side effects when this module is
    imported in tests where no network access or credentials are available.
    """
    return Github(GITHUB_TOKEN).get_repo(GITHUB_REPO)

class FixPostTool(BaseTool):
    def __init__(self, pr_number: int):
        self.pr_number = pr_number

    @property
    def metadata(self):
        return ToolMetadata(name="FixPostTool", description="Fixes blog post content in the PR.")

    def __call__(self, file_name: str, new_content: str) -> str:
        repo = get_repo()
        pr = repo.get_pull(self.pr_number)
        branch = pr.head.ref

        contents = repo.get_contents(file_name, ref=branch)
        repo.update_file(contents.path, f"fix: updated {file_name}", new_content, contents.sha, branch=branch)
        return f"✅ Updated `{file_name}` in PR #{self.pr_number}"

class SuggestTitleTool(BaseTool):
    def __init__(self):
        pass

    @property
    def metadata(self):
        return ToolMetadata(name="SuggestTitleTool", description="Suggests an improved title for a blog post.")

    def __call__(self, content: str) -> str:
        match = re.search(r"# (.+)", content)
        if not match:
            return "❌ No H1 title found."
        original = match.group(1)
        suggestion = (
            original.title()
            .replace("And", "and")
            .replace("Of", "of")
            .replace(" A ", " a ")
        )  # Toy example to keep short articles lowercase
        return f"💡 Suggested title: {suggestion}"
