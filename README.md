# palm-tree
Agentic Blog Draft System

This is basically an attempt at "vibe coding" an agentic system that talks with me on Discord about updating my blog and cross-posting to LinkedIn whenever I have an interesting chat with ChatGPT.

## Installation

Each component has its own `requirements.txt` so you only install what you need. For example, to install dependencies for the `publishing` tools only:

```bash
pip install -r publishing/requirements.txt
```

The root `requirements.txt` aggregates all component files for development convenience.

## Development notes

`llama_agent.handle_pr_request` first builds a `VectorStoreIndex` from the PR
contents. After the index is ready, the GitHub-focused tools are instantiated.
These tools don't consume the index directly but operate on the pull request via
the GitHub API. The index simply provides context for the language model during
the agent run.

