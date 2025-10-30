import time

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from pyfiglet import Figlet

from utils.helpers import clear_screen

console = Console()

def show_startup() -> None:
    """
    Displays the startup screen with an ASCII art banner and a loading animation.

    This function clears the screen, shows the program banner, displays
    a short progress bar animation, and prepares the interface for the main menu.
    """
    clear_screen()

    # Render the ASCII banner
    f = Figlet(font="standard")
    banner = f.renderText("Task Manager")
    console.print(f"[bold cyan]{(banner)}[/bold cyan]")

    # Welcome message
    console.print("[bold white]Welcome to your personal task dashboard![/bold white]")
    console.print("[green]Manage your work, deadlines, and focus with style.[/green]\n")

    # Loading bar animation
    with Progress(
        TextColumn("[bold cyan]Loading...[/bold cyan]"),
        BarColumn(bar_width=None),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True,  # hides after completion
    ) as progress:
        task = progress.add_task("Loading", total=100)
        for _ in range(100):
            time.sleep(0.02)
            progress.update(task, advance=1)

    console.print("[bold green]Ready! Launching main menu...[/bold green]")
    time.sleep(1)
    clear_screen()
