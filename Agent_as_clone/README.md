## Cloning Agents with the OpenAI Agents SDK

This example shows how to clone agents using the OpenAI Agents SDK, create lightweight variants, and when to use shallow vs deep copies of configuration.

### What is agent cloning?
Cloning creates a new `Agent` from an existing one with selected changes (name, instructions, model, tools, etc.). It’s ideal for creating specialized variants without re-specifying shared configuration.

```startLine:36:endLine:48:Agent_as_clone/main.py
agent: Agent = Agent(
    name="Math Expert Agent",
    instructions="You are a math expert agent. You can solve any math problem and explain the solution step by step in an easy manner.",
    model=model,
    tools=[subtract],
)

agent2: Agent = agent.clone(
    name="Math Expert Agent 2",
    instructions="You only give a simple response to the math problem without any explanation.",
    model=OpenAIChatCompletionsModel(model="gemini-1.5-flash", openai_client=client),
    tools=[add],
)
```

### What this project demonstrates
- **Base agent** with one tool (`subtract`) and a Gemini chat-completions model via OpenAI-compatible endpoint.
- **Cloned agent** with different name, instructions, model, and tool (`add`).
- **Synchronous run** of both to compare outputs on the same prompt.


You should see outputs from the original and cloned agents printed separately.

## Shallow vs Deep Copy with Agents

### Shallow clone (recommended default)
Use `Agent.clone(...)` to make a new agent that reuses most configuration but changes only what you specify (e.g., `name`, `instructions`, `model`, `tools`). This is typically all you need.

From the SDK docs, `clone()` duplicates an agent and applies your overrides. It’s conceptually a shallow copy of the agent’s configuration, not a full object graph duplication.

### Ensuring independent lists/dicts (shallow copy of containers)
If you plan to mutate container fields (like `tools`), pass a new container to avoid accidental shared references:

```python
agent_variant = agent.clone(
    tools=[*agent.tools],  # new list instance
)
```

Because tools are typically functions (immutable), sharing them is safe. Creating a new list is useful if you plan to append/remove tools without affecting the original.

### Deep copy nested configuration (targeted)
If you need full isolation of nested, mutable config (e.g., model settings), make a deep copy of those specific objects and pass them to `clone()`:

```python
import copy

deep_settings = copy.deepcopy(getattr(agent, "model_settings", None))
agent_isolated = agent.clone(model_settings=deep_settings)
```

If the SDK uses Pydantic models for settings, prefer their built-in deep copy when available (e.g., `model_copy(deep=True)`):

```python
deep_settings = agent.model_settings.model_copy(deep=True)
agent_isolated = agent.clone(model_settings=deep_settings)
```

### What not to deep copy
- Live clients, sessions, event loops, or I/O handles. Instead, construct new clients explicitly when needed and pass them in your overrides.

```startLine:16:endLine:24:Agent_as_clone/main.py
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-pro",
    openai_client=client,
)
```

To isolate models or clients, create a new `openai_client` or `model` instance and pass it to `clone()` rather than deep copying existing ones.

## Practical recipes

### 1) Variant with a different tool
```python
agent_tools_variant = agent.clone(tools=[add])
```

### 2) Variant with fully isolated model settings
```python
import copy

isolated_settings = copy.deepcopy(getattr(agent, "model_settings", None))
agent_isolated = agent.clone(model_settings=isolated_settings)
```

### 3) Variant with a new client and model
```python
new_client = AsyncOpenAI(api_key=os.environ["GEMINI_API_KEY"], base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
new_model = OpenAIChatCompletionsModel(model="gemini-1.5-flash", openai_client=new_client)
agent_new_model = agent.clone(model=new_model)
```

## Troubleshooting
- Missing key errors: ensure `.env` contains `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) and `OPENAI_API_KEY` and that it’s loaded.
- `ModuleNotFoundError: agents`: install `openai-agents` and `openai` as shown above.
- Python version issues: this project targets Python 3.13. If you use another version, adjust your environment or update `pyproject.toml` accordingly.

## References
- OpenAI Agents SDK docs: see “Agents” and “Cloning/copying agents”.

