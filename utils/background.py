# utils/background.py
import time
import threading

from typing import Optional, Set
from task_manager import TaskManager
from .helpers import notify_due_tasks

def start_background_notifier(
    manager: TaskManager,
    interval: int = 60,
    stop_flag: Optional[threading.Event] = None
) -> None:
    """
    Continuously checks tasks in the TaskManager and sends notifications for overdue or
    soon-due tasks. Designed to be run in a background thread.

    Args:
        manager (TaskManager): Instance of TaskManager containing all tasks.
        interval (int, optional): Number of seconds to wait between checks. Defaults to 60.
        stop_flag (Optional[threading.Event], optional): Thread-safe event to signal stopping
            the loop. If None, the loop runs indefinitely. Defaults to None.

    Returns:
        None
    """
    notified: Set[str] = set()  # Keep track of tasks already notified
    
    while stop_flag is None or not stop_flag.is_set():
        manager = TaskManager()
        manager.load_tasks()
        notify_due_tasks(manager, notified)
        time.sleep(interval)