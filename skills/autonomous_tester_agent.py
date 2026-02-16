"""Autonomous Tester Agent - Runs tests automatically when code changes.

This agent runs continuously, monitors the codebase for changes,
and automatically runs tests when files are modified.
"""

import asyncio
import hashlib
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from dino_os.agent_core import Agent
from dino_os.memory_layer import MemoryLayer


class AutonomousTesterAgent(Agent):
    """Autonomous agent that runs tests when code changes.
    
    Runs continuously, monitors files for modifications,
    auto-discovers and runs tests, reports results.
    """
    
    name = "autotester"
    description = "Autonomous: Runs tests automatically when code changes"
    
    def __init__(self):
        super().__init__()
        self.memory = MemoryLayer()
        self.watch_paths: List[Path] = []
        self.file_hashes: Dict[str, str] = {}  # filepath -> hash
        self.check_interval = 30  # Check every 30 seconds
        self.is_running = False
        self.test_results: List[Dict] = []
        
    def add_watch_path(self, path: str):
        """Add a directory to watch for changes."""
        self.watch_paths.append(Path(path))
        
    async def run(self):
        """Start autonomous testing loop."""
        self.is_running = True
        
        if not self.watch_paths:
            # Default: watch current directory
            self.watch_paths.append(Path("."))
        
        print(f"🧪 Autonomous Tester started")
        print(f"   Watching: {[str(p) for p in self.watch_paths]}")
        print(f"   Check interval: {self.check_interval}s")
        print(f"   Press Ctrl+C to stop\n")
        
        # Initial scan
        await self._initial_scan()
        
        try:
            while self.is_running:
                changed_files = await self._detect_changes()
                
                if changed_files:
                    print(f"\n📝 Detected changes in {len(changed_files)} file(s)")
                    await self._run_tests(changed_files)
                
                await asyncio.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Autonomous Tester stopped")
            
        return {"status": "success", "output": "Testing completed"}
    
    async def _initial_scan(self):
        """Initial scan to establish baseline."""
        print("📊 Scanning codebase...")
        total_files = 0
        
        for watch_path in self.watch_paths:
            if watch_path.exists():
                for file_path in watch_path.rglob("*.py"):
                    if self._should_watch(file_path):
                        file_hash = self._get_file_hash(file_path)
                        self.file_hashes[str(file_path)] = file_hash
                        total_files += 1
        
        print(f"   Watching {total_files} Python files")
    
    def _should_watch(self, file_path: Path) -> bool:
        """Determine if a file should be watched."""
        # Skip cache, venv, etc.
        skip_patterns = [
            '__pycache__', '.git', 'venv', '.venv', 'env',
            'node_modules', '.pytest_cache', '.mypy_cache'
        ]
        
        path_str = str(file_path)
        for pattern in skip_patterns:
            if pattern in path_str:
                return False
        
        return file_path.suffix == '.py'
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file contents."""
        try:
            content = file_path.read_bytes()
            return hashlib.md5(content).hexdigest()
        except:
            return ""
    
    async def _detect_changes(self) -> List[Path]:
        """Detect changed files."""
        changed = []
        
        for watch_path in self.watch_paths:
            if not watch_path.exists():
                continue
                
            for file_path in watch_path.rglob("*.py"):
                if not self._should_watch(file_path):
                    continue
                    
                file_key = str(file_path)
                current_hash = self._get_file_hash(file_path)
                
                if file_key not in self.file_hashes:
                    # New file
                    self.file_hashes[file_key] = current_hash
                    changed.append(file_path)
                elif self.file_hashes[file_key] != current_hash:
                    # Modified file
                    self.file_hashes[file_key] = current_hash
                    changed.append(file_path)
        
        return changed
    
    async def _run_tests(self, changed_files: List[Path]):
        """Run tests for changed files."""
        print(f"🧪 Running tests...")
        
        # Find test files related to changes
        test_files = self._find_related_tests(changed_files)
        
        if test_files:
            print(f"   Found {len(test_files)} related test file(s)")
            for test_file in test_files:
                await self._run_test_file(test_file)
        else:
            print(f"   No specific tests found, running all tests...")
            await self._run_all_tests()
        
        # Generate report
        await self._generate_report()
    
    def _find_related_tests(self, changed_files: List[Path]) -> List[Path]:
        """Find test files related to changed files."""
        test_files = []
        
        for changed_file in changed_files:
            # Look for test file patterns
            patterns = [
                changed_file.parent / f"test_{changed_file.name}",
                changed_file.parent / f"tests.py",
                changed_file.parent / "tests" / f"test_{changed_file.name}",
                changed_file.parent.parent / "tests" / f"test_{changed_file.name}",
            ]
            
            for pattern in patterns:
                if pattern.exists():
                    test_files.append(pattern)
        
        return list(set(test_files))  # Remove duplicates
    
    async def _run_test_file(self, test_file: Path):
        """Run a specific test file."""
        print(f"   Running: {test_file.name}")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            self._record_result(test_file, success, output, result.returncode)
            
            if success:
                print(f"   ✅ Passed")
            else:
                print(f"   ❌ Failed (exit code: {result.returncode})")
                
        except subprocess.TimeoutExpired:
            print(f"   ⏱️  Timeout")
            self._record_result(test_file, False, "Test timed out", -1)
        except Exception as e:
            print(f"   💥 Error: {e}")
            self._record_result(test_file, False, str(e), -1)
    
    async def _run_all_tests(self):
        """Run all tests in the project."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            success = result.returncode == 0
            
            # Parse results
            output = result.stdout
            failed = output.count("FAILED")
            passed = output.count("PASSED")
            
            print(f"   Results: {passed} passed, {failed} failed")
            
            self.test_results.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'all_tests',
                'success': success,
                'passed': passed,
                'failed': failed,
                'output': output[-1000:] if len(output) > 1000 else output
            })
            
        except Exception as e:
            print(f"   Could not run tests: {e}")
            # Try unittest instead
            await self._run_unittest()
    
    async def _run_unittest(self):
        """Fallback to unittest discovery."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            output = result.stdout
            
            print(f"   Unittest results: {'✅ Passed' if success else '❌ Failed'}")
            
            self.test_results.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'unittest',
                'success': success,
                'output': output[-500:] if len(output) > 500 else output
            })
            
        except Exception as e:
            print(f"   No tests found or error: {e}")
    
    def _record_result(self, test_file: Path, success: bool, output: str, exit_code: int):
        """Record test result."""
        self.test_results.append({
            'timestamp': datetime.now().isoformat(),
            'file': str(test_file),
            'success': success,
            'exit_code': exit_code,
            'output': output[-500:] if len(output) > 500 else output
        })
        
        # Store in memory
        memory_key = f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.memory.add(memory_key, str({
            'file': str(test_file),
            'success': success,
            'timestamp': datetime.now().isoformat()
        }))
    
    async def _generate_report(self):
        """Generate and display test report."""
        if not self.test_results:
            return
        
        recent = self.test_results[-5:]  # Last 5 results
        passed = sum(1 for r in recent if r.get('success'))
        failed = len(recent) - passed
        
        print(f"\n📊 Recent Test Summary:")
        print(f"   Passed: {passed} | Failed: {failed}")
        
        if failed > 0:
            print(f"\n   ⚠️  {failed} test(s) failed recently")
            for result in recent:
                if not result.get('success'):
                    print(f"      - {result.get('file', 'Unknown')}")
    
    def get_test_history(self) -> List[Dict]:
        """Get test history from memory."""
        keys = self.memory.list_keys(prefix="test_result_")
        history = []
        
        for key in keys:
            entry = self.memory.get(key)
            if entry:
                try:
                    import ast
                    data = ast.literal_eval(entry['value'])
                    history.append(data)
                except:
                    pass
        
        return sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    def stop(self):
        """Stop autonomous operation."""
        self.is_running = False
        print("\n🛑 Stopping Autonomous Tester...")


if __name__ == "__main__":
    # Run autonomously
    agent = AutonomousTesterAgent()
    agent.add_watch_path(".")
    asyncio.run(agent.run())
