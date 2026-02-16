"""Writer Agent - AI writing assistant for content creation."""

from dino_os.agent_core import Agent
from dino_os.tool_sandbox import FileSandbox


class WriterAgent(Agent):
    """Agent that can write and edit text content."""
    
    name = "writer"
    description = "Writes and edits text content"
    
    def __init__(self):
        super().__init__()
        self.files = FileSandbox()
        
    async def run(self):
        """Run the writer agent."""
        return {
            "status": "success",
            "output": "Writer agent ready! I can help you write and edit content."
        }
    
    def write_content(self, filepath: str, content: str) -> bool:
        """Write content to a file."""
        try:
            self.files.write(filepath, content)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def read_content(self, filepath: str) -> str:
        """Read content from a file."""
        try:
            return self.files.read(filepath)
        except Exception as e:
            return f"Error: {e}"
    
    def generate_markdown(self, title: str, sections: list) -> str:
        """Generate markdown document."""
        md = f"# {title}\n\n"
        for section in sections:
            md += f"## {section}\n\n"
            md += "Content here...\n\n"
        return md
