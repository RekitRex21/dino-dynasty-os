# Dino Dynasty OS: Foundation

A standalone AI operating system written in Python. Built for speed, security, and extensibility.

## 🚀 Quick Start

```bash
# Setup virtual environment
cd dino_dynasty_os
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run CLI
python cli.py run hello
python cli.py list
python cli.py status

# OR run the interactive dashboard (recommended!)
python dashboard.py
```

## 🎨 Interactive Dashboard

```bash
# Start the TUI dashboard
python dashboard.py

# Features:
# - 📊 Show Status
# - 🎯 List Agents
# - ▶️ Run Agent
# - 🔨 BUILD Agent (full dev access)
# - 📋 PLAN Agent (read-only analysis)
# - 🧠 Memory Manager
```

## ✨ New Features

### Multi-Provider Fallback
Dino Dynasty OS now supports multiple LLM providers with automatic fallback. Configure providers in `config.yaml` and the system tries each one in order until success.

```yaml
llm:
  providers:
    - name: "vl_local"
      provider: "vl"
      model: "llama-3.1-8b"
      base_url: "http://localhost:8000/v1"
      enabled: true
    - name: "ollama"
      provider: "ollama"
      model: "phi4-mini"
      enabled: true
    - name: "minimax"
      provider: "minimax"
      model: "MiniMax-M2.5"
      enabled: true
```

### vLLM Local Model Support
Run local LLMs via vLLM server (localhost:8000). Fast, private inference with OpenAI-compatible API.

```yaml
- name: "vl_local"
  provider: "vl"
  model: "llama-3.1-8b"
  base_url: "http://localhost:8000/v1"
```

### Workspace Sandbox
Restrict file operations to your workspace directory for security.

```yaml
sandbox:
  enabled: true
  restrictToWorkspace: true
  workspace_path: "."
```

### Channel Plugins
Multi-platform messaging support (Telegram, Discord, WhatsApp stubs included).

```yaml
channels:
  enabled: true
  telegram:
    enabled: false
    bot_token: ""
  discord:
    enabled: false
    bot_token: ""
  whatsapp:
    enabled: false
```

---

## 🦖 What is Dino Dynasty OS?

Dino Dynasty OS is a standalone AI operating system inspired by the NanoBot/MCP architecture. It provides:

- **Agent Core** - Run intelligent agents with LLM integration
- **Memory Layer** - Persistent, semantic memory with SQLite
- **Scheduler** - Cron-style job scheduling
- **Tool Sandbox** - Isolated, secure tool execution
- **Message Bus** - Pub/sub messaging between agents
- **Security Gateway** - API key management and permissions

## 📁 Project Structure

```
dino_dynasty_os/
├── dino_os/                 # Main package
│   ├── __init__.py         # Package initialization
│   ├── agent_core.py       # Agent runner and LLM integration
│   ├── config.py           # YAML configuration management
│   ├── memory_layer.py     # SQLite-backed semantic memory
│   ├── message_bus.py      # Inter-agent pub/sub messaging
│   ├── scheduler.py        # Cron-style job scheduler
│   ├── security_gateway.py # API keys and permissions
│   └── tool_sandbox.py     # Isolated tool execution
├── skills/                  # Agent skills and tools
├── tests/                   # Test suite
├── cli.py                   # CLI entry point
├── config.yaml              # System configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🧠 Agent System

### Creating Your First Agent

```python
# skills/hello.py
from dino_os import skill

@skill
def hello_agent(name: str = "World") -> str:
    """A simple greeting agent."""
    return f"Roar! Hello, {name}! 🦖"
```

### Running Agents

```bash
# Run with default parameters
python cli.py run hello

# Run with custom parameters
python cli.py run hello --params '{"name": "Rex"}'

# List all available agents
python cli.py list
```

### Agent Structure

Agents in Dino Dynasty OS are Python functions decorated with `@skill`. They can:

- Accept typed parameters
- Return strings or structured data
- Access memory layer
- Call other tools securely
- Participate in message bus

## 💾 Memory Layer

### SQLite-Backed Persistent Memory

The memory layer provides persistent, semantic memory storage:

```python
from dino_os.memory_layer import MemoryLayer

memory = MemoryLayer()

# Store a memory
memory.add("user_preference", "likes_crypto_trading")

# Retrieve by key
result = memory.get("user_preference")

# Search semantically
results = memory.search("trading preferences")

# List all keys
keys = memory.list()
```

### Semantic Search

The memory layer supports semantic search using embeddings:

```python
# Store with embedding
memory.add("important_trade", "BTC buy at 45000", embed=True)

# Search by meaning
results = memory.search("bitcoin purchase")
```

## ⏰ Scheduler

Run jobs on schedules:

```python
from dino_os.scheduler import Scheduler

scheduler = Scheduler()

# Add a job
scheduler.add_job(
    name="daily_report",
    func=generate_report,
    trigger="cron",
    hour=9,
    minute=0
)

