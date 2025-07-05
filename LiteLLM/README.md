# LiteLLM

**LiteLLM** is an open-source Python library that provides a unified API for interacting with multiple large language model (LLM) providers, including OpenAI, Azure, Anthropic, Cohere, and others. It allows developers to switch between different LLM backends with minimal code changes, making it easier to experiment with and deploy various models.

## Key Features

- Unified API for multiple LLM providers (OpenAI, Azure, Anthropic, etc.)
- Simple interface for chat, completion, and embedding endpoints
- Easy model switching and provider fallback
- Supports both cloud and self-hosted models

## Example Usage

```python
from litellm import completion

response = completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, world!"}]
)
print(response['choices'][0]['message']['content'])
```

## Use Cases

- Rapid prototyping with different LLMs
- Cost and latency optimization by switching providers
- Building robust AI applications with provider fallback

## Resources

- [LiteLLM GitHub Repository](https://github.com/BerriAI/litellm)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
