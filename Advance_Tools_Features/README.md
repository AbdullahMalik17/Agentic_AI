# Tool Use Behavior in OpenAI SDK Agent Module

This project demonstrates advanced tool use behavior configuration in OpenAI SDK's agent module, showing how to control and customize how agents interact with tools.

## Overview

Tool use behavior defines how an agent handles tool execution during its decision-making process. This implementation showcases the use of `StopAtTools` behavior, which allows fine-grained control over the agent's tool execution flow.

## Key Components

### 1. Agent Configuration

```python
    tool_use_behavior=StopAtTools(stop_at_tool_names=["get_travel_plan"])
```


### 3. Tool Use Behavior Control

The implementation uses `StopAtTools` behavior which:
- Allows specifying which tools should pause the execution loop
- Provides control over the agent's decision-making process
- Enables human intervention when needed

## Flow Control Patterns

The agent's execution can follow different patterns:

1. **NLP Answer**: 
   - Loop completes when a natural language response is generated
   - No tool intervention needed

2. **Tool Call**:
   - Loop continues if regular tool is called
   - Loop pauses if specified in `stop_at_tool_names`
   - Allows for human verification or intervention

## Usage Example

```python
# Regular weather query - completes normally
result = Runner.run_sync(base_agent, "What is weather in Lahore")

# Travel plan query - pauses for verification
result = Runner.run_sync(base_agent, "Make me travel plan for Lahore")
```

## Model Configuration

The implementation supports different LLM services and models:
- Configurable API endpoints
- Custom model selection
- Extensible client implementation

## Benefits

- Fine-grained control over tool execution
- Support for human-in-the-loop scenarios
- Flexible model and service configuration
- Clear separation of concerns between tools and behavior

This implementation demonstrates advanced control over agent behavior, making it suitable for applications requiring careful tool execution management and human oversight.
