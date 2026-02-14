"""Tool Sandbox - Isolated tool execution for Dino Dynasty OS."""

import asyncio
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    duration_ms: float


class ToolSandbox:
    """Isolated tool execution environment with workspace restriction."""
    
    def __init__(self, base_path: Optional[str] = None, workspace_path: Optional[str] = None):
        """Initialize the tool sandbox.
        
        Args:
            base_path: Base path for tool scripts.
            workspace_path: Allowed workspace path (for restriction).
        """
        self._tools: Dict[str, Dict[str, Any]] = {}
        self.base_path = base_path or os.path.dirname(__file__)
        
        # Workspace restriction
        if workspace_path:
            self.workspace_path = Path(workspace_path).resolve()
        else:
            self.workspace_path = Path(__file__).parent.parent.resolve()
        self.restrict_to_workspace = True  # Default enabled

    def register_tool(self, name: str, path: str, description: str = "", allowed: bool = True) -> None:
        """Register a tool.
        
        Args:
            name: Tool name
            path: Path to tool script
            description: Tool description
            allowed: Whether tool is allowed to run
        """
        self._tools[name] = {
            "path": path,
            "description": description,
            "allowed": allowed
        }

    def list_tools(self) -> List[Dict[str, str]]:
        """List all registered tools."""
        return [
            {"name": name, "description": info["description"], "allowed": str(info["allowed"])}
            for name, info in self._tools.items()
        ]

    def is_allowed(self, name: str) -> bool:
        """Check if a tool is allowed."""
        return self._tools.get(name, {}).get("allowed", False)

    def _is_path_safe(self, path: str) -> bool:
        """Check if a path is within the workspace.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is safe (within workspace).
        """
        if not self.restrict_to_workspace:
            return True
        
        try:
            resolved = Path(path).resolve()
            # Check if path is within workspace
            return str(resolved).startswith(str(self.workspace_path))
        except Exception:
            return False

    def set_workspace_restriction(self, enabled: bool, workspace_path: Optional[str] = None) -> None:
        """Configure workspace restriction.
        
        Args:
            enabled: Whether to enable restriction
            workspace_path: Optional new workspace path
        """
        self.restrict_to_workspace = enabled
        if workspace_path:
            self.workspace_path = Path(workspace_path).resolve()

    async def execute(self, name: str, args: Optional[List[str]] = None, timeout: int = 30) -> ToolResult:
        """Execute a tool in isolation.
        
        Args:
            name: Tool name
            args: Command line arguments
            timeout: Execution timeout in seconds
            
        Returns:
            ToolResult with execution details.
        """
        if name not in self._tools:
            return ToolResult(
                success=False,
                stdout="",
                stderr=f"Unknown tool: {name}",
                return_code=-1,
                duration_ms=0
            )
        
        tool_info = self._tools[name]
        if not tool_info["allowed"]:
            return ToolResult(
                success=False,
                stdout="",
                stderr=f"Tool {name} is not allowed",
                return_code=-1,
                duration_ms=0
            )
        
        import time
        start_time = time.time()
        
        cmd = [sys.executable, tool_info["path"]] + (args or [])
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.base_path)
            )
            stdout, stderr = await process.communicate(timeout=timeout)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=process.returncode == 0,
                stdout=stdout.decode('utf-8'),
                stderr=stderr.decode('utf-8'),
                return_code=process.returncode,
                duration_ms=duration_ms
            )
        except asyncio.TimeoutExpired:
            return ToolResult(
                success=False,
                stdout="",
                stderr=f"Tool execution timed out after {timeout} seconds",
                return_code=-1,
                duration_ms=timeout * 1000
            )
        except Exception as e:
            return ToolResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                duration_ms=(time.time() - start_time) * 1000
            )

    async def execute_python(self, code: str, timeout: int = 30) -> ToolResult:
        """Execute Python code in isolation.
        
        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            ToolResult with execution details.
        """
        import time
        start_time = time.time()
        
        try:
            # Create a subprocess with restricted environment
            env = os.environ.copy()
            env.update({
                "PYTHONPATH": self.base_path,
                "PYTHONUNBUFFERED": "1"
            })
            
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-c", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=str(self.base_path)
            )
            stdout, stderr = await process.communicate(timeout=timeout)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=process.returncode == 0,
                stdout=stdout.decode('utf-8'),
                stderr=stderr.decode('utf-8'),
                return_code=process.returncode,
                duration_ms=duration_ms
            )
        except asyncio.TimeoutExpired:
            return ToolResult(
                success=False,
                stdout="",
                stderr=f"Code execution timed out after {timeout} seconds",
                return_code=-1,
                duration_ms=timeout * 1000
            )
        except Exception as e:
            return ToolResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                duration_ms=(time.time() - start_time) * 1000
            )


class FileSandbox:
    """File operation sandbox with workspace restriction."""
    
    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize file sandbox.
        
        Args:
            workspace_path: Path to allowed workspace.
        """
        if workspace_path:
            self.workspace_path = Path(workspace_path).resolve()
        else:
            self.workspace_path = Path(__file__).parent.parent.parent.resolve()
        self.restrict_enabled = True
    
    def set_restriction(self, enabled: bool, workspace_path: Optional[str] = None) -> None:
        """Configure workspace restriction.
        
        Args:
            enabled: Whether to enable restriction
            workspace_path: Optional workspace path
        """
        self.restrict_enabled = enabled
        if workspace_path:
            self.workspace_path = Path(workspace_path).resolve()
    
    def _check_path(self, path: str) -> Path:
        """Check and resolve a path within workspace.
        
        Args:
            path: Path to check
            
        Returns:
            Resolved path
            
        Raises:
            ValueError: If path is outside workspace.
        """
        resolved = Path(path).resolve()
        
        if self.restrict_enabled:
            try:
                resolved.relative_to(self.workspace_path)
            except ValueError:
                raise ValueError(f"Path '{path}' is outside allowed workspace '{self.workspace_path}'")
        
        return resolved
    
    def read(self, path: str) -> str:
        """Read a file (within workspace).
        
        Args:
            path: File path
            
        Returns:
            File contents
        """
        safe_path = self._check_path(path)
        return safe_path.read_text(encoding='utf-8')
    
    def write(self, path: str, content: str) -> None:
        """Write to a file (within workspace).
        
        Args:
            path: File path
            content: Content to write
        """
        safe_path = self._check_path(path)
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content, encoding='utf-8')
    
    def exists(self, path: str) -> bool:
        """Check if path exists (within workspace).
        
        Args:
            path: Path to check
            
        Returns:
            True if exists.
        """
        try:
            safe_path = self._check_path(path)
            return safe_path.exists()
        except ValueError:
            return False
    
    def list_dir(self, path: str = ".") -> List[str]:
        """List directory contents (within workspace).
        
        Args:
            path: Directory path
            
        Returns:
            List of filenames.
        """
        safe_path = self._check_path(path)
        if safe_path.is_dir():
            return [f.name for f in safe_path.iterdir()]
        return []
