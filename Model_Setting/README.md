# ModelSettings - Complete Guide

The `ModelSettings` class in the OpenAI Agents library allows you to configure various parameters that control how your language model behaves. This guide covers all available attributes and their effects.

## Import

```python
from agents import ModelSettings
```

## Basic Usage

```python
model_settings = ModelSettings(
    temperature=0.7,
    max_tokens=1000,
    tool_choice="auto"
)
```

## All Available Attributes

### 1. `temperature` (float)
**Range:** 0.0 to 2.0  
**Default:** 1.0  
**Description:** Controls the randomness of the model's responses.

- **0.0**: Very deterministic, consistent responses
- **0.5**: Balanced creativity and consistency  
- **1.0**: Default randomness
- **1.5+**: More creative, varied responses

```python
# Conservative, factual responses
ModelSettings(temperature=0.2)

# Creative writing
ModelSettings(temperature=1.5)
```

### 2. `max_tokens` (int)
**Range:** 1 to model maximum  
**Default:** Model default  
**Description:** Maximum number of tokens the model can generate in response.

```python
# Short, concise responses
ModelSettings(max_tokens=100)

# Long, detailed responses
ModelSettings(max_tokens=4000)
```

### 3. `tool_choice` (str)
**Values:** `"auto"`, `"none"`, `"required"`  
**Default:** `"auto"`  
**Description:** Controls when and how the model uses tools.

- **`"auto"`**: Model decides whether to use tools
- **`"none"`**: Model cannot use tools
- **`"required"`**: Model must use at least one tool

```python
# Let model decide about tools
ModelSettings(tool_choice="auto")

# Force tool usage
ModelSettings(tool_choice="required")

# Disable tools
ModelSettings(tool_choice="none")
```

### 4. `parallel_tool_calls` (bool)
**Values:** `True`, `False`  
**Default:** `False`  
**Description:** Whether the model can call multiple tools simultaneously.

⚠️ **Note:** Not supported by all models (e.g., Gemini API doesn't support this)

```python
# Sequential tool calls (safer)
ModelSettings(parallel_tool_calls=False)

# Parallel tool calls (faster, but not widely supported)
ModelSettings(parallel_tool_calls=True)
```

### 5. `frequency_penalty` (float)
**Range:** 0.0 to 2.0  
**Default:** 0.0  
**Description:** Reduces repetition of the same tokens/phrases.

- **0.0**: No penalty for repetition
- **0.5**: Moderate penalty
- **1.0+**: Strong penalty against repetition

```python
# Allow repetition (good for technical content)
ModelSettings(frequency_penalty=0.0)

# Reduce repetition (good for creative writing)
ModelSettings(frequency_penalty=0.8)
```

### 6. `presence_penalty` (float)
**Range:** 0.0 to 2.0  
**Default:** 0.0  
**Description:** Penalizes tokens based on their presence in the conversation history.It is not used with gemnini-2.5 models

- **0.0**: No penalty
- **0.5**: Moderate penalty for repeated topics
- **1.0+**: Strong penalty for repeated topics

```python
# Allow topic repetition
ModelSettings(presence_penalty=0.0)

# Encourage new topics
ModelSettings(presence_penalty=0.6)
```

### 7. `top_p` (float)
**Range:** 0.0 to 1.0  
**Default:** 1.0  
**Description:** Controls diversity via nucleus sampling.

- **1.0**: No filtering (default)
- **0.9**: High diversity
- **0.5**: Moderate diversity
- **0.1**: Low diversity

```python
# High diversity responses
ModelSettings(top_p=0.9)

# Focused, consistent responses
ModelSettings(top_p=0.3)
```

### 8. `truncation` (str)
**Values:** `"auto"`, `"none"`  
**Default:** `"none"`  
**Description:** Controls how input text is truncated when it exceeds model limits.

- **`"auto"`**: Automatically truncate long inputs
- **`"none"`**: Don't truncate (may cause errors if input is too long)

```python
# Auto-truncate long inputs
ModelSettings(truncation="auto")

# Don't truncate (use with caution)
ModelSettings(truncation="none")
```

## Common Use Cases

### 1. Factual Assistant
```python
ModelSettings(
    temperature=0.2,
    max_tokens=1000,
    tool_choice="auto",
    frequency_penalty=0.0
)
```

### 2. Creative Writer
```python
ModelSettings(
    temperature=1.5,
    max_tokens=2000,
    frequency_penalty=0.8,
    presence_penalty=0.3
)
```

### 3. Tool-Heavy Agent
```python
ModelSettings(
    temperature=0.7,
    tool_choice="required",
    parallel_tool_calls=False  # For compatibility
)
```

### 4. Code Generator
```python
ModelSettings(
    temperature=0.3,
    max_tokens=4000,
    frequency_penalty=0.0,  # Allow repeated code patterns
    tool_choice="auto"
)
```

## Best Practices

1. **Start Conservative**: Begin with low temperature (0.2-0.5) for factual tasks
2. **Test Tool Settings**: Verify `tool_choice` and `parallel_tool_calls` work with your model
3. **Monitor Token Usage**: Set appropriate `max_tokens` to control costs
4. **Balance Penalties**: Use `frequency_penalty` and `presence_penalty` together for optimal diversity
5. **Model Compatibility**: Check your model's documentation for supported parameters

## Example Implementation

```python
from agents import Agent, ModelSettings

# Create an agent with specific model settings
agent = Agent(
    name="Smart Assistant",
    instructions="You are a helpful assistant that provides accurate information.",
    model="gemini-2.0-flash",
    model_settings=ModelSettings(
        temperature=0.3,
        max_tokens=1500,
        tool_choice="auto",
        frequency_penalty=0.2,
        presence_penalty=0.1
    )
)
```

## Troubleshooting

### Common Issues:
- **"Parallel tool calls not supported"**: Set `parallel_tool_calls=False`
- **"Model not found"**: Check your model name and API configuration
- **"Token limit exceeded"**: Reduce `max_tokens` or use `truncation="auto"`

### Model-Specific Notes:
- **Gemini Models**: Don't support `parallel_tool_calls=True`
- **OpenAI Models**: Support all parameters
- **Custom Models**: Check provider documentation for supported parameters 