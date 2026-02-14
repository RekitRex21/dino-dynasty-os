# Dino Dynasty OS: API Reference

Complete API documentation for all modules.

## 📦 dino_os Package

### Module: agent_core

#### AgentCore

```python
from dino_os.agent_core import AgentCore

agent = AgentCore(provider="ollama", model="phi4-mini")
```

**Parameters:**
- `provider` (str): LLM provider (ollama, openai, anthropic)
- `model` (str): Model name
- `api_key` (str, optional): API key override
- `base_url` (str, optional): Custom endpoint

**Methods:**

##### `run(prompt: str, **kwargs) -> str`

Execute an agent with a prompt.

```python
response = agent.run("Analyze BTCUSDT market conditions")
print(response)
```

##### `run_stream(prompt: str) -> Generator[str, None, None]`

Stream response token by token.

```python
for token in agent.run_stream("Write a trading strategy"):
    print(token, end="", flush=True)
```

##### `chat(messages: list) -> str`

Multi-turn chat conversation.

```python
messages = [
    {"role": "system", "content": "You are a trading expert."},
    {"role": "user", "content": "What's the trend for ETH?"}
]
response = agent.chat(messages)
```

### Module: config

#### Config

```python
from dino_os.config import Config

config = Config("config.yaml")
```

**Methods:**

##### `get(path: str) -> any`

Get nested config value using dot notation.

```python
config.get("llm.local.model")  # Returns "phi4-mini"
config.get("system.log_level")  # Returns "INFO"
```

##### `set(path: str, value: any) -> None`

Set nested config value.

```python
config.set("system.log_level", "DEBUG")
```

##### `reload() -> None`

Reload config from file.

```python
config.reload()
```

**Config Structure:**

```yaml
system:
  name: str
  version: str
  log_level: str  # DEBUG, INFO, WARNING, ERROR

llm:
  provider: str
  local:
    provider: str
    model: str
    base_url: str
  cloud:
    provider: str
    model: str
  fallback:
    provider: str
    model: str
  embeddings:
    provider: str
    model: str

memory:
  backend: str
  path: str
  semantic: bool

scheduler:
  enabled: bool
  timezone: str

security:
  enabled: bool
  require_keys: bool
  audit_log: bool
```

### Module: memory_layer

#### MemoryLayer

```python
from dino_os.memory_layer import MemoryLayer

memory = MemoryLayer(db_path="dino_memory.db")
```

**Methods:**

##### `add(key: str, value: str, embed: bool = True) -> None`

Store a memory.

```python
memory.add("user_name", "Rex")
memory.add("trade_history", json.dumps(trades), embed=True)
```

##### `get(key: str) -> Optional[str]`

Retrieve a memory by key.

```python
value = memory.get("user_name")  # Returns "Rex"
```

##### `delete(key: str) -> bool`

Delete a memory.

```python
memory.delete("temporary_data")
```

##### `list() -> List[str]`

List all keys.

```python
keys = memory.list()
```

##### `search(query: str, top_k: int = 5) -> List[MemoryResult]`

Semantic search.

```python
results = memory.search("trading preferences", top_k=10)
for result in results:
    print(f"{result.key}: {result.score:.3f} - {result.value[:50]}...")
```

##### `get_all() -> Dict[str, str]`

Export all memories.

```python
all_memory = memory.get_all()
```

##### `clear() -> None`

Clear all memories.

```python
memory.clear()
```

##### `backup(path: str) -> None`

Backup database.

```python
memory.backup("backup_20240101.db")
```

##### `restore(path: str) -> None`

Restore from backup.

```python
memory.restore("backup_20240101.db")
```

### Module: scheduler

#### Scheduler

```python
from dino_os.scheduler import Scheduler

scheduler = Scheduler()
```

**Methods:**

##### `add_job(name: str, func: Callable, trigger: dict, **kwargs) -> str`

Add a scheduled job.

```python
# Cron trigger
scheduler.add_job(
    name="daily_report",
    func=generate_report,
    trigger={"kind": "cron", "expr": "0 9 * * *"}
)

# Interval trigger
scheduler.add="health_check",
    func=check_system,
    trigger={"kind": "interval", "everyMs": 60000}
)

#_job(
    name One-time trigger
scheduler.add_job(
    name="delayed_task",
    func=send_reminder,
    trigger={"kind": "at", "at": "2024-01-15T10:00:00Z"}
)
```

##### `remove_job(job_id: str) -> bool`

Remove a job.

```python
scheduler.remove_job("daily_report")
```

