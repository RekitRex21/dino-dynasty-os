# Dino Dynasty OS: Foundation

**4,159 lines of Python** - Lightweight AI operating system written in Python. Built for speed, security, and extensibility.

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

## 🤖 All 8 Agents

### **Manual Agents** (Run on demand)

| Agent | Command | Description |
|-------|---------|-------------|
| `hello` | `python cli.py run hello` | Demo agent - says hello |
| `coder` | Interactive | Reads/writes code files |
| `writer` | Interactive | Creates text content & markdown |
| `websearch` | Interactive | Searches DuckDuckGo for info |
| `computer` | Interactive | Controls mouse, keyboard, screenshots |

### **Autonomous Agents** (Run 24/7)

| Agent | Command | Check Interval | What It Does |
|-------|---------|----------------|--------------|
| `autocoder` | `python skills/autonomous_coder_agent.py` | Every 60s | Watches code, auto-implements TODOs |
| `autoresearcher` | `python skills/autonomous_researcher_agent.py` | Every 5min | Monitors topics, summarizes news |
| `autotester` | `python skills/autonomous_tester_agent.py` | Every 30s | Detects code changes, runs tests |

## 🚀 Autonomous Mode

### **autocoder** - Auto-Implements TODOs
```bash
python skills/autonomous_coder_agent.py
```
- 🔄 Runs continuously (checks every 60 seconds)
- 👀 Watches code for TODO/FIXME/XXX/HACK comments
- 🔨 Automatically implements them with appropriate code
- 📝 Logs all actions to `logs/autocoder_actions.log`

**Usage:**
```python
# Add to any Python file:
# TODO: Add error handling here

# The agent will automatically:
# 1. Detect the TODO
# 2. Generate implementation
# 3. Insert into file
# 4. Log the action
```

### **autoresearcher** - Monitors & Summarizes News
```bash
python skills/autonomous_researcher_agent.py
```
- 🔄 Runs continuously (checks every 5 minutes)
- 🔍 Searches the web for watched topics
- 📝 Generates summaries automatically
- 🚨 Alerts on significant news
- 💾 Stores results in memory

**Add topics to monitor:**
```python
agent.add_topic("Artificial Intelligence")
agent.add_topic("Python Programming")
```

### **autotester** - Auto-Runs Tests on Changes
```bash
python skills/autonomous_tester_agent.py
```
- 🔄 Runs continuously (checks every 30 seconds)
- 👀 Monitors files for changes
- 🧪 Auto-runs related tests
- 📊 Reports pass/fail status
- 💾 Stores test history

**The agent will:**
- Detect when you save a file
- Find related test files
- Run pytest or unittest
- Show results immediately

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
dino-dynasty-os/
├── dino_os/                 # Core OS modules
│   ├── agent_core.py       # Agent system with async support
│   ├── memory_layer.py     # Persistent memory
│   ├── scheduler.py        # Job scheduling
│   ├── llm_provider.py     # Multi-provider LLM
│   ├── tool_sandbox.py     # Isolated execution
│   ├── security_gateway.py # API key management
│   └── channels.py         # Messaging integrations
├── skills/                  # All agents
│   ├── hello_agent.py
│   ├── coder_agent.py
│   ├── writer_agent.py
│   ├── websearch_agent.py
│   ├── computer_use_agent.py
│   ├── autonomous_coder_agent.py      # 24/7 autonomous
│   ├── autonomous_researcher_agent.py # 24/7 autonomous
│   └── autonomous_tester_agent.py     # 24/7 autonomous
├── channels/                # Discord, Telegram, WhatsApp
├── logs/                    # Autonomous agent logs
├── screenshots/             # Computer agent screenshots
├── cli.py                   # CLI entry point
├── dashboard.py             # Interactive TUI
├── config.yaml              # System configuration
└── requirements.txt         # Dependencies
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

## 💻 Computer Control Agent

The `computer` agent provides full desktop automation:

```python
from skills.computer_use_agent import ComputerUseAgent

agent = ComputerUseAgent()

# Screenshots
agent.take_screenshot()  # Saves to screenshots/

# Mouse control
agent.move_mouse(500, 300)
agent.click_mouse()
agent.scroll(-3, 500, 300)

# Keyboard control
agent.type_text("Hello World!")
agent.press_key("enter")
agent.press_key("ctrl+c")  # Hotkeys

# Screen info
size = agent.get_screen_size()
position = agent.get_mouse_position()
```

### Installation
```bash
pip install -r skills/computer_use_requirements.txt
```

## 🛡️ Safety Features

- ✅ **All computer actions logged** to `logs/computer_use_YYYYMMDD.log`
- ✅ **Dangerous text blocked** (sudo, rm -rf, passwords)
- ✅ **Workspace sandboxing** - Files restricted to workspace
- ✅ **API key validation** with hashing
- ✅ **Rate limiting** on all operations
- ✅ **Failsafe** - Move mouse to corner = emergency stop
- ✅ **Autonomous action logging** - Every agent action recorded
- ✅ **Continuous operation** - Agents run 24/7 with full logging

### Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Sandbox all tools** - Never execute untrusted code directly
3. **Audit everything** - Enable security gateway logging
4. **Limit permissions** - Use least-privilege principle
5. **Review autonomous logs** - Check logs/ directory regularly

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

## 🎯 Use Cases

### 1. **Auto-Implement All TODOs**
```bash
python skills/autonomous_coder_agent.py
# Add # TODO: comments to any file
# The agent will implement them automatically
```

### 2. **Research AI News Continuously**
```bash
python skills/autonomous_researcher_agent.py
# Monitors topics and alerts on significant news
```

### 3. **Auto-Test on Every Save**
```bash
python skills/autonomous_tester_agent.py
# Detects file changes and runs tests automatically
```

### 4. **Control Your Computer**
```python
from skills.computer_use_agent import ComputerUseAgent
agent = ComputerUseAgent()
agent.take_screenshot()
agent.type_text("Hello")
```

### 5. **Search & Research**
```python
from skills.websearch_agent import WebSearchAgent
result = await WebSearchAgent().run("Python best practices")
print(result['output'])
```

### 6. **Write Code Automatically**
```python
from skills.coder_agent import CoderAgent
agent = CoderAgent()
agent.write_file("script.py", "print('Hello')")
```

## 🦖 About

**Dino Dynasty OS** is a fully autonomous AI operating system that:
- 🤖 Runs 24/7 without human input
- 🧠 Makes decisions and takes actions autonomously
- 💾 Remembers and learns from past actions
- 🌐 Searches and monitors the web continuously
- 💻 Controls your computer (mouse, keyboard, screenshots)
- 📝 Writes and edits code automatically
- 🧪 Tests code continuously
- 🛡️ Stays secure with comprehensive safety controls
- 📱 Integrates with messaging platforms
- ⚡ Provides fast local LLM inference

**A complete autonomous AI framework with 8 agents, persistent memory, job scheduling, and full computer control.**

**Built by Rex, for Rex.** 🦖👑
