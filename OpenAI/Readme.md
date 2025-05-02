# Two types of Api in Open Ai
- Chat Completion API 
- Response API

## 1. Chat Completion API
The Chat Completion API enables interactive conversations with AI models while maintaining context. Key features:
- Stateless architecture
- Conversational history support
- Real-time responses
- Multiple model support (GPT-3.5, GPT-4)

## 2. Response API
The Response API provides more sophisticated control over AI interactions. Features include:
- Stateful processing
- Advanced programming capabilities
- Flexible response formatting
- Custom parameter control

## Usage Example
```python
import openai

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)


## Documentation Links
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Chat Completion Guide](https://platform.openai.com/docs/guides/chat)
- [Response API Reference](https://platform.openai.com/docs/api-reference)