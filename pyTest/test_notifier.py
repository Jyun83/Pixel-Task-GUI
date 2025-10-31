# tests/test_notifier.py
import pytest
from unittest.mock import patch

import threading
import time
from typing import Set, Optional

from task import Task
from task_manager import TaskManager
from notifier import send_notification
from utils.background import start_background_notifier
from utils.helpers import notify_due_tasks

@pytest.fixture
def sample_manager() -> TaskManager:
    """
    Provides a TaskManager instance with sample tasks for testing notifications.

    Returns:
        TaskManager: Instance containing overdue and due-soon tasks.
    """
    manager = TaskManager()
    # Task overdue in the past
    manager.tasks.append(Task("Overdue Task", "desc", "2000-01-01", []))
    # Task due soon (adjust date to match is_due_soon logic if needed)
    manager.tasks.append(Task("Due Soon Task", "desc", "2099-12-31", []))
    return manager



def test_send_notification_calls_subprocess() -> None:
    """
    Tests that send_notification calls subprocess.run with the correct arguments.
    """
    with patch("subprocess.run") as mock_run:
        send_notification("Hello", "World")

        # Verify subprocess.run was called once
        mock_run.assert_called_once_with([
            "osascript", "-e",
            'display notification "World" with title "Hello" sound name "Ping" '
        ])



# def test_notify_due_tasks_calls_send_notification(sample_manager: TaskManager) -> None:
#     """
#     Tests that notify_due_tasks calls send_notification for tasks that are overdue or due soon.

#     Args:
#         sample_manager (TaskManager): Fixture containing sample tasks.

#     Returns:
#         None
#     """
#     notified_set: Set[str] = set()

#     with patch("utils.helpers.send_notification") as mock_notify:
#         notify_due_tasks(sample_manager, notified_set)

#         # Assert that at least one notification was triggered
#         assert mock_notify.call_count >= 1

#         # check arguments of the first call
#         called_args = mock_notify.call_args[0]
#         assert "Task" in called_args[0]


# def test_start_background_notifier_runs_once(sample_manager: TaskManager) -> None:
#     """
#     Tests that start_background_notifier can run in a background thread and triggers notifications.

#     Args:
#         sample_manager (TaskManager): Fixture containing sample tasks.

#     Returns:
#         None
#     """
#     stop_flag: threading.Event = threading.Event()

#     with patch("utils.helpers.send_notification") as mock_notify:
#         def run_notifier() -> None:
#             start_background_notifier(sample_manager, interval=1, stop_flag=stop_flag)

#         thread = threading.Thread(target=run_notifier)
#         thread.start()

#         # Let the thread run briefly, then stop it
#         time.sleep(0.5)
#         stop_flag.set()
#         thread.join()

#         # Assert that at least one notification was triggered
#         assert mock_notify.call_count >= 1
