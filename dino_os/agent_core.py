"""Agent Core - MCP-style agent runner for Dino Dynasty OS."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Tool:
    """Represents a tool that can be registered with an agent."""
    
    def __init__(self, name: str, description: str, func: callable):
        """Initialize a tool.
        
        Args:
            name: Tool name
            description: Tool description
            func: Function to execute
        """
        self.name = name
        self.description = description
        self.func = func

    def __call__(self, *args, **kwargs) -> Any:
        """Execute the tool."""
        return self.func(*args, **kwargs)


class Agent(ABC):
    """Base agent class for Dino Dynasty OS."""
    
    # Subclasses should override these
    name: str = "base_agent"
    description: str = "A base agent"
    
    def __init__(self):
        """Initialize the agent."""
        self._tools: Dict[str, Tool] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def register_tool(self, name: str, description: str, func: callable) -> None:
        """Register a tool with the agent.
        
        Args:
            name: Tool name
            description: Tool description
            func: Function to execute
        """
        self._tools[name] = Tool(name, description, func)

    def tool(self, name: str, description: str):
        """Decorator to register a tool.
        
        Args:
            name: Tool name
            description: Tool description
        """
        def decorator(func: callable):
            self.register_tool(name, description, func)
            return func
        return decorator

    @property
    def tools(self) -> List[Dict[str, str]]:
        """Get list of registered tools."""
        return [
            {"name": name, "description": tool.description}
            for name, tool in self._tools.items()
        ]

    @property
    def is_running(self) -> bool:
        """Check if agent is running."""
        return self._running

    async def start(self) -> None:
        """Start the agent."""
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        """Stop the agent."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run_loop(self) -> None:
        """Internal run loop."""
        try:
            await self.run()
        except Exception as e:
            print(f"Agent {self.name} error: {e}")
        finally:
            self._running = False

    @abstractmethod
    async def run(self) -> Dict[str, Any]:
        """Main agent execution. Override in subclasses.
        
        Returns:
            Dictionary with execution results.
        """
        raise NotImplementedError

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Tool execution result.
        """
        if tool_name not in self._tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        return self._tools[tool_name](**kwargs)
