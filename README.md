# Research Agent

A command-line research assistant that combines local LLM conversation with a small multi-agent research pipeline. The app chats normally, and when the user asks to research a topic it searches the web, summarizes findings, checks the summary, and formats citations into a report.

## Features

- Conversational CLI interface
- Local LLM calls through Ollama
- Research trigger routing via `ConversationManager`
- DuckDuckGo web search helper
- Summarization, fact-checking, and citation agents
- Formatted research report output

## Project Structure

```text
.
├── main.py                     # CLI entry point
├── conversation_manager.py     # Chat loop, tool-call parsing, research routing
├── orchestrator.py             # Coordinates the research pipeline
├── Agents/
│   ├── base_agent.py           # Shared Ollama chat helper and tool-call parsing
│   ├── search_agent.py         # Builds/searches research queries
│   ├── summariser_agent.py     # Produces concise summaries
│   ├── fact_checker_agent.py   # Reviews summaries for unsupported claims
│   └── citation_agent.py       # Formats source citations
└── Tools/
    ├── web_search.py           # DuckDuckGo search helper
    ├── summariser.py           # Lightweight extractive summarizer
    └── citation.py             # Basic APA-style citation formatter
```

## Requirements

- Python 3.10+
- Ollama installed and running locally
- The `llama3` model pulled in Ollama
- Python package:
  - `requests`

## Setup

Install Python dependencies:

```bash
pip install requests
```

Start Ollama:

```bash
ollama serve
```

Pull the default model if needed:

```bash
ollama pull llama3
```

The model name is configured in `conversation_manager.py` and `Agents/base_agent.py`:

```python
MODEL = 'llama3'
```

Change that value if you want to use a smaller or different local model.

## Usage

Run the assistant:

```bash
python main.py
```

You can chat normally:

```text
You: hello
```

To trigger the research pipeline, ask for research explicitly:

```text
You: research renewable energy storage trends
```

Exit with:

```text
quit
```

## How It Works

1. `main.py` starts a terminal chat loop.
2. `ConversationManager` sends user input to the local Ollama model.
3. If the model returns a `run_research` tool call, the manager passes the topic to `ResearchOrchestrator`.
4. `ResearchOrchestrator` runs:
   - `SearchAgent`
   - `SummariserAgent`
   - `FactCheckerAgent`
   - `CitationAgent`
5. The compiled report is sent back through the conversation manager for a final assistant response.

## Known Issues

- Some agent methods currently treat `_chat()` as if it returns a full Ollama response object, but `BaseAgent._chat()` returns only the message content string. Those methods may need to parse the returned string directly.
- Package directories are named `Agents` and `Tools`, while imports use lowercase `agents` and `tools`. This may work on case-insensitive filesystems like Windows, but can fail on case-sensitive systems.
- `Agents/_init_.py` and `Tools/_init_.py` are named with one underscore on each side. Python package initializers are normally named `__init__.py`.

## Notes

This is a local-first prototype. It depends on Ollama for LLM responses and DuckDuckGo's public instant-answer endpoint for search results, so research quality and coverage can vary by topic.
