#!/usr/bin/env python3
"""Dino Dynasty OS CLI - Command line interface."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dino_os.agent_core import Agent
from dino_os.memory_layer import MemoryLayer
from dino_os.scheduler import Scheduler


class DinoCLI:
    """CLI for Dino Dynasty OS."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.memory = MemoryLayer()
        self.scheduler = Scheduler()
        
    def run(self):
        """Run the CLI."""
        parser = argparse.ArgumentParser(
            prog="dino",
            description="Dino Dynasty OS - A standalone AI operating system"
        )
        parser.add_argument(
            "--version",
            action="version",
            version="Dino Dynasty OS 0.1.0"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # run command
        run_parser = subparsers.add_parser("run", help="Run an agent")
        run_parser.add_argument("agent", help="Agent name to run")
        
        # list command
        subparsers.add_parser("list", help="List available agents")
        
        # status command
        subparsers.add_parser("status", help="Show system status")
        
        # memory command
        memory_parser = subparsers.add_parser("memory", help="Memory operations")
        memory_subparsers = memory_parser.add_subparsers(dest="memory_command")
        
        memory_add = memory_subparsers.add_parser("add", help="Add a memory")
        memory_add.add_argument("key", help="Memory key")
        memory_add.add_argument("value", help="Memory value")
        
        memory_get = memory_subparsers.add_parser("get", help="Get a memory")
        memory_get.add_argument("key", help="Memory key")
        
        memory_list = memory_subparsers.add_parser("list", help="List memories")
        
        memory_search = memory_subparsers.add_parser("search", help="Search memories")
        memory_search.add_argument("query", help="Search query")
        
        # scheduler command
        scheduler_parser = subparsers.add_parser("schedule", help="Scheduler operations")
        scheduler_subparsers = scheduler_parser.add_subparsers(dest="schedule_command")
        
        scheduler_add = scheduler_subparsers.add_parser("add", help="Add a scheduled job")
        scheduler_add.add_argument("job_id", help="Job ID")
        scheduler_add.add_argument("seconds", type=int, help="Interval in seconds")
        scheduler_add.add_argument("command", help="Command to run")
        
        scheduler_list = scheduler_subparsers.add_parser("list", help="List scheduled jobs")
        
        args = parser.parse_args()
        
        if args.command is None:
            parser.print_help()
            return
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if args.command == "run":
                self._run_agent(args.agent)
            elif args.command == "list":
                self._list_agents()
            elif args.command == "status":
                self._show_status()
            elif args.command == "memory":
                self._handle_memory(args)
            elif args.command == "schedule":
                self._handle_scheduler(args)
        finally:
            loop.close()
    
    def _load_agents(self) -> dict:
        """Load all agents from skills directory."""
        agents = {}
        skills_path = Path(__file__).parent / "skills"
        
        if not skills_path.exists():
            return agents
        
        for file in skills_path.glob("*_agent.py"):
            module_name = file.stem
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(module_name, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, Agent) and 
                        attr != Agent):
                        agents[attr.name] = attr
            except Exception as e:
                print(f"Error loading agent {module_name}: {e}")
        
        return agents
    
    def _run_agent(self, agent_name: str) -> None:
        """Run an agent."""
        agents = self._load_agents()
        
        if agent_name not in agents:
            print(f"Agent '{agent_name}' not found. Available agents: {', '.join(agents.keys())}")
            return
        
        agent_class = agents[agent_name]
        agent = agent_class()
        
        print(f"Running agent: {agent.name}")
        loop = asyncio.get_event_loop()
        try:
            result = loop.run_until_complete(agent.run())
            print(f"Agent completed: {result}")
        except Exception as e:
            print(f"Agent error: {e}")
    
    def _list_agents(self) -> None:
        """List available agents."""
        agents = self._load_agents()
        
        if not agents:
            print("No agents found in skills directory.")
            return
        
        print("Available agents:")
        for name, agent_class in agents.items():
            print(f"  - {name}: {agent_class.description}")
    
    def _show_status(self) -> None:
        """Show system status."""
        print("Dino Dynasty OS Status")
        print("=" * 30)
        
        # Memory stats
        keys = self.memory.list_keys()
        print(f"Memory entries: {len(keys)}")
        
        # Scheduler stats
        jobs = self.scheduler.list_jobs()
        print(f"Scheduled jobs: {len(jobs)}")
        
        print(f"Python version: {sys.version.split()[0]}")
        print(f"Working directory: {os.getcwd()}")
    
    def _handle_memory(self, args) -> None:
        """Handle memory commands."""
        if args.memory_command == "add":
            success = self.memory.add(args.key, args.value)
            if success:
                print(f"Memory added: {args.key}")
            else:
                print(f"Failed to add memory: {args.key}")
        elif args.memory_command == "get":
            memory = self.memory.get(args.key)
            if memory:
                print(f"Key: {memory['key']}")
                print(f"Value: {memory['value']}")
                print(f"Created: {memory['created_at']}")
                print(f"Updated: {memory['updated_at']}")
            else:
                print(f"Memory not found: {args.key}")
        elif args.memory_command == "list":
            keys = self.memory.list_keys()
            print("Memory entries:")
            for key in keys:
                print(f"  - {key}")
        elif args.memory_command == "search":
            results = self.memory.search(args.query)
            print(f"Search results for '{args.query}':")
            for result in results:
                print(f"  - {result['key']}: {result['value'][:50]}...")
    
    def _handle_scheduler(self, args) -> None:
        """Handle scheduler commands."""
        if args.schedule_command == "add":
            self.scheduler.add_interval_job(args.job_id, args.seconds, print, f"Job {args.job_id} executed")
            print(f"Job added: {args.job_id} (every {args.seconds}s)")
        elif args.schedule_command == "list":
            jobs = self.scheduler.list_jobs()
            print("Scheduled jobs:")
            for job in jobs:
                print(f"  - {job['id']}: {job['type']} ({job['schedule']}) next: {job['next_run']}")


def main():
    """Main entry point."""
    cli = DinoCLI()
    cli.run()


if __name__ == "__main__":
    main()
