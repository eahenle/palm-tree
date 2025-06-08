# agent_tools.py
from llama_index.tools.tool_spec.base import BaseTool
from github import Github
import os
import re

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
REPO = Github(GITHUB_TOKEN).get_repo(GITHUB_REPO)

class FixPostTool(BaseTool):
    def __init__(self, pr_number: int):
        super().__init__(name="FixPostTool", description="Fixes blog post content in the PR.")
        self.pr_number = pr_number

    def __call__(self, file_name: str, new_content: str) -> str:
        pr = REPO.get_pull(self.pr_number)
        branch = pr.head.ref

        contents = REPO.get_contents(file_name, ref=branch)
        REPO.update_file(contents.path, f"fix: updated {file_name}", new_content, contents.sha, branch=branch)
        return f"✅ Updated `{file_name}` in PR #{self.pr_number}"

class SuggestTitleTool(BaseTool):
    def __init__(self):
        super().__init__(name="SuggestTitleTool", description="Suggests an improved title for a blog post.")

    def __call__(self, content: str) -> str:
        match = re.search(r"# (.+)", content)
        if not match:
            return "❌ No H1 title found."
        original = match.group(1)
        suggestion = original.title().replace("And", "and").replace("Of", "of")  # Toy example
        return f"💡 Suggested title: {suggestion}"
