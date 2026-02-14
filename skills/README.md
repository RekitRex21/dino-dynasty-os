# Dino Dynasty OS Skills

This directory contains agent skills for Dino Dynasty OS.

## Creating a New Agent

1. Create a file named `<agent_name>_agent.py`
2. Import the Agent base class: `from dino_os import Agent`
3. Create a class that inherits from Agent
4. Implement the `run()` method

Example:
```python
from dino_os import Agent

class HelloAgent(Agent):
    name = "hello"
    description = "Says hello"
    
    async def run(self):
        print("Hello from Dino Dynasty OS!")
        return {"status": "success"}
```

## Running Your Agent

```bash
python cli.py run hello
```
