# Dino Dynasty OS: Developer Guide

Deep dive into architecture, patterns, and extending the system.

## 🏗️ Architecture Overview

### Core Philosophy

Dino Dynasty OS follows these principles:

1. **Layered Architecture** - Clear separation of concerns
2. **Event-Driven** - Pub/sub messaging for loose coupling
3. **Sandboxed Execution** - Tools run in isolation
4. **Persistent Memory** - SQLite-backed, semantic search
5. **Local-First** - Fast local inference with cloud fallback

### System Layers

```
┌─────────────────────────────────────────────────┐
│                  CLI Layer                       │
├─────────────────────────────────────────────────┤
│                  Agent Layer                     │
│  ┌─────────────┬─────────────┬─────────────┐    │
│  │  AgentCore  │  Scheduler  │ MessageBus  │    │
│  └─────────────┴─────────────┴─────────────┘    │
├─────────────────────────────────────────────────┤
│                 Memory Layer                     │
│  ┌─────────────────────────────────────────┐    │
│  │           MemoryLayer (SQLite)           │    │
│  └─────────────────────────────────────────┘    │
├─────────────────────────────────────────────────┤
│                 Security Layer                   │
│  ┌─────────────────────────────────────────┐    │
│  │         SecurityGateway (Keys + ACL)     │    │
│  └─────────────────────────────────────────┘    │
├─────────────────────────────────────────────────┤
│                 Storage Layer                    │
│  ┌─────────────────────────────────────────┐    │
│  │           Config (YAML)                  │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

## 🔧 Extending the System

### Creating Custom Agents

Agents are Python functions decorated with `@skill`:

```python
# skills/trading_agent.py
from dino_os import skill
from dino_os.memory_layer import MemoryLayer

@skill
def analyze_market(symbol: str, timeframe: str = "1h") -> dict:
    """
    Analyze market conditions for a symbol.
    
    Args:
        symbol: Trading pair (e.g., BTCUSDT)
        timeframe: Chart timeframe (1h, 4h, 1d)
    
    Returns:
        Dict with analysis results
    """
    # Access shared memory
    memory = MemoryLayer()
    previous = memory.get(f"analysis_{symbol}")
    
    # Perform analysis
    result = {
        "symbol": symbol,
        "timeframe": timeframe,
        "signal": "neutral",
        "confidence": 0.5
    }
    
    # Store for next comparison
    memory.add(f"analysis_{symbol}", result)
    
    return result
```

### Custom Tools

Add new tools to the sandbox:

```python
# dino_os/tool_sandbox.py extension
class CustomToolSandbox(ToolSandbox):
    def __init__(self):
        super().__init__()
        self.register_tool("custom_api", self.call_custom_api)
    
    def call_custom_api(self, endpoint: str, method: str = "GET"):
        """Call a custom API endpoint."""
        import requests
        response = requests.request(method, endpoint)
        return response.json()
```

### Memory Backends

Swap the memory backend:

```python
# dino_os/memory_layer.py
class VectorMemoryLayer:
    """Alternative memory with vector similarity."""
    
    def __init__(self, embedding_model="nomic-embed-text"):
        self.embeddings = load_embedding_model(embedding_model)
        self.vector_store = ChromaCollection()
    
    def add(self, key: str, value: str, embed: bool = True):
        if embed:
            vector = self.embeddings.encode(value)
            self.vector_store.add(key, value, vector)
        else:
            self.db[key] = value
    
    def search(self, query: str, top_k: int = 5):
        query_vector = self.embeddings.encode(query)
        return self.vector_store.search(query_vector, top_k)
```

## 🎯 Agent Development Patterns

### Pattern 1: Chained Agents

```python
@skill
def analyze_trade(symbol: str) -> dict:
    """Chain multiple analysis steps."""
    # Step 1: Get price data
    price = get_price(symbol)
    
    # Step 2: Analyze trend
    trend = analyze_trend(price)
    
    # Step 3: Calculate indicators
    indicators = calculate_indicators(price)
    
    # Step 4: Generate signal
    signal = combine_signals(trend, indicators)
    
    return signal
```

### Pattern 2: Parallel Agents

```python
@skill
def multi_timeframe_analysis(symbol: str) -> dict:
    """Run analysis across timeframes in parallel."""
    from concurrent.futures import ThreadPoolExecutor
    
    timeframes = ["15m", "1h", "4h", "1d"]
    
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(
            lambda tf: analyze_tf(symbol, tf),
            timeframes
        ))
    
    return {"timeframes": dict(zip(timeframes, results))}
```

### Pattern 3: Memory-Augmented Agents

```python
@skill
def smart_trading_agent(symbol: str) -> dict:
    """
    Agent that learns from past decisions.
    """
    memory = MemoryLayer()
    
    # Retrieve similar past situations
    similar = memory.search(f"trade_{symbol}", top_k=10)
    
    # Learn from wins/losses
    wins = [s for s in similar if s["outcome"] == "win"]
    losses = [s for s in similar if s["outcome"] == "loss"]
    
    # Adjust strategy based on history
    if len(wins) > len(losses):
        strategy = "aggressive"
    else:
        strategy = "conservative"
    
    return {"strategy": strategy, "confidence": len(similar) / 10}
