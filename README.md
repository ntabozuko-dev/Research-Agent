# Research Agent

[![tests](https://github.com/ntabozuko-dev/Research-Agent/actions/workflows/tests.yml/badge.svg)](https://github.com/ntabozuko-dev/Research-Agent/actions/workflows/tests.yml)

A local-first, command-line research assistant. It chats normally through a local LLM (Ollama); when you ask it to research a topic, the LLM emits a **tool call** that hands the request to a small multi-agent pipeline which searches the web, summarises, fact-checks and cites, then returns a report.

## Features

- Conversational CLI
- LLM inference runs locally through [Ollama](https://ollama.com) (no cloud LLM API or key)
- LLM-driven routing: the model decides when to call the `run_research` tool (JSON tool calls, tolerant of code-fenced output)
- Four cooperating agents run by an orchestrator: search, summarise, fact-check, cite
- Clear, actionable errors (Ollama not running, model not pulled, timeouts) instead of silent failures
- Unit-tested, with CI on Linux (Python 3.10 and 3.12)

## How it works

```text
You ──► ConversationManager ──► Ollama (llama3)
              │  model replies {"tool": "run_research", "args": {"topic": "..."}}
              ▼
        ResearchOrchestrator
          1. SearchAgent       LLM writes the query ► DuckDuckGo search
          2. SummariserAgent   extractive tool + LLM rewrites as bullet points
          3. FactCheckerAgent  LLM flags unsupported or doubtful statements
          4. CitationAgent     APA-style references for each source
              ▼
        report ──► back through the model ──► reply to you
```

## Project structure

```text
.
├── main.py                  # CLI entry point
├── conversation_manager.py  # Chat loop, tool-call routing, history
├── orchestrator.py          # Runs the research pipeline, compiles the report
├── llm.py                   # The only module that talks to Ollama (MODEL / URL live here)
├── tool_parsing.py          # Parses JSON tool calls from model output
├── agents/                  # BaseAgent + search, summariser, fact-checker, citation agents
├── tools/                   # web_search, extractive summariser, citation formatter
├── tests/                   # pytest suite (all network/LLM calls mocked)
└── .github/workflows/       # CI
```

## Setup

Requires Python 3.10+ and [Ollama](https://ollama.com).

```bash
pip install -r requirements.txt

ollama serve            # in one terminal
ollama pull llama3      # once
```

To use a smaller or different model, change `MODEL` in `llm.py`.

## Usage

```bash
python main.py
```

```text
You: hello
You: research renewable energy storage trends
You: quit
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

No Ollama or internet connection is needed: the LLM and search calls are mocked.

## Limitations

This is a prototype, and its limits are worth knowing:

- **Search coverage varies.** It uses DuckDuckGo's free Instant Answer API, which returns related topics and abstracts rather than full web results. Broad or niche queries can come back empty ("No results found").
- **Summaries are built from search snippets**, not from the full text of the pages.
- **Fact-checking is LLM self-review**, not verification against sources. Treat it as a sanity check.
- **Citations are basic.** Search results carry no author or date, so references use "(n.d.)".
- **Quality depends on the local model.** Smaller models follow the tool-call format less reliably.
