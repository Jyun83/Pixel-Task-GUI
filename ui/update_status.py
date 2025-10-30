from InquirerPy import inquirer

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from utils.helpers import clear_screen
from ui.view_tasks import view_tasks_interface
from task_manager import TaskManager

console = Console()
manager = TaskManager()
def show_simple_task_list() -> None:
    """
    Display a simple list of all tasks with only title, due date, and status.
    """
    clear_screen()
    tasks = manager.view_tasks()

    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        input("\nPress [Enter] to return...")
        return

    console.print(Panel("[bold cyan]All Tasks (Summary)[/bold cyan]", border_style="cyan"))

    for idx, t in enumerate(tasks, start=1):
        console.print(
            f"[bold white]{idx}. {t.title}[/bold white]\n"
            f"   -  Due Date: [magenta]{t.due_date}[/magenta]\n"
            f"   -  Status: [green]{t.status}[/green]\n"
        )
    
    input("\nPress [Enter] to return...")

def update_status_interface() -> None:
    """
    Allows user to update the status of a specific task.
    """
    clear_screen()

    task_titles = [t.title for t in manager.view_tasks()]
    if not task_titles:
        console.print("[yellow]No tasks found.[/yellow]")
        input("\nPress [Enter] to return...")
        return

    # Let user search and select title with TAB / arrow keys
    title = inquirer.fuzzy(  # type: ignore
        message="Select a task to update:",
        choices=task_titles,
        default=None,
        multiselect=False,
        height=10,
    ).execute()


    task = manager.find_task(title)

    if not task:
        console.print("[red]Task not found.[/red]")
        input("\nPress [Enter] to return...")
        return


    new_status = inquirer.select( #type: ignore
        message =  "Enter new status (Pending/In Progress/Completed)", 
        choices = ["Not Yet", "Pending", "Completed"],
        default=task.status
    ).execute()
    manager.edit_task(task.title, {"status": new_status})
    console.print("[green]Task status updated successfully![/green]")
    input("\nPress [Enter] to return...")

def update_menu() -> None:
    """
    Displays the update menu interface for viewing and updating task statuses.
    """
    clear_screen()
    while True:
        console.print(Panel(
            "[bold cyan]Update Menu[/bold cyan]\n"
            "1. View All Tasks\n"
            "2. Update Task Status\n"
            "3. Back",
        ))

        choice = Prompt.ask("Select an option")
        if choice == "1":
            show_simple_task_list()

        elif choice == "2":
            update_status_interface()
        elif choice == "3":
            break
        else:
            console.print("[red]Invalid option![/red]")
