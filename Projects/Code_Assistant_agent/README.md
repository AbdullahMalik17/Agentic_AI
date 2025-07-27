# Multi-Agent Development Assistant Platform

## Project Overview
A sophisticated AI-powered development platform that utilizes three specialized agents to provide expert guidance and assistance in software development. Each agent is designed to handle specific domains of expertise while working together seamlessly.

## Agent Architecture

### 1. Web Developer Agent
- **Expertise**: Full-stack web development
- **Capabilities**:
  - HTML, CSS, JavaScript guidance
  - Front-end framework consulting (React, Angular, Vue)
  - Back-end development support (Node.js, Python, databases)
  - Code examples and best practices
  - Project structure recommendations

### 2. Mobile App Developer Agent
- **Expertise**: Mobile application development
- **Capabilities**:
  - iOS and Android development guidance
  - Cross-platform framework support (React Native, Flutter)
  - Mobile UI/UX best practices
  - App deployment and publishing assistance
  - Performance optimization tips

### 3. Agentic AI Developer Agent
- **Expertise**: AI agent development and integration
- **Capabilities**:
  - Multi-agent system design
  - AI integration strategies
  - LLM implementation guidance
  - Agent communication protocols
  - Tool integration support

## Features
- **Smart Routing**: Automatically directs queries to the most appropriate agent
- **Integrated Tools**:
  - DevOps support for deployment guidance
  - OpenAI integration for enhanced responses
- **Interactive Interface**: Built with Chainlit for smooth user interaction
- **Context Awareness**: Maintains conversation context across agent handoffs
- **Code Generation**: Provides practical code examples and solutions

## Technical Stack
- **Language**: Python 3.13+
- **Framework**: Chainlit
- **AI Model**: Gemini 2.0
- **Key Libraries**:
  - OpenAI Agents SDK
  - AsyncOpenAI
  - Python-dotenv

## Setup and Installation
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
5. Run the application:
   ```bash
   chainlit run main.py
   ```

## Usage Examples
```python
# Ask about web development
"How do I create a responsive navigation bar?"

# Get mobile app guidance
"What's the best way to implement push notifications in React Native?"

# Learn about AI agent development
"How can I create a multi-agent system with tool integration?"
```

## Project Structure
```
Code_Assistant_agent/
├── main.py              # Main application file
├── system_prompt.py     # Agent prompts and instructions
├── .env                 # Environment variables
└── README.md           # Documentation
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
MIT License - feel free to use and modify as needed.

## Contact
- Author: Abdullah Malik
- GitHub: [@AbdullahMalik17](https://github.com/AbdullahMalik17)
