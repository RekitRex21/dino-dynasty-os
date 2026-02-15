#!/usr/bin/env python3
"""
Dino Dynasty OS - Terminal Dashboard
A rich CLI dashboard with ASCII art and colors.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    import questionary
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
except ImportError:
    print("Installing rich and questionary...")
    os.system("pip install rich questionary -q")
    import questionary
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box

from dino_os.config import Config
from dino_os.agent_core import Agent
from dino_os.memory_layer import MemoryLayer
from dino_os.scheduler import Scheduler

console = Console()

DINOSAUR_ART = """
                       __
                      / _)
                     / /
           __   __  / /      ___   _   __
          / _\ / _ \/ /_    / _ \ | | / /
         / // // __/ __ \  / // / | |/ /
        /____/ \___/_/ |_| /____/  |___/
"""

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║  D I N O   D Y N A S T Y   O S                                ║
║  Lightning Fast | Secure | Smart                                ║
╚══════════════════════════════════════════════════════════════════╝
"""


def print_banner():
    console.print("\n")
    console.print(DINOSAUR_ART, style="bold green")
    console.print(BANNER, style="bold cyan")
    console.print("\n")


def show_status():
    config = Config()
    memory = MemoryLayer(config)
    scheduler = Scheduler(config)
    memory_entries = len(memory.list())
    jobs = scheduler.list_jobs()
    
    table = Table(title="System Status", box=box.ROUNDED)
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    table.add_row("Memory", "Active", f"{memory_entries} entries")
    table.add_row("Scheduler", "Active", f"{len(jobs)} jobs")
    table.add_row("Python", "Running", f"{sys.version.split()[0]}")
    table.add_row("Working Dir", "Set", os.getcwd())
    console.print(table)


def list_agents():
    agents_dir = Path(__file__).parent / "skills"
    agents = ["hello"]
    if agents_dir.exists():
        for f in agents_dir.glob("*.py"):
            if f.stem != "__init__":
                agents.append(f.stem)
    
    table = Table(title="Available Agents", box=box.ROUNDED)
    table.add_column("Agent", style="cyan")
    for a in sorted(set(agents)):
        table.add_row(a)
    console.print(table)


def run_agent(name):
    console.print(f"\nRunning agent: {name}\n")
    config = Config()
    agent = Agent(name, config)
    result = agent.run()
    if result.get("status") == "success":
        console.print(Panel(f"Success: {result.get('output', '')}", title=name, border_style="green"))
    else:
        console.print(Panel(f"Failed: {result.get('error', '')}", title=name, border_style="red"))


def memory_menu():
    config = Config()
    memory = MemoryLayer(config)
    
    while True:
        choice = questionary.select(
            "Memory Menu",
            choices=["List memories", "Add memory", "Get memory", "Delete memory", "Back"]
        ).ask()
        
        if choice == "Back": break
        elif choice == "List memories":
            entries = memory.list()
            for k, v in entries.items(): console.print(f"{k}: {v}")
        elif choice == "Add memory":
            k = questionary.text("Key:").ask()
            v = questionary.text("Value:").ask()
            memory.add(k, v)
            console.print(f"Added: {k}")
        elif choice == "Get memory":
            k = questionary.text("Key:").ask()
            console.print(memory.get(k, "Not found"))
        elif choice == "Delete memory":
            k = questionary.text("Key:").ask()
            memory.delete(k)
            console.print(f"Deleted: {k}")


def main_menu():
    while True:
        choice = questionary.select(
            "Dino Dynasty OS",
            choices=["Show Status", "List Agents", "Run Agent", "Memory Manager", "Exit"]
        ).ask()
        
        if choice == "Show Status":
            print_banner()
            show_status()
        elif choice == "List Agents":
            list_agents()
        elif choice == "Run Agent":
            agents = ["hello"]
            skills_dir = Path(__file__).parent / "skills"
            if skills_dir.exists():
                for f in skills_dir.glob("*.py"):
                    if f.stem != "__init__":
                        agents.append(f.stem)
            agent = questionary.select("Select:", choices=list(set(agents))).ask()
            if agent: run_agent(agent)
        elif choice == "Memory Manager":
            memory_menu()
        elif choice == "Exit":
            console.print("\nBye!\n")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            print_banner()
            show_status()
    else:
        print_banner()
        main_menu()
