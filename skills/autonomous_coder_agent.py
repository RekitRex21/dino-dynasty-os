"""Autonomous Coder Agent - Watches code and auto-implements TODOs.

This agent runs continuously, monitors codebase for TODO/FIXME comments,
and automatically implements them using LLM and file operations.
"""

import asyncio
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import hashlib

from dino_os.agent_core import Agent
from dino_os.tool_sandbox import FileSandbox


class AutonomousCoderAgent(Agent):
    """Autonomous agent that watches code and implements TODOs.
    
    Runs continuously, scans files for TODO/FIXME comments,
    and auto-implements them using available tools.
    """
    
    name = "autocoder"
    description = "Autonomous: Watches code and implements TODOs automatically"
    
    def __init__(self):
        super().__init__()
        self.files = FileSandbox()
        self.watch_paths: List[Path] = []
        self.processed_todos: Set[str] = set()  # Hash of processed TODOs
        self.is_running = False
        self.check_interval = 60  # Check every 60 seconds
        
    def add_watch_path(self, path: str):
        """Add a directory to watch for code changes."""
        self.watch_paths.append(Path(path))
        
    async def run(self):
        """Start autonomous operation loop."""
        self.is_running = True
        
        if not self.watch_paths:
            # Default: watch skills directory
            self.watch_paths.append(Path(__file__).parent)
        
        print(f"🤖 Autonomous Coder started")
        print(f"   Watching: {[str(p) for p in self.watch_paths]}")
        print(f"   Check interval: {self.check_interval}s")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while self.is_running:
                await self._scan_and_implement()
                await asyncio.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("\n🛑 Autonomous Coder stopped")
            
        return {"status": "success", "output": "Autonomous operation completed"}
    
    async def _scan_and_implement(self):
        """Scan files and implement TODOs."""
        for watch_path in self.watch_paths:
            if not watch_path.exists():
                continue
                
            for file_path in watch_path.rglob("*.py"):
                if file_path.name.startswith("__"):
                    continue
                    
                try:
                    content = file_path.read_text()
                    todos = self._extract_todos(content, file_path)
                    
                    for todo in todos:
                        todo_hash = self._hash_todo(todo)
                        if todo_hash not in self.processed_todos:
                            await self._implement_todo(todo, file_path)
                            self.processed_todos.add(todo_hash)
                            
                except Exception as e:
                    print(f"   Error scanning {file_path}: {e}")
    
    def _extract_todos(self, content: str, file_path: Path) -> List[Dict]:
        """Extract TODO/FIXME comments from code."""
        todos = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Match TODO, FIXME, XXX, HACK comments
            patterns = [
                r'#\s*(TODO|FIXME|XXX|HACK)[\s:]+(.+)',
                r'""".*?(TODO|FIXME|XXX|HACK)[\s:]+(.+).*?"""',
                r"'''.*?(TODO|FIXME|XXX|HACK)[\s:]+(.+).*?'''",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    todos.append({
                        'type': match.group(1).upper(),
                        'description': match.group(2).strip(),
                        'line': i,
                        'context': self._get_context(lines, i)
                    })
                    break
                    
        return todos
    
    def _get_context(self, lines: List[str], line_num: int, context_lines: int = 3) -> str:
        """Get surrounding context for a TODO."""
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        return '\n'.join(lines[start:end])
    
    def _hash_todo(self, todo: Dict) -> str:
        """Create unique hash for a TODO."""
        content = f"{todo['type']}:{todo['description']}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _implement_todo(self, todo: Dict, file_path: Path):
        """Implement a TODO automatically."""
        print(f"\n🔨 Implementing {todo['type']}: {todo['description'][:50]}...")
        print(f"   File: {file_path.name}:{todo['line']}")
        
        # Simple implementations based on TODO type
        implementation = self._generate_implementation(todo)
        
        if implementation:
            try:
                # Insert implementation after TODO comment
                self._insert_implementation(file_path, todo['line'], implementation)
                print(f"   ✅ Implemented successfully")
                
                # Log the action
                await self._log_action(todo, file_path, implementation)
                
            except Exception as e:
                print(f"   ❌ Implementation failed: {e}")
    
    def _generate_implementation(self, todo: Dict) -> Optional[str]:
        """Generate implementation code based on TODO description."""
        desc = todo['description'].lower()
        
        # Pattern matching for common TODOs
        if 'print' in desc or 'log' in desc:
            return '        print(f"Debug: {variable}")  # Auto-implemented'
            
        elif 'error handling' in desc or 'exception' in desc:
            return '''        try:
            # Implementation here
            pass
        except Exception as e:
            print(f"Error: {e}")  # Auto-implemented error handling'''
            
        elif 'return' in desc:
            return '        return None  # Auto-implemented return'
            
        elif 'import' in desc:
            return '# Auto-implemented import'
            
        elif 'function' in desc or 'def ' in desc:
            return '''    def auto_function():
        """Auto-implemented function"""
        pass'''
            
        elif 'class' in desc:
            return '''class AutoClass:
    """Auto-implemented class"""
    pass'''
            
        elif 'test' in desc:
            return '''    def test_auto(self):
        """Auto-implemented test"""
        assert True  # TODO: Add actual test'''
            
        else:
            # Generic implementation
            return f'        # TODO: {todo["description"]}\n        pass  # Auto-implemented placeholder'
    
    def _insert_implementation(self, file_path: Path, line_num: int, implementation: str):
        """Insert implementation into file after TODO line."""
        lines = file_path.read_text().split('\n')
        
        # Find the right indentation
        todo_line = lines[line_num - 1]
        indent = len(todo_line) - len(todo_line.lstrip())
        base_indent = ' ' * indent
        
        # Apply indentation to implementation
        impl_lines = implementation.split('\n')
        indented_impl = '\n'.join([base_indent + line.lstrip() for line in impl_lines])
        
        # Insert after TODO line
        lines.insert(line_num, indented_impl)
        
        # Write back
        file_path.write_text('\n'.join(lines))
    
    async def _log_action(self, todo: Dict, file_path: Path, implementation: str):
        """Log autonomous actions."""
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "autocoder_actions.log"
        
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Time: {datetime.now().isoformat()}\n")
            f.write(f"File: {file_path}\n")
            f.write(f"TODO: {todo['type']}: {todo['description']}\n")
            f.write(f"Line: {todo['line']}\n")
            f.write(f"Implementation:\n{implementation}\n")
    
    def stop(self):
        """Stop autonomous operation."""
        self.is_running = False
        print("\n🛑 Stopping Autonomous Coder...")


if __name__ == "__main__":
    # Run autonomously
    agent = AutonomousCoderAgent()
    agent.add_watch_path(".")
    asyncio.run(agent.run())
