# utils/background.py
import time
import threading
from typing import Optional
from task_manager import TaskManager
from notifier import send_notification

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
        interval (int, optional): Number of seconds to wait between checks. Defaults to 60. (for testing)
        stop_flag (Optional[threading.Event], optional): 
            Thread-safe event to signal stopping
            the loop. If None, the loop runs indefinitely. Defaults to None.

    Returns:
        None
    """
    notified = set()  # Keep track of tasks already notified

    while stop_flag is None or not stop_flag.is_set():
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

        time.sleep(interval)