```

## 📡 Message Bus Patterns

### Request/Response Pattern

```python
# Request handler
@skill
def handle_price_request(symbol: str) -> dict:
    def callback(response):
        print(f"Price: {response['price']}")
    
    bus = MessageBus()
    bus.subscribe(f"price_{symbol}", callback)
    bus.publish("price_request", {"symbol": symbol})
    
    # Wait for response (simplified)
    return {"status": "requested"}
```

### Event Pattern

```python
# Event publisher
@skill
def execute_trade(signal: dict) -> dict:
    result = place_order(signal)
    
    # Notify all subscribers
    bus = MessageBus()
    bus.publish("trade_executed", result)
    
    return result

# Event subscriber
def on_trade_executed(data):
    print(f"Trade executed: {data}")
    
bus = MessageBus()
bus.subscribe("trade_executed", on_trade_executed)
```

## 🔐 Security Patterns

### API Key Rotation

```python
@skill
def rotate_api_key(service: str) -> dict:
    """Rotate API key with zero downtime."""
    security = SecurityGateway()
    
    # Get current key
    current = security.get_key(service)
    
    # Generate new key (simulated)
    new_key = generate_new_key()
    
    # Update in secret manager
    security.set_key(service, new_key)
    
    # Test new key
    test_result = test_api_connection(service, new_key)
    
    if test_result["success"]:
        return {"status": "rotated", "key_id": new_key[:8]}
    else:
        # Rollback
        security.set_key(service, current)
        return {"status": "rolled_back", "error": test_result["error"]}
```

### Permission Scopes

```python
# Define permission scopes
SCOPES = {
    "read": ["memory_get", "file_read"],
    "write": ["memory_add", "file_write"],
    "execute": ["tool_sandbox", "api_call"],
    "admin": ["key_management", "config_write"]
}

@skill
def secure_api_call(api_name: str, data: dict, scope: str) -> dict:
    """Make API call with permission check."""
    security = SecurityGateway()
    
    # Check permission
    if not security.has_permission(scope, api_name):
        return {"error": "Permission denied"}
    
    # Execute with key
    api_key = security.get_key(api_name)
    return make_api_call(api_name, api_key, data)
```

## ⚡ Performance Optimization

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_price(symbol: str) -> float:
    """Cache price lookups for 60 seconds."""
    return fetch_price(symbol)

# Use in agents
@skill
def get_symbol_price(symbol: str) -> dict:
    price = get_cached_price(symbol)
    return {"symbol": symbol, "price": price}
```

### Batch Processing

```python
@skill
def batch_analyze(symbols: list) -> dict:
    """Analyze multiple symbols efficiently."""
    # Single API call for all symbols
    data = fetch_all_prices(symbols)
    
    results = {}
    for symbol in symbols:
        results[symbol] = analyze(data[symbol])
    
    return results
```

## 🧪 Testing Strategies

### Unit Testing Agents

```python
# tests/test_agents.py
import pytest
from skills.trading_agent import analyze_market

def test_analyze_market_btc():
    result = analyze_market("BTCUSDT")
    assert result["signal"] in ["buy", "sell", "neutral"]
    assert 0 <= result["confidence"] <= 1

def test_analyze_market_with_timeframe():
    result = analyze_market("BTCUSDT", timeframe="4h")
    assert result["timeframe"] == "4h"
```

### Integration Testing

```python
# tests/test_memory.py
from dino_os.memory_layer import MemoryLayer

def test_memory_persistence():
    memory = MemoryLayer()
    memory.add("test_key", "test_value")
    
    # Simulate restart
    memory2 = MemoryLayer()
    assert memory2.get("test_key") == "test_value"

def test_semantic_search():
    memory = MemoryLayer()
    memory.add("apple_fruit", "An apple is a fruit")
    memory.add("car_vehicle", "A car is a vehicle")
    
    results = memory.search("fruit")
    assert "apple_fruit" in [r.key for r in results]
```

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "cli.py", "run", "hello"]
```

### Production Settings

```yaml
# config.yaml for production
system:
  log_level: "WARNING"
  workers: 4

memory:
  pool_size: 10
  max_connections: 100

scheduler:
  max_jobs: 1000
  thread_pool: 8

security:
  require_keys: true
  audit_log: true
  rate_limit:
    requests_per_minute: 60
    burst: 10
```

### Monitoring

```python
# metrics.py
from dino_os.scheduler import Scheduler

def track_metrics():
    scheduler = Scheduler()
    return {
        "jobs_scheduled": scheduler.job_count(),
        "agents_running": scheduler.running_jobs(),
        "memory_used": get_memory_usage(),
        "uptime": get_uptime()
    }
```

## 📚 API Reference

For complete API documentation, see [API_REFERENCE.md](API_REFERENCE.md).

## 🤝 Contributing

1. Read the architecture overview
2. Check existing agents in `skills/`
3. Follow the `@skill` decorator pattern
4. Add tests for new functionality
5. Update documentation

## 🦖rex's Notes

- Phi-4-mini is your local brain (fast, efficient)
- MiniMax-M2.1 cloud for heavy reasoning
- Always sandbox unknown code
- Memory layer is your long-term memory
- Message bus enables agent collaboration

**Build something awesome!** 🦖👑
