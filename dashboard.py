#!/usr/bin/env python3
"""
Dino Dynasty OS - Terminal Dashboard
A rich CLI dashboard with ASCII art and colors.
"""

import sys
import os
import shutil
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

# Get terminal size for dynamic width
def get_terminal_size():
    cols, rows = shutil.get_terminal_size()
    return int(cols * 0.8), rows - 15

DINOSAUR_ART = """
                       __
                      / _)
                     / /
           __   __  / /      ___   _   __
          / _\\ / _ \\/ /_    / _ \\ | | / /
         / // // __/ __ \\  / // / | |/ /
        /____/ \\___/_/ |_| /____/  |___/
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


def ascii_art_menu():
    """ASCII Art Generator - matches Dino aesthetic"""
    from PIL import Image, ImageEnhance
    
    while True:
        choice = questionary.select(
            "ASCII Art Generator",
            choices=["Generate from image", "Set width", "Set contrast", "Back"]
        ).ask()
        
        if choice == "Back": break
        elif choice == "Generate from image":
            path = questionary.text("Image path:").ask()
            if path and os.path.exists(path):
                try:
                    # Dynamic width calculation
                    width, height = get_terminal_size()
                    
                    # Dino aesthetic ramp
                    ascii_chars = "MW#Nxo:. "
                    
                    # Process image
                    img = Image.open(path)
                    aspect = img.height / img.width
                    new_height = int(width * aspect * 0.55)
                    new_height = min(new_height, height)  # Limit height
                    img = img.resize((width, new_height))
                    img = img.convert("L")
                    
                    # Contrast boost for Dino look
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.3)
                    
                    pixels = img.getdata()
                    bucket = 255 / (len(ascii_chars) - 1)
                    ascii_str = "".join(ascii_chars[int(p // bucket)] for p in pixels)
                    
                    lines = [ascii_str[i:i+width] for i in range(0, len(ascii_str), width)]
                    
                    console.print("\n\033[32m" + "\n".join(lines) + "\033[0m\n")
                except Exception as e:
                    console.print(f"Error: {e}")
            else:
                console.print("File not found")
        elif choice == "Set width":
            console.print("Width is automatically calculated based on terminal size")
        elif choice == "Set contrast":
            console.print("Contrast is auto-boosted to 1.3 for Dino aesthetic")


def main_menu():
    while True:
        choice = questionary.select(
            "Dino Dynasty OS",
            choices=["Show Status", "List Agents", "Run Agent", "Memory Manager", "ASCII Art", "Exit"]
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
        elif choice == "ASCII Art":
            ascii_art_menu()
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
