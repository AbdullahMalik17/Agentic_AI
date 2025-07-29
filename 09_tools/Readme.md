# Tools in OpenAI SDK
Tools let agents take actions: things like fetching data, running code, calling external APIs, and even using a computer. There are three classes of tools in the Agent SDK:

1. `Hosted tools`: these run on LLM servers alongside the AI models. OpenAI offers retrieval, web search and computer use as hosted tools.
2. `Function calling`: these allow you to use any Python function as a tool.
3. `Agents as tools`: this allows you to use an agent as a tool, allowing Agents to call other agents without handing off to them.

For more details, see the [OpenAI API documentation](https://openai.github.io/openai-agents-python/tools/).