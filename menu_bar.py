import rumps
import subprocess
import threading

import time
from typing import Optional

from task_manager import TaskManager
from utils.background import start_background_notifier


class TaskMenuBar(rumps.App):
    """A macOS menu bar application for managing and receiving task notifications.

    This app provides a simple system tray interface that integrates with
    the `TaskManager` class. Users can:
    - Open a CLI-based task manager.
    - Enable or disable background notifications.
    - Quit the app from the menu bar.
    """

    def __init__(self) -> None:
        """Initialize the menu bar application and its attributes."""
        super(TaskMenuBar, self).__init__("Tasks", quit_button=None) # type: ignore
        self.manager: TaskManager = TaskManager()
        self.notification_on: bool = False
        self.bg_thread: Optional[threading.Thread] = None

        # Define menu items displayed in the macOS menu bar.
        self.menu = [
            "Open CLI Task Manager",
            "Turn On Notifications",
            None,
            "Quit",
        ]

    @rumps.clicked("Open CLI Task Manager")
    def open_cli(self, _: rumps.MenuItem) -> None:
        """Open the CLI version of the task manager in a new subprocess.

        Args:
            _: rumps.MenuItem
                The clicked menu item (unused, but required by the decorator).
        """
        try:
            subprocess.Popen(["python3", "menu_cli.py"], start_new_session=True)
        except FileNotFoundError:
            rumps.alert("Error", "GUI.py not found. Please check the file path.")

    @rumps.clicked("Turn On Notifications")
    def toggle_notifications(self, sender: rumps.MenuItem) -> None:
        """Toggle the background notification feature on or off.

        Args:
            sender (rumps.MenuItem): The clicked menu item that triggered the event.
        """
        if not self.notification_on:
            self.notification_on = True
            sender.title = "Turn Off Notifications"
            rumps.notification(
                "Notifications Enabled", "", "Task reminders are now active!"
            )

            # Run notification loop in the background thread
            self.bg_thread = threading.Thread(
                target=self.notification_loop, daemon=True
            )
            self.bg_thread.start()
        else:
            self.notification_on = False
            sender.title = "Turn On Notifications"
            rumps.notification(
                "Notifications Disabled", "", "No reminders will be sent."
            )

    def notification_loop(self) -> None:
        """Run background checks for due tasks every few minutes."""
        while self.notification_on:
            try:
                start_background_notifier(self.manager)
                print("Checking tasks in background...")
            except Exception as e:
                print(f"[Error in notifier] {e}")
            time.sleep(120)  # Check every 2 minutes

    @rumps.clicked("Quit")
    def quit_app(self, _: rumps.MenuItem) -> None:
        """Quit the application and display a closing notification.

        Args:
            _: rumps.MenuItem
                The clicked menu item (unused).
        """
        rumps.notification("Exiting", "", "Task Manager closed.")
        rumps.quit_application()


if __name__ == "__main__":
    TaskMenuBar().run()
