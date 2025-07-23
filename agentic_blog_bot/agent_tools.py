import re

class SuggestTitleTool:
    """Simple tool to suggest a title capitalization."""
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