# Start the scheduler
scheduler.start()
```

### Trigger Types

- **cron**: Traditional cron syntax
- **interval**: Fixed interval
- **date**: One-time execution

## 🔧 Tool Sandbox

Execute tools in isolation:

```python
from dino_os.tool_sandbox import ToolSandbox

sandbox = ToolSandbox()

# Execute a tool safely
result = sandbox.execute(
    tool="python",
    code="print('Hello from sandbox!')",
    timeout_ms=5000
)
```

### Available Tools

- `python`: Execute Python code
- `shell`: Run shell commands
- `http`: Make HTTP requests
- `file`: Read/write files

## 📡 Message Bus

Pub/sub messaging between agents:

```python
from dino_os.message_bus import MessageBus

bus = MessageBus()

# Subscribe to a channel
bus.subscribe("trading_signals", my_callback)

# Publish a message
bus.publish("trading_signals", {"action": "buy", "symbol": "BTC"})

# Unsubscribe
bus.unsubscribe("trading_signals", my_callback)
```

## 🔐 Security Gateway

Manage API keys and permissions:

```python
from dino_os.security_gateway import SecurityGateway

security = SecurityGateway()

# Store an API key
security.set_key("alpaca", "your-api-key")

# Retrieve (masked)
key = security.get_key("alpaca")

# Check permissions
can_execute = security.can_execute("tool_name", "user_id")

# Audit log
logs = security.get_audit_log()
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# Dino Dynasty OS Configuration
# All settings for the AI operating system

# System settings
system:
  name: "Dino Dynasty OS"
  version: "1.0.0"
  log_level: "INFO"

# LLM Configuration - Multi-provider with fallback
llm:
  # Provider registry - tried in order until one works
  providers:
    - name: "vl_local"
      provider: "vl"
      model: "llama-3.1-8b"
      base_url: "http://localhost:8000/v1"
      enabled: true
    - name: "ollama"
      provider: "ollama"
      model: "phi4-mini"
      enabled: true
    - name: "minimax"
      provider: "minimax"
      model: "MiniMax-M2.5"
      enabled: true
  
  default_temperature: 0.7
  default_max_tokens: 4096
  timeout: 60

# Workspace Sandbox
sandbox:
  enabled: true
  restrictToWorkspace: true
  workspace_path: "."

# Channel Plugins
channels:
  enabled: true
  telegram:
    enabled: false
  discord:
    enabled: false
  whatsapp:
    enabled: false

# Memory Configuration
memory:
  storage: "sqlite"
  path: "dino_memory.db"
  embedding_enabled: false

# Scheduler Configuration
scheduler:
  enabled: true
  max_concurrent_jobs: 3
  default_tz: "America/Chicago"

# Security Configuration
security:
  rate_limit:
    enabled: true
    requests_per_minute: 60
```

## 🔌 LLM Integration

### Supported Providers

| Provider | Models | Use Case |
|----------|--------|----------|
| vLLM | llama-3.1-8b, etc. | Fast local inference (OpenAI-compatible) |
| Ollama | phi4-mini, qwen2.5:7b | Local with Ollama |
| OpenRouter | claude-3.5-sonnet | Cloud fallback |
| Anthropic | Claude 3.5 | Direct API |
| MiniMax | MiniMax-M2.5 | Primary cloud |

### Using Different Models

```python
from dino_os.agent_core import AgentCore

# Use vLLM local (fastest)
agent = AgentCore(provider="vl", model="llama-3.1-8b", base_url="http://localhost:8000/v1")

# Use Ollama local
agent = AgentCore(provider="ollama", model="phi4-mini")

# Use cloud
agent = AgentCore(provider="minimax", model="MiniMax-M2.5")

# Multi-provider: configured in config.yaml, automatic fallback
```

### Auto-Fallback
The system automatically tries each enabled provider in order until one succeeds:

## 📚 Skills

Skills are reusable tools for agents:

```python
# skills/calculator.py
from dino_os import skill

@skill
def calculate(expression: str) -> float:
    """Evaluate a mathematical expression."""
    return eval(expression)

@skill
def fibonacci(n: int) -> list:
    """Generate Fibonacci sequence."""
    if n < 0:
        return []
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]
```

### Installing Skills

```bash
# List available skills
python cli.py list

# Skills are automatically loaded from skills/ directory
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_agent_core.py

# Run with coverage
python -m pytest tests/ --cov=dino_os
```

## 🛡️ Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Sandbox all tools** - Never execute untrusted code directly
3. **Audit everything** - Enable security gateway logging
4. **Limit permissions** - Use least-privilege principle

## 📖 Developer Guide

For detailed architecture, API reference, and advanced usage, see:
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Deep dive on architecture
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🦖 About

Dino Dynasty OS was built to create a standalone AI operating system that:
- Runs locally with fast inference
- Provides robust memory and scheduling
- Maintains security and isolation
- Integrates seamlessly with existing Python projects

**Built by Rex, for Rex.** 🦖👑
