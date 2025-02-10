# JARVIS AI System

JARVIS is a comprehensive AI assistant system with advanced memory management, task planning, and multimodal capabilities. It's designed to be modular, scalable, and easily extensible.

## Features

- **Memory Management**: Multi-tiered memory system with short-term (Redis), mid-term (ChromaDB), and long-term (PostgreSQL) storage
- **Personality System**: Adaptive personality with emotional state tracking and relationship memory
- **Task Planning**: Advanced task decomposition and execution planning using LangChain
- **Multi-modal Support**: Handles text, speech, and potentially other forms of input/output
- **Self-improvement**: Capability to analyze and evolve its own codebase
- **Security**: Sandboxed execution environment with comprehensive security measures

## System Requirements

- Python 3.8 or higher
- Redis
- PostgreSQL
- OpenAI API key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jarvis-ai.git
   cd jarvis-ai
   ```

2. Run the setup script:
   ```bash
   python setup.py
   ```

3. Update the `.env` file with your OpenAI API key and other configurations

4. Review and adjust `config/config.yaml` as needed

## Usage

Start the JARVIS system:
```bash
python -m jarvis
```

The system will start and expose an API endpoint for interaction.

Example interaction:
```python
import requests

# Send a request to JARVIS
response = requests.post("http://localhost:8000/interact", 
                        json={"text": "What's the weather like today?"})
print(response.json())
```

## Architecture

### Core Components

1. **MemoryCore**
   - Manages different tiers of memory
   - Handles memory consolidation and retrieval
   - Implements semantic search capabilities

2. **PersonaEngine**
   - Manages personality traits and emotional states
   - Tracks user relationships and preferences
   - Adapts behavior based on context

3. **TaskManager**
   - Handles task decomposition and planning
   - Manages execution flow and dependencies
   - Provides reflection and improvement capabilities

4. **SystemCore**
   - Manages system security and access control
   - Handles command execution in sandbox
   - Provides logging and monitoring

### Modules

1. **InputOutputManager**
   - Handles different types of input/output
   - Manages speech-to-text and text-to-speech
   - Provides format conversion utilities

2. **Scheduler**
   - Manages task timing and scheduling
   - Handles conflicts and priorities
   - Provides timezone awareness

3. **CodeEvolver**
   - Analyzes and improves system code
   - Manages version control integration
   - Provides safe testing environment

### Data Flow

```
Input → IO Manager → Task Manager → Memory Core ↔ Persona Engine → Output
                          ↓
                    System Core
```

## Configuration

The system can be configured through:
1. `.env` file for environment variables
2. `config/config.yaml` for system configuration
3. Runtime API for dynamic adjustments

## Security Considerations

- All commands are executed in a sandboxed environment
- Input validation at all entry points
- Rate limiting for resource-intensive operations
- Secure storage for sensitive data
- Regular security audits

## Development

### Adding New Capabilities

1. Create a new module in the `modules` directory
2. Implement the required interfaces
3. Register the module in `__main__.py`
4. Update configuration as needed

### Testing

Run the test suite:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details