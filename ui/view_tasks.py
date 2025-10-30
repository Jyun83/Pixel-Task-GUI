from typing import Optional, Tuple, List
from datetime import datetime

from InquirerPy import inquirer

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel

from utils.helpers import clear_screen
from task_manager import TaskManager, Task

console = Console()
manager = TaskManager()

def view_tasks_interface() -> None:
    """
    Display all tasks in a table and allow the user to view details of individual tasks.

    This function:
        Clears the screen before displaying tasks.
        Shows all tasks in a formatted table with columns: Title, Due Date, Status, Folder.
        If no tasks exist, displays a message and waits for user input.
        Prompts the user to view details for a specific task:
            Displays task details in a panel if the task exists.
            Shows an error message if the task is not found.
        Allows the user to return to the task list or exit the view.

    Args:
        None

    Returns:
        None
    """
    # Ask user if they want to filter
    filter_by: Optional[Tuple[str, str]] = None
    sort_order: Optional[str] = None

    # Ask for filter
    filter_choice: str = inquirer.select( #type: ignore
        message="Filter tasks by attribute?",
        choices=["due_date", "status", "none"],
        default="none"
    ).execute()

    if filter_choice == "status":
        value: str = inquirer.select( #type: ignore
            message="Select status to filter:",
            choices=["Not Yet", "Pending", "Completed"]
        ).execute()
        filter_by = ("status", value)

    elif filter_choice == "due_date":
        sort_order = inquirer.select( #type: ignore
            message="Sort by due date:",
            choices=["asc", "desc"],
            default="asc"
        ).execute()


    tasks = manager.view_tasks(filter_by)  # filter tasks if any

    if sort_order:  # sort if needed
        tasks.sort(key=lambda t: datetime.strptime(t.due_date, "%Y-%m-%d"),
                reverse=(sort_order == "desc"))

    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        input("\nPress [Enter] to return...")
        return
    
    # Build Table
    table = Table(title="Task List", show_lines=True)
    table.add_column("Title", style="cyan", justify="center")
    table.add_column("Due Date", style="magenta", justify="center")
    table.add_column("Status", style="green", justify="center")
    table.add_column("Folder", style="blue", justify="center")

    for t in tasks:
        table.add_row(t.title, t.due_date, t.status, t.folder or "-")

    console.print(table)
    
    # View Details for a specific task
    view_more = inquirer.confirm(# type: ignore
        message = "View Details for a specific task").execute()
    
    while view_more:

        title = Prompt.ask("[bold white]Enter the title of the task to view[/bold white]")
        task = manager.find_task(title)

        if not task:
            console.print(f"[red]Task '{title}' not found.[/red]")
        else:
            clear_screen()
            console.print(Panel(f"[bold cyan]Task Details[/bold cyan]", border_style="cyan"))
            console.print(f"[bold white]Title:[/bold white] {task.title}")
            console.print(f"[bold white]Description:[/bold white] {task.description or '-'}")
            console.print(f"[bold white]Status:[/bold white] {task.status}")
            console.print(f"[bold white]Due Date:[/bold white] {task.due_date}")
            console.print(f"[bold white]Folder:[/bold white] {task.folder or '-'}")
            console.print(f"[bold white]Tags:[/bold white] {', '.join(task.tags) or '-'}")

            input("\nPress [Enter] to return to task list...")
            clear_screen()
            console.print(Panel("[bold cyan]All Tasks[/bold cyan]", border_style="cyan"))
            console.print(table)
            
            view_more = inquirer.confirm(# type: ignore 
                message = "View Details for a specific task").execute()

    input("\nPress [Enter] to return...")