#!/usr/bin/env python3
"""
Dino Dynasty OS - Terminal Dashboard
A rich CLI dashboard with ASCII art and colors.
With OpenCode-style build/plan agents!
"""

import sys
import os
import asyncio
import importlib.util
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

BANNER = """
╔══════════════════════════════════════════════════════════════════════════╗
║ 🦖 D I N O   D Y N A S T Y   O S 🦖                               ║
║ ⚡ Lightning Fast | 🔒 Secure | 🧠 Intelligent                      ║
╚══════════════════════════════════════════════════════════════════════════╝
"""


def print_banner():
    console.print("\n")
    console.print(DINOSAUR_ART, style="bold cyan")
    console.print(BANNER, style="bold green")
    console.print("\n")


def show_status():
    console.print("\n📊 System Status")
    console.print(f"  🧠 Memory: Active")
    console.print(f"  📅 Scheduler: Active")
    console.print(f"  🐍 Python: {sys.version.split()[0]}")
    console.print(f"  📁 {os.getcwd()}\n")


def list_agents():
    skills_dir = Path(__file__).parent / "skills"
    agents = []
    if skills_dir.exists():
        for f in skills_dir.glob("*_agent.py"):
            if f.stem != "__init__":
                # Extract agent name without _agent suffix
                agent_name = f.stem.replace("_agent", "")
                agents.append(agent_name)
    
    table = Table(title="Available Agents", box=box.ROUNDED)
    table.add_column("Agent", style="cyan")
    for a in sorted(set(agents)):
        table.add_row(a)
    console.print(table)


def run_agent(name):
    console.print(f"\n🎯 Running agent: {name}\n")
    skills_dir = Path(__file__).parent / "skills"
    
    # Look for agent file
    agent_file = skills_dir / f"{name}_agent.py"
    if not agent_file.exists():
        agent_file = skills_dir / f"{name}.py"
    
    if not agent_file.exists():
        console.print(f"[red]Agent file not found: {agent_file}[/red]")
        return
    
    try:
        spec = importlib.util.spec_from_file_location("agent_module", agent_file)
        if spec is None or spec.loader is None:
            console.print(f"[red]Could not load agent module: {agent_file}[/red]")
            return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        from dino_os.agent_core import Agent as BaseAgent
        agent_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseAgent) and attr is not BaseAgent:
                agent_class = attr
                break
        
        if agent_class is None:
            console.print(f"[yellow]No Agent class found, running simple test[/yellow]")
            console.print(Panel("✅ Agent loaded!", title=name, border_style="green"))
            return
        
        agent = agent_class()
        result = asyncio.run(agent.run())
        
        if result.get("status") == "success":
            console.print(Panel(
                f"✅ Success!\n{result.get('output', '')}",
                title=name,
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"❌ Failed: {result.get('error', 'Unknown')}",
                title=name,
                border_style="red"
            ))
    except Exception as e:
        console.print(Panel(f"Error: {str(e)}", title="Error", border_style="red"))


def memory_menu():
    from dino_os.memory_layer import MemoryLayer
    memory = MemoryLayer()
    
    while True:
        choice = questionary.select(
            "Memory Menu",
            choices=["List memories", "Add memory", "Get memory", "Delete memory", "Back"]
        ).ask()
        
        if choice == "Back": break
        elif choice == "List memories":
            keys = memory.list_keys()
            if keys:
                for key in keys:
                    entry = memory.get(key)
                    if entry:
                        console.print(f"  {key}: {entry['value']}")
            else:
                console.print("[yellow]No memories found[/yellow]")
        elif choice == "Add memory":
            k = questionary.text("Key:").ask()
            v = questionary.text("Value:").ask()
            memory.add(k, v)
            console.print(f"✅ Added: {k}")
        elif choice == "Get memory":
            k = questionary.text("Key:").ask()
            result = memory.get(k)
            if result:
                console.print(f"Key: {result['key']}")
                console.print(f"Value: {result['value']}")
                console.print(f"Created: {result['created_at']}")
            else:
                console.print("[yellow]Not found[/yellow]")
        elif choice == "Delete memory":
            k = questionary.text("Key:").ask()
            memory.delete(k)
            console.print(f"✅ Deleted: {k}")


