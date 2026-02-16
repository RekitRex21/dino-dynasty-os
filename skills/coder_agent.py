"""Coder Agent - AI-powered coding assistant for Dino Dynasty OS."""

from dino_os.agent_core import Agent
from dino_os.tool_sandbox import FileSandbox


class CoderAgent(Agent):
    """Agent that can write, edit, and analyze code."""
    
    name = "coder"
    description = "Writes and edits code files"
    
    def __init__(self):
        super().__init__()
        self.files = FileSandbox()
        
    async def run(self):
        """Run the coder agent."""
        return {
            "status": "success",
            "output": "Coder agent ready! Use register_tool to add coding capabilities."
        }
    
    def read_file(self, filepath: str) -> str:
        """Read a file's contents."""
        try:
            return self.files.read(filepath)
        except Exception as e:
            return f"Error reading file: {e}"
    
    def write_file(self, filepath: str, content: str) -> bool:
        """Write content to a file."""
        try:
            self.files.write(filepath, content)
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False
    
    def list_files(self, directory: str = ".") -> list:
        """List files in a directory."""
        return self.files.list_dir(directory)