##### `list_jobs() -> List[Job]`

List all jobs.

```python
jobs = scheduler.list_jobs()
for job in jobs:
    print(f"{job.id}: {job.name} - {job.next_run}")
```

##### `start() -> None`

Start the scheduler.

```python
scheduler.start()
```

##### `stop() -> None`

Stop the scheduler.

```python
scheduler.stop()
```

##### `pause(job_id: str) -> None`

Pause a job.

```python
scheduler.pause("daily_report")
```

##### `resume(job_id: str) -> None`

Resume a job.

```python
scheduler.resume("daily_report")
```

##### `run_now(job_id: str) -> None`

Trigger a job to run immediately.

```python
scheduler.run_now("daily_report")
```

**Job Attributes:**

```python
@dataclass
class Job:
    id: str
    name: str
    func: str  # Function name
    trigger: dict
    next_run: datetime
    last_run: Optional[datetime]
    status: str  # scheduled, paused, running
```

### Module: message_bus

#### MessageBus

```python
from dino_os.message_bus import MessageBus

bus = MessageBus()
```

**Methods:**

##### `subscribe(channel: str, callback: Callable) -> str`

Subscribe to a channel.

```python
def on_trade(data):
    print(f"Trade: {data}")

sub_id = bus.subscribe("trading", on_trade)
```

##### `unsubscribe(channel: str, callback_or_id: Union[Callable, str]) -> bool`

Unsubscribe from a channel.

```python
bus.unsubscribe("trading", sub_id)
# or
bus.unsubscribe("trading", on_trade)
```

##### `publish(channel: str, message: dict) -> int`

Publish a message to a channel.

```python
count = bus.publish("trading", {
    "action": "buy",
    "symbol": "BTCUSDT",
    "amount": 0.1
})
print(f"Published to {count} subscribers")
```

##### `get_subscribers(channel: str) -> List[Subscriber]`

Get subscribers for a channel.

```python
subscribers = bus.get_subscribers("trading")
```

##### `list_channels() -> List[str]`

List all channels.

```python
channels = bus.list_channels()
```

##### `channel_history(channel: str, limit: int = 100) -> List[Message]`

Get message history for a channel.

```python
history = bus.channel_history("trading", limit=50)
```

##### `ping() -> bool`

Check if message bus is running.

```python
if bus.ping():
    print("Message bus is alive")
```

### Module: security_gateway

#### SecurityGateway

```python
from dino_os.security_gateway import SecurityGateway

security = SecurityGateway()
```

**Methods:**

##### `set_key(service: str, key: str, metadata: dict = None) -> bool`

Store an API key.

```python
security.set_key("alpaca", "your-api-key", {
    "created": "2024-01-01",
    "permissions": ["trade", "read"]
})
```

##### `get_key(service: str, masked: bool = True) -> Optional[str]`

Retrieve an API key.

```python
key = security.get_key("alpaca")  # Returns "AKIA..."
masked = security.get_key("alpaca", masked=False)  # Returns full key
```

##### `delete_key(service: str) -> bool`

Delete an API key.

```python
security.delete_key("unused_service")
```

##### `list_keys() -> List[KeyInfo]`

List all stored keys (masked).

```python
keys = security.list_keys()
for key in keys:
    print(f"{key.service}: {key.key[:8]}... ({key.created})")
```

##### `can_execute(tool: str, entity: str) -> bool`

Check execution permission.

```python
if security.can_execute("python_sandbox", "agent_1"):
    print("Permission granted")
```

##### `grant_permission(entity: str, permission: str) -> bool`

Grant a permission.

```python
security.grant_permission("agent_1", "trade_execution")
```

##### `revoke_permission(entity: str, permission: str) -> bool`

Revoke a permission.

```python
security.revoke_permission("agent_1", "trade_execution")
```

##### `get_permissions(entity: str) -> List[str]`

Get all permissions for an entity.

```python
perms = security.get_permissions("agent_1")
```

##### `get_audit_log(limit: int = 100) -> List[AuditEntry]`

Get audit log entries.

```python
logs = security.get_audit_log()
for log in logs:
    print(f"{log.timestamp}: {log.action} by {log.entity}")
```

##### `log_action(action: str, entity: str, details: dict = None) -> None`

Log an action.

```python
security.log_action("api_call", "agent_1", {"tool": "trading_api"})
```

##### `rotate_key(service: str) -> bool`

Rotate an API key.

```python
if security.rotate_key("alpaca"):
    print("Key rotated successfully")
```