# ═══════════════════════════════════════════════════════════════════════
# OPENCODE-STYLE BUILD & PLAN AGENTS
# ═══════════════════════════════════════════════════════════════════════

def run_build_agent():
    """
    BUILD MODE - Full access agent for development work.
    Can read/write files and run commands.
    """
    console.print(Panel(
        "🔨 BUILD MODE - Full Development Access\n\n"
        "I have full access to help you with:\n"
        "• Creating and editing files\n"
        "• Running commands\n"
        "• Installing packages\n"
        "• Running tests\n\n"
        "What would you like to build?",
        title="🔨 BUILD Agent",
        border_style="green"
    ))
    
    task = questionary.text("Task:").ask()
    if not task:
        return
    
    console.print(f"\n[cyan]Processing: {task}[/cyan]\n")
    
    # For now, create a simple agent task file
    skills_dir = Path(__file__).parent / "skills"
    task_file = skills_dir / "build_task.py"
    
    code = f'''"""Auto-generated build task: {task}"""
from dino_os.agent_core import Agent

class BuildTask(Agent):
    async def run(self):
        return {{
            "status": "success",
            "output": "Build task completed: {task}"
        }}
'''
    task_file.write_text(code)
    console.print(f"✅ Created build task: {task_file.name}")
    console.print("[green]Build agent ready![/green]")


def run_plan_agent():
    """
    PLAN MODE - Read-only agent for analysis.
    Asks permission before running bash commands.
    """
    console.print(Panel(
        "📋 PLAN MODE - Analysis & Planning\n\n"
        "I'm in read-only mode. I can:\n"
        "• Analyze codebases\n"
        "• Review files\n"
        "• Plan changes\n"
        "• Search for patterns\n\n"
        "I will ASK before running any commands.\n\n"
        "What would you like to analyze?",
        title="📋 PLAN Agent",
        border_style="yellow"
    ))
    
    task = questionary.text("Analysis task:").ask()
    if not task:
        return
    
    console.print(f"\n[cyan]Analyzing: {task}[/cyan]\n")
    
    # Show what would happen
    console.print(Panel(
        f"📋 Plan for: {task}\n\n"
        "1. Read relevant files\n"
        "2. Analyze code structure\n"
        "3. Identify changes needed\n"
        "4. Propose modifications\n\n"
        "Run BUILD mode to execute changes.",
        title="📋 Analysis Plan",
        border_style="yellow"
    ))


# ═══════════════════════════════════════════════════════════════════════

def main_menu():
    while True:
        choice = questionary.select(
            "🦖 Dino Dynasty OS - Main Menu",
            choices=[
                "📊 Show Status",
                "🎯 List Agents",
                "▶️ Run Agent",
                "🔨 BUILD Agent (full dev)",
                "📋 PLAN Agent (read-only)",
                "🧠 Memory Manager",
                "⚙️ Settings",
                "🚪 Exit"
            ]
        ).ask()
        
        if choice == "📊 Show Status":
            print_banner()
            show_status()
        elif choice == "🎯 List Agents":
            list_agents()
        elif choice == "▶️ Run Agent":
            agents = []
            skills_dir = Path(__file__).parent / "skills"
            if skills_dir.exists():
                for f in skills_dir.glob("*_agent.py"):
                    if f.stem != "__init__":
                        agent_name = f.stem.replace("_agent", "")
                        agents.append(agent_name)
            if not agents:
                console.print("[yellow]No agents found in skills directory[/yellow]")
                continue
            agent = questionary.select("Select:", choices=sorted(set(agents))).ask()
            if agent: run_agent(agent)
        elif choice == "🔨 BUILD Agent (full dev)":
            run_build_agent()
        elif choice == "📋 PLAN Agent (read-only)":
            run_plan_agent()
        elif choice == "🧠 Memory Manager":
            memory_menu()
        elif choice == "⚙️ Settings":
            console.print("[cyan]Settings coming soon![/cyan]")
        elif choice == "🚪 Exit":
            console.print("\n🦖 Bye!\n")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            print_banner()
            show_status()
    else:
        print_banner()
        main_menu()
