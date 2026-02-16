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
    from rich.text import Text
    from rich import box
except ImportError:
    print("Installing rich and questionary...")
    os.system("pip install rich questionary -q")
    import questionary
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box

from dino_os.config import Config
from dino_os.agent_core import Agent
from dino_os.memory_layer import MemoryLayer
from dino_os.scheduler import Scheduler

console = Console()



# ASCII Art
DINOSAUR_ART = """
████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗     
╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║     
   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║     
   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║     
   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
        ██████╗ ███████╗██╗   ██╗
        ██╔══██╗██╔════╝██║   ██║
        ██║  ██║█████╗  ██║   ██║
        ██║  ██║██╔══╝  ╚██╗ ██╔╝
        ██████╔╝███████╗ ╚████╔╝ 
        ╚═════╝ ╚══════╝  ╚═══╝  
"""

def print_banner():
    console.print("\n")
    console.print(DINOSAUR_ART, style="bold cyan")
    title_text = Text("🦖 D I N O   D Y N A S T Y   O S 🦖", style="bold green", justify="center")
    sub_text = Text("⚡ Lightning Fast | 🔒 Secure | 🧠 Intelligent", style="bold yellow", justify="center")
    banner_body = Text()
    banner_body.append_text(title_text)
    banner_body.append("\n")
    banner_body.append_text(sub_text)
    console.print(Panel(banner_body, box=box.DOUBLE, border_style="green", padding=(1, 2)))
    console.print("\n")


def show_status():
    memory = MemoryLayer()
    scheduler = Scheduler()
    memory_entries = memory.count()
    jobs = scheduler.list_jobs()
    
    table = Table(title="📊 System Status", box=box.ROUNDED)
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    table.add_row("🧠 Memory", "✅ Active", f"{memory_entries} entries")
    table.add_row("📅 Scheduler", "✅ Active", f"{len(jobs)} jobs")
    table.add_row("🐍 Python", "✅ Running", f"{sys.version.split()[0]}")
    table.add_row("📁 Working Dir", "✅ Set", os.getcwd())
    console.print(table)


def list_agents():
    agents_dir = Path(__file__).parent / "skills"
    if not agents_dir.exists():
        console.print("[red]No skills folder found![/red]")
        return
    agents = []
    for f in agents_dir.glob("*.py"):
        if f.stem != "__init__":
            agents.append(f.stem)
    table = Table(title="🎯 Available Agents", box=box.ROUNDED)
    table.add_column("Agent Name", style="cyan")
    table.add_column("Description", style="green")
    for agent in sorted(agents):
        table.add_row(f"🤖 {agent}", "Custom agent")
    if not agents:
        table.add_row("hello", "Default hello agent")
    console.print(table)


def run_agent(name):
    console.print(f"\n[bold cyan]Running agent: {name}[/bold cyan]\n")
    
    # Load agent from skills directory
    import importlib.util
    skills_dir = Path(__file__).parent / "skills"
    # Look for agent file (name.py or name_agent.py)
    agent_file = skills_dir / f"{name}.py"
    if not agent_file.exists():
        agent_file = skills_dir / f"{name}_agent.py"
    if not agent_file.exists():
        agent_file = skills_dir / f"hello_agent.py"  # fallback
    
    if not agent_file.exists():
        console.print(f"[red]Agent file not found: {agent_file}[/red]")
        return
    
    try:
        spec = importlib.util.spec_from_file_location(f"{name}_agent", agent_file)
        if spec is None or spec.loader is None:
            console.print(f"[red]Could not load agent module: {name}[/red]")
            return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the Agent subclass
        from dino_os.agent_core import Agent as BaseAgent
        agent_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, BaseAgent) and 
                attr is not BaseAgent):
                agent_class = attr
                break
        
        if agent_class is None:
            console.print(f"[red]No Agent subclass found in {name}[/red]")
            return
        
        agent = agent_class()
        
        # Run the async agent
        import asyncio
        result = asyncio.run(agent.run())
        
        if result.get("status") == "success":
            console.print(Panel(
                f"✅ [green]Agent completed successfully![/green]\n{result.get('output', '')}",
                title=f"🎉 {name}",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"❌ [red]Agent failed![/red]\n{result.get('error', 'Unknown error')}",
                title=f"🚫 {name}",
                border_style="red"
            ))
    except Exception as e:
        console.print(f"[red]Error running agent: {e}[/red]")


def memory_menu():
    memory = MemoryLayer()
    while True:
        choice = questionary.select(
            "🧠 Memory Menu",
            choices=["List all memories", "Add a memory", "Get a memory", "Delete a memory", "← Back to main menu"]
        ).ask()
        if choice == "← Back to main menu":
            break
        elif choice == "List all memories":
            keys = memory.list_keys()
            if keys:
                table = Table(title="💾 Memory Entries", box=box.ROUNDED)
                table.add_column("Key", style="cyan")
                table.add_column("Value", style="green")
                for key in keys:
                    entry = memory.get(key)
                    if entry:
                        table.add_row(key, str(entry['value'])[:50])
                console.print(table)
            else:
                console.print("[yellow]No memory entries![/yellow]")
        elif choice == "Add a memory":
            key = questionary.text("Enter key:").ask()
            value = questionary.text("Enter value:").ask()
            memory.add(key, value)
            console.print(f"[green]✅ Added: {key}[/green]")
        elif choice == "Get a memory":
            key = questionary.text("Enter key:").ask()
            value = memory.get(key)
            if value:
                console.print(Panel(str(value), title=f"📤 {key}", border_style="cyan"))
            else:
                console.print(f"[red]Key not found: {key}[/red]")
        elif choice == "Delete a memory":
            key = questionary.text("Enter key to delete:").ask()
            memory.delete(key)
            console.print(f"[green]✅ Deleted: {key}[/green]")


def main_menu():
    while True:
        choice = questionary.select(
            "🦖 Dino Dynasty OS - Main Menu",
            choices=["📊 Show Status", "🎯 List Agents", "▶️ Run Agent", "🧠 Memory Manager", "⚙️ Settings", "🚪 Exit"]
        ).ask()
        if choice == "📊 Show Status":
            print_banner()
            show_status()
        elif choice == "🎯 List Agents":
            list_agents()
        elif choice == "▶️ Run Agent":
            agents = ["hello"]
            skills_dir = Path(__file__).parent / "skills"
            if skills_dir.exists():
                for f in skills_dir.glob("*.py"):
                    if f.stem != "__init__":
                        agents.append(f.stem)
            agent = questionary.select("Select agent:", choices=agents).ask()
            if agent:
                run_agent(agent)
        elif choice == "🧠 Memory Manager":
            memory_menu()
        elif choice == "⚙️ Settings":
            console.print("[cyan]Settings coming soon![/cyan]")
        elif choice == "🚪 Exit":
            console.print("\n[bold cyan]🦖 Bye! See you next time![/bold cyan]\n")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        print_banner()
        show_status()
    elif len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_agents()
    else:
        print_banner()
        main_menu()
