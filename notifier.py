import subprocess

def send_notification(title: str, message: str) -> None:
    """
    Sends a macOS desktop notification using AppleScript.

    Args:
        title (str): The title of the notification.
        message (str): The body message of the notification.

    Returns:
        None
    """
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "{title}" sound name "Ping" '
    ])
