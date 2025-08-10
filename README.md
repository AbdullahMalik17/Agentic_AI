## Agentic AI Monorepo

This repository contains multiple, focused examples and mini-projects for building Agentic AI apps with Chainlit and the OpenAI Agents SDK. Each subproject is self-contained and runnable with `uv`.

### Prerequisites
- Python 3.13+
- uv (Rust-based Python package manager) — install from `https://astral.sh/uv`
- Optional: Playwright browsers for the computer-use demo

### Environment variables (.env)
Create a `.env` file at the repo root or in each project folder that needs it:

```
GEMINI_API_KEY=your_gemini_key_here
TAVILY_API_KEY=your_tavily_key_here
```

Notes:
- Gemini models are accessed via the OpenAI-compatible Gemini endpoint in these projects.
- Tavily is used for web search in relevant demos.

### How to run projects
Use `uv run` so dependencies from each project's `pyproject.toml` and `uv.lock` are resolved automatically. Always run commands from the project folder unless stated otherwise.

#### 1) Web Search Agent (Chainlit)
- Folder: `_Projects/Web_Search_Agent`
- Features: tool calling (Tavily web search), context-aware `get_info` tool, streaming responses

Commands:
```
cd _Projects/Web_Search_Agent
uv run chainlit run main.py --watch
```

#### 2) Multi-Agent Code Assistant (Chainlit)
- Folder: `_Projects/Code_Assistant_agent`
- Features: triage + expert agents (Web, Mobile, Agentic AI), agents-as-tools, Tavily search tool

Commands:
```
cd _Projects/Code_Assistant_agent
uv run chainlit run main.py --watch
```

#### 3) Function Calling (Chainlit)
- Folder: `07_Function_Calling`
- Features: simple function tools with streaming output

Commands:
```
cd 07_Function_Calling
uv run chainlit run main.py --watch
```

#### 4) Model Context (Console)
- Folder: `Model_Context`
- Features: `RunContextWrapper[T]` pattern for passing local context to tools

Commands:
```
cd Model_Context
uv run python main.py
```

#### 5) Streaming Demo (Console)
- Folder: `Model_configuration/05_Streaming`
- Features: token streaming via `ResponseTextDeltaEvent`

Commands:
```
cd Model_configuration/05_Streaming
uv run python main.py
```

#### 6) Tavily Search Tool (Chainlit)
- Folder: `09_tools/web_search_tool_in_tavily`
- Features: direct Tavily integration and formatted result rendering

Commands:
```
cd 09_tools/web_search_tool_in_tavily
uv run chainlit run main.py --watch
```

#### 7) Computer Use Tool (Console + local browser)
- Folder: `09_tools/computer_tools`
- Features: local Playwright-driven browser automation via `ComputerTool`

First-time setup:
```
cd 09_tools/computer_tools
uv add playwright
python -m playwright install
```

Run:
```
uv run python main.py
```

#### 8) Chainlit Starter (Chainlit)
- Folder: `02_chailit`

Commands:
```
cd 02_chailit
uv run chainlit run app.py --watch
```

#### 9) MCP Notes (Console)
- Folder: `08_MCP`

Commands:
```
cd 08_MCP
uv run python main.py
```

### Troubleshooting
- Cannot instantiate typing.Union: Ensure tool signatures use `RunContextWrapper[T]` and access data via `Wrapper.context` (not `Wrapper.data`). Avoid conflicting names like `from multiprocessing import context`.
- Tools not called: Verify `Agent(..., tools=[...])` is a list (no trailing commas creating tuples). If using Chainlit, restart the server after code changes.
- Tavily errors: Check `TAVILY_API_KEY` and network connectivity.
- Gemini model errors: Confirm `GEMINI_API_KEY` and model name (e.g., `gemini-2.5-flash`).

### Repo notes
- Each folder contains its own `pyproject.toml` and `uv.lock`. Running with `uv run` inside that folder will install and use the correct dependencies.
- Chainlit apps can be accessed in the browser at the URL printed in the terminal after startup.

# Working of LLM 
Two things are sent to LLM . One thing is System Instruction and another is Tool Call 

### License and Contact
- License: MIT
- Author: Abdullah Malik
- GitHub: @AbdullahMalik17
        