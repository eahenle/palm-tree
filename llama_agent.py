# llama_agent.py
import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, ServiceContext
from llama_index.agent import OpenAIAgentWorker, AgentRunner
from llama_index.llms import OpenAI
from github_utils import get_pr_diff_and_comments, save_pr_to_local

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

from agent_tools import FixPostTool, SuggestTitleTool

# Add these after index creation
tools = [
    FixPostTool(pr_number),
    SuggestTitleTool(),
]

agent = AgentRunner.from_tools(
    tools=tools,
    llm=llm,
    system_prompt="You are a markdown blog post editing assistant...",
    context_retriever=index.as_retriever()
)


def handle_pr_request(pr_number: int) -> str:
    # 1. Retrieve PR content from GitHub
    diff_text, comments = get_pr_diff_and_comments(pr_number)

    # 2. Persist locally for indexing
    pr_path = save_pr_to_local(pr_number, diff_text, comments)

    # 3. Load into LlamaIndex
    reader = SimpleDirectoryReader(pr_path)
    docs = reader.load_data()
    index = VectorStoreIndex.from_documents(docs)

    # 4. Create AgentWorkflow
    llm = OpenAI(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
    service_context = ServiceContext.from_defaults(llm=llm)
    agent = AgentRunner.from_tools(
        tools=[],
        llm=llm,
        system_prompt="You are a code review assistant for markdown blog posts. Review the proposed edits and suggest improvements.",
        context_retriever=index.as_retriever()
    )

    # 5. Run it
    return agent.chat("Please review this pull request and suggest improvements.").response
