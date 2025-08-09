## Web Search Agent

A production-ready Chainlit agent demonstrating tool use and streaming with the OpenAI Agents SDK.

### What it does
- Uses Tavily to fetch fresh, real-time web results
- Exposes a custom `get_info` tool that reads a typed user profile from local run context
- Streams model output token-by-token for responsive UX

### Tech stack
- Chainlit UI
- OpenAI Agents SDK (function tools, runners, model settings)
- Gemini via OpenAI-compatible endpoint (`gemini-2.5-flash`)
- Tavily Search API

### Requirements
- Python 3.13+
- uv
- Environment variables in `.env`:
```
GEMINI_API_KEY=your_gemini_key_here
TAVILY_API_KEY=your_tavily_key_here
```

### Install & Run
```
cd _Projects/Web_Search_Agent
uv run chainlit run main.py --watch
```
Open the URL printed by Chainlit in your terminal.

### Project structure
```
_Projects/Web_Search_Agent/
├─ main.py           # Agent, tools, streaming
├─ pyproject.toml    # Dependencies (chainlit, openai-agents, tavily-python, dotenv)
├─ chainlit.md       # Welcome screen
└─ README.md         # This file
```

### How it works
- Tools are defined with `@function_tool`.
- The agent registers: `tools=[web_search, get_info]`.
- Local context is passed as a dataclass instance: `Runner.run_streamed(..., context=Info(...))`.
- Inside tools, access context via `Wrapper.context` (type-safe with `RunContextWrapper[Info]`).
- Responses are streamed using `Runner.run_streamed(...).stream_events()`.

### Usage examples
- “Search the latest news about AI regulation and summarize key points.”
- “What is my profile info?” (invokes `get_info` and returns values from `Info`)

### Configuration tips
- Model: adjust `model="gemini-2.5-flash"` in `main.py` as needed.
- Tool choice: `ModelSettings(tool_choice="auto")` lets the model decide when to use tools.
- Temperature: increase for creativity, decrease for factual responses.

### Security & privacy
- API keys are read from `.env`; never hardcode credentials.
- `get_info` uses local run context; that data is not sent to the LLM unless surfaced in tool output.
- Avoid putting PII in prompts; keep sensitive data in local context when possible.

### Troubleshooting
- Cannot instantiate typing.Union: Ensure tool signatures use `RunContextWrapper[T]` and read via `Wrapper.context`. Avoid `from multiprocessing import context`.
- Tools not called: Confirm `Agent(..., tools=[web_search, get_info])` is a list (no trailing comma creating a tuple). Restart Chainlit after changes.
- Tavily errors: Set `TAVILY_API_KEY` and ensure network access.
- Gemini errors: Verify `GEMINI_API_KEY` and model name.

### License
MIT — use and modify as needed.

### Author
Abdullah Malik — `@AbdullahMalik17`