### Module: tool_sandbox

#### ToolSandbox

```python
from dino_os.tool_sandbox import ToolSandbox

sandbox = ToolSandbox()
```

**Methods:**

##### `execute(tool: str, **kwargs) -> SandboxResult`

Execute a tool in sandbox.

```python
# Execute Python code
result = sandbox.execute(
    tool="python",
    code="print('Hello!')",
    timeout_ms=5000
)

# Execute shell command
result = sandbox.execute(
    tool="shell",
    command="dir",
    timeout_ms=10000
)

# HTTP request
result = sandbox.execute(
    tool="http",
    url="https://api.example.com/data",
    method="GET"
)
```

##### `register_tool(name: str, func: Callable) -> None`

Register a custom tool.

```python
@sandbox.register_tool
def custom_analysis(data: str) -> dict:
    return {"result": analyze(data)}
```

##### `unregister_tool(name: str) -> bool`

Unregister a tool.

```python
sandbox.unregister_tool("custom_analysis")
```

##### `list_tools() -> List[str]`

List available tools.

```python
tools = sandbox.list_tools()
```

##### `set_timeout(tool: str, timeout_ms: int) -> None`

Set timeout for a tool.

```python
sandbox.set_timeout("python", 30000)  # 30 seconds
```

**Built-in Tools:**

| Tool | Parameters | Description |
|------|------------|-------------|
| `python` | `code`, `timeout_ms` | Execute Python code |
| `shell` | `command`, `timeout_ms` | Run shell command |
| `http` | `url`, `method`, `headers`, `body` | Make HTTP request |
| `file` | `path`, `content`, `mode` | Read/write files |

### Module: cli

#### CLI Commands

```bash
python cli.py <command> [options]
```

**Commands:**

##### `run <agent> [--params JSON]`

Run an agent.

```bash
python cli.py run hello
python cli.py run analyze --params '{"symbol": "BTCUSDT"}'
```

##### `list`

List available agents.

```bash
python cli.py list
```

##### `status`

Show system status.

```bash
python cli.py status
```

##### `memory add <key> <value>`

Add a memory.

```bash
python cli.py memory add my_key "my value"
```

##### `memory get <key>`

Get a memory.

```bash
python cli.py memory get my_key
```

##### `memory list`

List all memories.

```bash
python cli.py memory list
```

##### `memory search <query>`

Search memories.

```bash
python cli.py memory search "trading"
```

##### `scheduler list`

List scheduled jobs.

```bash
python cli.py scheduler list
```

##### `scheduler start`

Start the scheduler.

```bash
python cli.py scheduler start
```

##### `scheduler stop`

Stop the scheduler.

```bash
python cli.py scheduler stop
```

##### `config get <path>`

Get config value.

```bash
python cli.py config get llm.local.model
```

##### `version`

Show version.

```bash
python cli.py version
```

##### `help`

Show help.

```bash
python cli.py help
```

## 🦖 Decorator: @skill

The `@skill` decorator marks functions as agents/skills:

```python
from dino_os import skill

@skill
def my_agent(param1: str, param2: int = 10) -> dict:
    """
    Agent description.
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        Dict with results
    """
    # Agent logic
    return {"result": "value"}
```

**Features:**
- Automatic parameter parsing
- Type validation
- Help text generation
- Error handling
- Integration with CLI

## 📊 Result Types

### SandboxResult

```python
@dataclass
class SandboxResult:
    success: bool
    output: str
    error: Optional[str]
    execution_time_ms: int
    memory_used_bytes: int
```

### MemoryResult

```python
@dataclass
class MemoryResult:
    key: str
    value: str
    score: float  # Similarity score (0-1)
    created: datetime
```

### Job

```python
@dataclass
class Job:
    id: str
    name: str
    func: str
    trigger: dict
    next_run: Optional[datetime]
    last_run: Optional[datetime]
    status: str
```

### AuditEntry

```python
@dataclass
class AuditEntry:
    timestamp: datetime
    action: str
    entity: str
    details: dict
    result: str
```

## 🔧 Exceptions

| Exception | Description |
|-----------|-------------|
| `ConfigError` | Configuration file error |
| `MemoryError` | Memory operation error |
| `SchedulerError` | Scheduler operation error |
| `SecurityError` | Security violation |
| `SandboxError` | Sandbox execution error |
| `MessageBusError` | Message bus error |

## 📚 See Also

- [README.md](README.md) - Getting started guide
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Architecture and patterns

**Happy coding!** 🦖👑
