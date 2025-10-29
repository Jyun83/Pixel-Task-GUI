import os

from typing import Optional, Set
from task_manager import TaskManager
from notifier import send_notification

def clear_screen():
    # os.system('cls' if os.name == 'nt' else 'clear')  for other mac users
    os.system('clear')


def notify_due_tasks(manager: TaskManager, notified: Optional[Set[str]] = None) -> None:
    """
    Checks all tasks once and sends notifications for overdue or soon-due tasks.
    
    Args:
        manager (TaskManager): The TaskManager instance containing all tasks.
        notified (Optional[Set[str]], optional): A set of task titles already notified
            to prevent duplicate notifications. If None, a new empty set is used.

    Returns:
        None
    """
    if notified is None:
        notified = set()

    for task in manager.tasks:
        if task.due_date and task.is_not_completed():
            # Notify overdue tasks
            if task.is_overdue() and task.title not in notified:
                send_notification(
                    "Overdue Task",
                    f"'{task.title}' is past due! ({task.due_date})"
                )
                notified.add(task.title)

            # Notify tasks due soon (1 day before)
            elif task.is_due_soon(1) and task.title not in notified:
                send_notification(
                    "Task Reminder",
                    f"'{task.title}' is due tomorrow! ({task.due_date})"
                )
                notified.add(task.title)
