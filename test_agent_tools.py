from agentic_blog_bot.agent_tools import SuggestTitleTool

def test_title_suggestion():
    tool = SuggestTitleTool()
    content = "# this is a blog post\n\nmore text"
    result = tool(content)
    assert "This Is a Blog Post" in result
