import sys
from datetime import datetime
import os
import functools

# PyQt6
from PyQt6.QtCore import (
    Qt, pyqtSignal, QEasingCurve, QPoint, QTimer, QVariantAnimation,
    QPropertyAnimation, QUrl
)

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QScrollArea, QFrame, QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy,
    QGraphicsOpacityEffect, QHBoxLayout, QMessageBox, QDialog
)

from PyQt6.QtGui import QFont, QColor, QFontDatabase, QIcon 

from PyQt6.QtMultimedia import QSoundEffect

# Project
from task_manager import TaskManager
from task import Task
from notifier import send_notification
from utils.helpers import back_to_desktop
# Assuming loading_animation is available, otherwise it defaults to basic QWidget
try:
    from loading_animation import PixelLoadingOverlay # type: ignore
except ImportError:
    class PixelLoadingOverlay(QWidget):
        def __init__(self, duration):
            super().__init__()
            self.duration = duration
            self.setWindowTitle("LOADING...")
            self.resize(300, 100)
            self.setStyleSheet("background-color: black;")
            loading_label = QLabel("LOADING...", self)
            loading_label.setFont(QFont("Menlo", 24))
            loading_label.setStyleSheet("color: white;")
            loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            loading_label.resize(300, 100)
# =========================================================================

import pathlib

# Path to bundled font (relative path recommended)
font_path = os.path.join(os.path.dirname(__file__), "assets/DisposableDroidBB.ttf")
# Fallback font family name
FONT_NAME = "Menlo"

# --- Define the icon file name ---
ICON_FILE = "app_icon.png" 
# ---------------------------------

# --- Define the loading duration in milliseconds ---
LOADING_DURATION_MS = 3000 # 3 seconds
# -------------------------------------------------------


# Added parent argument to ensure QSoundEffect is correctly parented
def load_sound(filename, parent=None):
    path = pathlib.Path(__file__).parent/ "assets" / filename
    if not path.exists():
        print(f"Sound file not found: {path}")
        return None

    # Pass the parent to QSoundEffect to prevent segmentation fault
    sound = QSoundEffect(parent)
    sound.setSource(QUrl.fromLocalFile(str(path.resolve())))
    sound.setVolume(1)
    return sound


# ----------------- Base Styled Window ----------------- #
class StyledWindow(QWidget):
    """
    Base class for all windows, providing common styling, framelessness,
    always-on-top behavior, and animation/sound cleanup.
    """
    def __init__(self, title, width=800, height=600, top_padding=50):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(width, height)

        self.layout = QVBoxLayout() # type: ignore
        self.layout.setSpacing(15) # pyright: ignore[reportAttributeAccessIssue]
        self.layout.setContentsMargins(20, top_padding, 20, 20)  # type: ignore # top padding here
        self.setLayout(self.layout) # type: ignore

        # Initialize animation and sound holders
        if not hasattr(self, '_anims'):
            self._anims = []
        if not hasattr(self, '_sounds'):
            self._sounds = []

        # Load the dedicated 'menu_back.wav' for the Back to Menu button
        self.back_sound = load_sound("menu_back.wav", parent=self)
        self._sounds.append(self.back_sound) # Add to cleanup list
        
        # LOAD SUCCESS SOUND
        self.success_sound = load_sound("success.wav", parent=self)
        self._sounds.append(self.success_sound)
        # ==============================================


    def make_label(self, text, font_size=24):
        """Creates a stylized QLabel with a drop shadow."""
        lbl = QLabel(text)
        lbl.setFont(QFont(FONT_NAME, font_size))
        lbl.setStyleSheet("color: white;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor("black"))
        shadow.setOffset(0)
        lbl.setGraphicsEffect(shadow)
        return lbl


    def make_button(self, text, font_size=24):
            """Creates a stylized QPushButton with a glassmorphism look (used for sort buttons)."""
            btn = QPushButton(text)
            btn.setFont(QFont(FONT_NAME, font_size))
            
            btn.setStyleSheet(
                """
                QPushButton {
                    /* Base Glass Effect */
                    color: #FFFFFF;
                    /* Semi-transparent background (10% opacity) */
                    background-color: rgba(255, 255, 255, 0.1); 
                    /* Light, semi-transparent border (the 'glass' edge) */
                    border: 1px solid rgba(255, 255, 255, 0.4);
                    border-radius: 12px;
                    padding: 15px 30px; 
                    outline: 0px; 
                }
                
                QPushButton:hover {
                    /* Hover: Slightly increase brightness and border visibility */
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.8);
                }
                
                QPushButton:pressed {
                    /* Pressed: Darken to simulate being pressed into the surface */
                    background-color: rgba(0, 0, 0, 0.2);
                    border-style: inset;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }
                """
            )
            return btn

    def make_menu_button(self, text, font_size=24):
            """Creates a stylized QPushButton with a glassmorphism look, designed for the 'Back' function."""
            btn = QPushButton(text)
            btn.setFont(QFont(FONT_NAME, font_size))
                        
            btn.setStyleSheet(
                """
                QPushButton {
                    /* Base Glass Effect */
                    color: #FFFFFF;
                    /* Semi-transparent background (10% opacity) */
                    background-color: rgba(255, 255, 255, 0.1); 
                    /* Light, semi-transparent border (the 'glass' edge) */
                    border: 1px solid rgba(255, 255, 255, 0.4);
                    border-radius: 8px; /* Slightly smaller radius for the back button */
                    padding: 10px 20px; /* Smaller padding than main buttons */
                    outline: 0px; 
                }
                
                QPushButton:hover {
                    /* Hover: Slightly increase brightness and border visibility */
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.8);
                }
                
                QPushButton:pressed {
                    /* Pressed: Darken to simulate being pressed into the surface */
                    background-color: rgba(0, 0, 0, 0.2);
                    border-style: inset;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }
                """
            )
            return btn


    def make_back_button(self):
            """Creates a styled Back to Menu button at the bottom"""
            # Use the new glassmorphism style
            btn = self.make_menu_button("Back to Menu", 24)
            btn.clicked.connect(self._back_to_menu)
            
            self.layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter) # type: ignore
            
            return btn

    def _back_to_menu(self):
        """Show parent menu and close current window. **Plays self.back_sound (menu_back.wav)**"""
        # This now uses the dedicated back sound (menu_back.wav)
        if self.back_sound:
            self.back_sound.play()
            
        if hasattr(self, "parent_menu") and self.parent_menu: # type: ignore
            # Fade the current window out first for a smoother transition
            fade = QPropertyAnimation(self, b"windowOpacity", self)
            fade.setDuration(200)
            fade.setStartValue(1.0)
            fade.setEndValue(0.0)
            fade.setEasingCurve(QEasingCurve.Type.OutCubic)

            def after_fade():
                self.parent_menu.setWindowOpacity(1.0) # type: ignore # Ensure parent is fully opaque
                self.parent_menu.show() # type: ignore
                self.parent_menu.setFocus() # type: ignore # Ensure the carousel gets focus back
                self.close()

            fade.finished.connect(after_fade)
            self._anims.append(fade)
            fade.start()

        else:
            self.close()

    def cleanup(self):
        """
        Safely stop ongoing animations/sounds and schedule C++ objects for
        deletion to prevent segmentation faults.
        """
        # Stop animations
        if hasattr(self, "_anims"):
            for anim in self._anims:
                if isinstance(anim, (QPropertyAnimation, QVariantAnimation)):
                    try:
                        anim.stop()
                        # Explicitly schedule for deletion to prevent segfault on shutdown
                        anim.deleteLater()
                    except Exception:
                        pass
            # Clear reference list
            self._anims = []

        # Stop sounds (references stored in self._sounds)
        if hasattr(self, '_sounds'):
            for sound in self._sounds:
                if sound:
                    try:
                        sound.stop()
                        sound.deleteLater()
                    except Exception:
                        pass
            self._sounds = []

        for sound_attr in ["move_sound", "select_sound", "typing_sound", "back_sound", "error_sound", "success_sound"]:
            if hasattr(self, sound_attr) and getattr(self, sound_attr):
                try:
                    getattr(self, sound_attr).stop()
                    getattr(self, sound_attr).deleteLater()
                except Exception:
                    pass
                setattr(self, sound_attr, None)

    def closeEvent(self, event): # type: ignore
        """Override closeEvent to ensure cleanup runs on window close too."""
        self.cleanup()
        event.accept()
        
    def keyPressEvent(self, event): # type: ignore
        """Overrides keyPressEvent to allow navigation back to the parent menu via Esc key."""
        # Only handle the Escape key for navigation back to the parent menu.
        if event.key() == Qt.Key.Key_Escape:
            self._back_to_menu()
        else:
            # Allow other keys (like letter/number input in a QLineEdit) to be processed
            # by child widgets, while non-mapped keys are generally ignored by the window.
            super().keyPressEvent(event)

# ----------------- Base Wizard ----------------- #
class BaseWizard(StyledWindow):
    """Base class for multi-step input wizards."""
    def __init__(self, title, parent_menu=None):
        super().__init__(title)
        self.parent_menu = parent_menu
        if self.parent_menu:
            self.parent_menu.hide()

        self.layout.setSpacing(15) # type: ignore
        self.layout.setContentsMargins(20, 20, 20, 20) # type: ignore

        # Back button always at bottom
        self.back_button = self.make_back_button()

        # Add a spacer to push content up
        self.layout.insertStretch(0, 1) # type: ignore # push existing widgets to top

        # NEW: Load the sound for error (for validation)
        self.error_sound = load_sound("error.wav", parent=self)
        self._sounds.append(self.error_sound)


    def setup_input_field(self, return_callback=None):
        """Reusable method for input field styling."""
        input_field = QLineEdit()
        input_field.setFont(QFont(FONT_NAME, 24))
        input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(0,0,0,0);
                color: white;
                border: none;
                selection-background-color: rgba(255,255,255,50%);
                padding: 5px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor("black"))
        shadow.setOffset(0)
        input_field.setGraphicsEffect(shadow)

        if return_callback:
            input_field.returnPressed.connect(return_callback)

        self.layout.insertWidget(0, input_field)  # type: ignore # insert at top
        return input_field

# ----------------- Wizard Windows ----------------- #
class AddTaskWizard(StyledWindow):
    """Wizard for adding a new task."""
    def __init__(self, manager, parent_menu=None):
        super().__init__("Add Task", top_padding=10)
        self.manager = manager
        self.parent_menu = parent_menu  # reference to main menu
        if self.parent_menu:
            self.parent_menu.hide()  # hide the menu

        # --- Load Typing Sound ---
        self.typing_sound = load_sound("typing.wav", parent=self)
        self._sounds.append(self.typing_sound)
        # -------------------------
        
        # NEW: Load the sound for error
        self.error_sound = load_sound("error.wav", parent=self)
        self._sounds.append(self.error_sound)

        self.steps = ["Title", "Description", "Due Date", "Folder", "Tags"]
        self.inputs = {}
        self.current_step = 0

        self.label = self.make_label(self.steps[self.current_step] + ":")

        self.input_field = QLineEdit()
        self._setup_input_field()
        
        self.layout.addWidget(self.label) # type: ignore
        self.layout.addWidget(self.input_field) # type: ignore

        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer) # type: ignore

        self.make_back_button()

    def _setup_input_field(self):
        self.input_field.setFont(QFont(FONT_NAME, 24))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(0,0,0,0);
                color: white;
                border: none;
                selection-background-color: rgba(255,255,255,50%);
                padding: 5px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor("black"))
        shadow.setOffset(0)
        self.input_field.setGraphicsEffect(shadow)
        
        # Connect typing sound
        if self.typing_sound:
            self.input_field.textChanged.connect(lambda: self.typing_sound.play()) # type: ignore
            
        self.input_field.returnPressed.connect(self.next_step)
        

    def next_step(self):
        value = self.input_field.text().strip()
        step_name = self.steps[self.current_step]

        # 1. Validate title
        if step_name == "Title" and not value:
            send_notification("Error", "Title cannot be empty!")
            if self.error_sound: self.error_sound.play() # Play error sound
            return

        # 2. Validate due date
        if step_name == "Due Date":
            # Allow empty string for optional due date
            if value:
                try:
                    due_date = datetime.strptime(value, "%Y-%m-%d")
                    today = datetime.now().date()
                    if due_date.date() < today:
                        send_notification("Error", "Due date cannot be before today!")
                        if self.error_sound: self.error_sound.play() # Play error sound
                        return
                except ValueError:
                    send_notification("Error", "Invalid date format! Use YYYY-MM-DD")
                    if self.error_sound: self.error_sound.play() # Play error sound
                    return
        
        if self.success_sound:
            self.success_sound.play()
        # ==============================================================================

        self.inputs[step_name] = value
        self.input_field.clear()
        self.current_step += 1

        if self.current_step >= len(self.steps):
            self.finish_task()
        else:
            self.label.setText(self.steps[self.current_step] + ":")

    def finish_task(self):
        try:
            task = Task(
                title=self.inputs.get("Title", ""),
                description=self.inputs.get("Description", ""),
                due_date=self.inputs.get("Due Date", ""),
                tags=[t.strip() for t in self.inputs.get("Tags", "").split(",") if t.strip()],
                folder=self.inputs.get("Folder", "")
            )
            self.manager.add_task(task)
            send_notification("Success", f"Task '{task.title}' added successfully!")
            
            if self.success_sound:
                self.success_sound.play()
            # ==============================================

        except Exception as e:
            send_notification("Error", f"Failed to add task: {str(e)}")
            if self.error_sound: self.error_sound.play()
        finally:
            self._back_to_menu() # Use the standardized transition

# ----------------- Edit Task Wizard  ----------------- #
class EditTaskWizard(StyledWindow):
    """
    Wizard for editing an existing task's details. 
    MODIFIED: Now uses the pre-selected task object and index instead of prompting for ID.
    """
    def __init__(self, manager, task_index, task, parent_menu=None):
        super().__init__(f"Edit Task #{task_index + 1}", top_padding=50)
        self.manager = manager
        self.parent_menu = parent_menu
        if self.parent_menu:
            self.parent_menu.hide()

        # --- Load Typing Sound ---
        self.typing_sound = load_sound("typing.wav", parent=self)
        self._sounds.append(self.typing_sound)
        # -------------------------

        self.error_sound = load_sound("error.wav", parent=self)
        self._sounds.append(self.error_sound)

        self.current_task = task
        self.current_task_original_title = task.title # Store original title for manager lookup
        self.current_task_index = task_index
        # ========================================================

        # Start directly at the first edit step
        self.steps = ["Title", "Description", "Due Date", "Folder", "Tags"]
        self.inputs = {}
        self.current_step = 0

        # Setup input field for the FIRST attribute (Title)
        self.input_field = QLineEdit()
        self._setup_input()

        # Initialize and display the first step
        self.label = self.make_label("") # Will be set in _set_next_step_label

        self.layout.addWidget(self.label) # type: ignore
        self.layout.addWidget(self.input_field) # type: ignore
        
        # Set the initial label/placeholder for 'Title'
        self._set_next_step_label() 

        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer) # type: ignore

        self.make_back_button()

    def _setup_input(self):
        """Setup common input field styling."""
        self.input_field.setFont(QFont(FONT_NAME, 24))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(0,0,0,0);
                color: white;
                border: none;
                selection-background-color: rgba(255,255,255,50%);
                padding: 5px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor("black"))
        shadow.setOffset(0)
        self.input_field.setGraphicsEffect(shadow)
        
        # Connect typing sound
        if self.typing_sound:
            self.input_field.textChanged.connect(lambda: self.typing_sound.play()) # type: ignore
            
        self.input_field.returnPressed.connect(self.next_step)
        
    def _set_next_step_label(self):
        """Helper to set the label and placeholder based on the current step."""
        if self.current_step < len(self.steps):
            next_step_name = self.steps[self.current_step]
            next_attr_name = next_step_name.lower().replace(' ', '_')
            
            # Get current value for display/placeholder
            current_display_value = getattr(self.current_task, next_attr_name)
            if next_attr_name == 'tags':
                current_display_value = ", ".join(current_display_value)

            # Set the label to show current value and prompt for new input
            self.label.setText(f"Editing '{self.current_task_original_title}' — {next_step_name} [Current: {current_display_value}]:")
            self.input_field.setPlaceholderText(str(current_display_value))
            self.input_field.clear() # Ensure input is clear for new value
        

    def next_step(self):
        value = self.input_field.text().strip()
        
        step_name = self.steps[self.current_step]
        attr_name = step_name.lower().replace(' ', '_')
        
        # 1.: Check Due Date if provided
        if step_name == "Due Date" and value:
            try:
                due_date = datetime.strptime(value, "%Y-%m-%d")
                today = datetime.now().date()
                if due_date.date() < today:
                    send_notification("Error", "Due date cannot be before today!")
                    if self.error_sound: self.error_sound.play() 
                    return
            except ValueError:
                send_notification("Error", "Invalid date format! Use YYYY-MM-DD")
                if self.error_sound: self.error_sound.play() 
                return
        
        # 2. Store input (or preserved original value if empty)
        if not value:
            # If input is empty, preserve the current task value
            preserved_value = getattr(self.current_task, attr_name)
            if attr_name == 'tags':
                preserved_value = ", ".join(preserved_value)
            self.inputs[step_name] = preserved_value
        else:
            # Use the user's new input
            self.inputs[step_name] = value

        if self.success_sound:
            self.success_sound.play()
        # ==============================================================================

        self.current_step += 1

        if self.current_step >= len(self.steps):
            self.finish_edit()
        else:
            self._set_next_step_label() # Proceed to the next editing step
        # ========================================================


    def finish_edit(self):
        updates = {
            # Use the input value, defaulting to the original if input was empty at the Title step
            "title": self.inputs.get("Title", self.current_task.title), 
            "description": self.inputs.get("Description", self.current_task.description),
            "due_date": self.inputs.get("Due Date", self.current_task.due_date),
            "folder": self.inputs.get("Folder", self.current_task.folder),
            # Tags are always handled as a comma-separated string that needs splitting
            "tags": [t.strip() for t in self.inputs.get("Tags", "").split(",") if t.strip()] 
        }

        try:
            # Use the original title to find the task in the manager before applying updates
            self.manager.edit_task(self.current_task_original_title, updates)
            send_notification("Success", f"Task '{updates['title']}' updated!")
            
            if self.success_sound:
                self.success_sound.play()
            # ==============================================

        except Exception as e:
            send_notification("Error", f"Failed to edit task: {str(e)}")
            if self.error_sound: self.error_sound.play() # NEW: Play error sound
        finally:
            self._back_to_menu() # Use the standardized transition

# ----------------- Delete Task Wizard ----------------- #
class DeleteTaskWizard(StyledWindow):
    """Wizard for deleting a task. Uses Task ID for lookup."""
    def __init__(self, manager, parent_menu=None):
        super().__init__("Delete Task", top_padding=50)
        self.manager = manager
        self.parent_menu = parent_menu
        if self.parent_menu:
            self.parent_menu.hide()

        # --- Load Typing Sound ---
        self.typing_sound = load_sound("typing.wav", parent=self)
        self._sounds.append(self.typing_sound)
        # -------------------------

        self.error_sound = load_sound("error.wav", parent=self)
        self._sounds.append(self.error_sound)

        self.label = self.make_label("Enter Task ID to Delete:")
        self.input_field = QLineEdit()
        self._setup_input()
        self.layout.addWidget(self.label) # type: ignore
        self.layout.addWidget(self.input_field) # type: ignore

        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer) # type: ignore

        self.make_back_button()

    def _setup_input(self):
        """Setup common input field styling and connect to delete_task."""
        self.input_field.setFont(QFont(FONT_NAME, 24))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(0,0,0,0);
                color: white;
                border: none;
                selection-background-color: rgba(255,255,255,50%);
                padding: 5px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor("black"))
        shadow.setOffset(0)
        self.input_field.setGraphicsEffect(shadow)
        
        # Connect typing sound
        if self.typing_sound:
            self.input_field.textChanged.connect(lambda: self.typing_sound.play()) # type: ignore
            
        self.input_field.returnPressed.connect(self.delete_task)

    def delete_task(self):
        id_str = self.input_field.text().strip()
        
        try:
            task_index = int(id_str) - 1 # Convert user's 1-based ID to 0-based index
            if not 0 <= task_index < len(self.manager.tasks):
                send_notification("Error", f"Task ID {id_str} is out of range.")
                if self.error_sound: self.error_sound.play() # NEW: Play error sound
                return
            
            task = self.manager.tasks[task_index]
            
            self.manager.delete_task(task.title) # Delete by original title
            send_notification("Success", f"Task '{task.title}' (ID: {id_str}) deleted!")
            
            if self.success_sound:
                self.success_sound.play()
            # ==============================================
            
        except ValueError:
            send_notification("Error", "Please enter a valid number for the Task ID.")
            if self.error_sound: self.error_sound.play() # NEW: Play error sound
        except Exception as e:
            send_notification("Error", f"Failed to delete task: {str(e)}")
            if self.error_sound: self.error_sound.play() # NEW: Play error sound

        self._back_to_menu() # Use the standardized transition

# ----------------- Update Status Wizard ----------------- #
class UpdateStatusWizard(StyledWindow):
    """
    Wizard for updating a task's status. 
    MODIFIED: Now uses the pre-selected task object and index instead of prompting for ID.
    """
    def __init__(self, manager, task_index, task, parent_menu=None):
        super().__init__(f"Update Status for Task #{task_index + 1}", top_padding=50)
        self.manager = manager
        self.parent_menu = parent_menu
        if self.parent_menu:
            self.parent_menu.hide()

        # --- Load Typing Sound ---
        self.typing_sound = load_sound("typing.wav", parent=self)
        self._sounds.append(self.typing_sound)
        # -------------------------

        # NEW: Load the sound for error
        self.error_sound = load_sound("error.wav", parent=self)
        self._sounds.append(self.error_sound)

        self.statuses = ["Not Yet", "Pending", "Completed"]
        self.current_task = task
        self.current_task_index = task_index
        
        self.label = self.make_label(f"Updating '{task.title}'. Current status: {task.status}. Enter new status (Not Yet/Pending/Completed):")
        # ======================================================
        
        self.input_field = QLineEdit()
        self._setup_input()
        self.layout.addWidget(self.label) # type: ignore
        self.layout.addWidget(self.input_field) # type: ignore

        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer) # type: ignore

        self.make_back_button()

    def _setup_input(self):
        """Setup common input field styling and connect to next_step."""
        self.input_field.setFont(QFont(FONT_NAME, 24))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(0,0,0,0);
                color: white;
                border: none;
                selection-background-color: rgba(255,255,255,50%);
                padding: 5px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor("black"))
        shadow.setOffset(0)
        self.input_field.setGraphicsEffect(shadow)
        
        # Connect typing sound
        if self.typing_sound:
            self.input_field.textChanged.connect(lambda: self.typing_sound.play()) # type: ignore
            
        self.input_field.returnPressed.connect(self.update_status)
        # ============================================================

    def update_status(self):
        value = self.input_field.text().strip()

        if value not in self.statuses:
            send_notification("Error", f"Invalid status: {value}. Use one of: {', '.join(self.statuses)}")
            if self.error_sound: self.error_sound.play()
            return

        try:
            # Use the pre-selected task's title for the update
            self.manager.edit_task(self.current_task.title, {"status": value})
            send_notification("Success", f"Status updated for '{self.current_task.title}' to '{value}'!")

            if self.success_sound:
                self.success_sound.play()
            # ==============================================

        except Exception as e:
            send_notification("Error", f"Failed to update status: {str(e)}")
            if self.error_sound: self.error_sound.play()

        self._back_to_menu() # Use the standardized transition
    # ======================================================

# ----------------- View Tasks ----------------- #
class ViewTasksWindow(StyledWindow):
    """Simple list view of all tasks (deprecated/unused by final GUI)."""
    def __init__(self, manager):
        super().__init__("View Tasks", width=1000, height=700)
        self.manager = manager

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QFrame()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        if not manager.tasks:
            container_layout.addWidget(self.make_label("No tasks found", 20))
        else:
            for t in manager.tasks:
                lbl = self.make_label(
                    f"{t.title} | {t.status} | {t.due_date} | {t.folder or '-'} | {', '.join(t.tags)}",
                    20
                )
                container_layout.addWidget(lbl)

        scroll.setWidget(container)
        self.layout.addWidget(scroll) # type: ignore

# ----------------- Main Menu Window Wrapper ----------------- #
class MainMenuWindow(StyledWindow):
    """
    A wrapper for the CarouselMenu to apply StyledWindow properties 
    and add static header elements (time, author).
    """
    def __init__(self, manager, options, callbacks):
        # Use a smaller height/width as the CarouselMenu handles its own sizing
        super().__init__("Cyberpunk Task Manager", width=600, height=400, top_padding=10) 
        self.manager = manager
        
        # Override the StyledWindow layout contents margins because the CarouselMenu 
        # is the main item and handles its own movement. We want the static header 
        # elements to appear near the top edge.
        self.layout.setContentsMargins(20, 10, 20, 20) # type: ignore

        # 1. Static Header Setup (Author and Time)
        self._setup_static_header()
        
        # 2. Add Spacer to push the menu to the center
        # self.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)) # REMOVED
        
        # 3. Initialize and Insert the CarouselMenu
        self.carousel_menu = CarouselMenu(options, manager)
        # Pass 'self' as the parent menu reference for all child windows
        self.carousel_menu.option_selected.connect(lambda idx: callbacks[idx](self)) 
        
        # Ensure the CarouselMenu is sized correctly within this wrapper
        carousel_container = QFrame()
        carousel_container_layout = QHBoxLayout(carousel_container)
        carousel_container_layout.setContentsMargins(0,0,0,0)
        carousel_container_layout.addWidget(self.carousel_menu)
        
        # Set size policy to ensure the container expands vertically
        carousel_container.setSizePolicy(
            QSizePolicy.Policy.Preferred, 
            QSizePolicy.Policy.Expanding
        )

        self.layout.addWidget(carousel_container) # type: ignore
        
        # The StyledWindow's cleanup/sounds are now the parent's responsibility
        self._sounds.extend(self.carousel_menu._sounds) # Ensure carousel sounds are cleaned up too
        
        # Remove the default back button from the StyledWindow 
        # (It would be added to self.layout by super().__init__).

    def _setup_static_header(self):
        """Creates and adds the Time and Author labels to the top with distinct styles."""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Left Label: Time Now (Neon Green, slightly larger) ---
        # Note: make_label applies FONT_NAME and shadow by default
        self.time_label = self.make_label("Time: 00:00:00", font_size=20) 
        self.time_label.setStyleSheet(self.time_label.styleSheet() + "color: #00FF00;") # Neon Green
        header_layout.addWidget(self.time_label)
        
        # Spacer to push elements apart
        header_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)) 
        
        # --- Right Label: Author (Subtle Blue background, smaller font) ---
        self.author_label = self.make_label("Author: Jyun", font_size=16) # Smaller size
        self.author_label.setStyleSheet("""
            QLabel {
                color: #66FFFF; /* Light Blue */
                background-color: rgba(0, 0, 0, 0.4); /* Dark, subtle background */
                border-radius: 5px;
                padding: 5px 10px;
            }
        """)
        header_layout.addWidget(self.author_label)
        
        self.layout.addWidget(header_widget) # type: ignore
        
        # Setup timer to update the time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000) # Update every 1000ms (1 second)

    def _update_time(self):
        """Updates the time label with the current system time."""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(f"Time: {current_time}")
        
    def showEvent(self, event): # type: ignore
        """Ensures the time is current and the carousel is reset when the window is shown."""
        self._update_time()
        # The parent menu itself needs to be shown, and the carousel needs its state reset
        if hasattr(self, 'carousel_menu'):
            # --- SAFEGUARD: Force the carousel to refresh its labels ---
            self.carousel_menu.update_labels(initial=True) 
            # ----------------------------------------------------------
            self.carousel_menu.showEvent(event)
        super().showEvent(event)
        
    def setFocus(self): # type: ignore
        """Forward focus to the carousel so key events work."""
        if hasattr(self, 'carousel_menu'):
            self.carousel_menu.setFocus()
            
    def keyPressEvent(self, event): # type: ignore
        """Forward key events to the contained CarouselMenu."""
        # MainMenuWindow should only forward to CarouselMenu, as it has no other input fields
        if hasattr(self, 'carousel_menu'):
            self.carousel_menu.keyPressEvent(event)
        else:
            super().keyPressEvent(event)
# ----------------- END Main Menu Window Wrapper ----------------- #


# ----------------- Carousel Menu ----------------- #
class CarouselMenu(QWidget):
    """
    Main menu widget with a vertical, animated carousel selection.
    """
    option_selected = pyqtSignal(int)

    def __init__(self, options, manager, font_size=48, spacing=20):
        super().__init__()
        self.manager = manager
        self.options = options
        self.font_size = font_size
        self.spacing = spacing
        self.current_index = 0
        self.labels = []
        self._anims = []
        self._sounds = []

        # --- Add sound effects ---
        self.move_sound = load_sound("move.wav", parent=self)
        self.select_sound = load_sound("select.wav", parent=self)
        # Load the dedicated exit sound here for use by the Exit option (menu_close.wav is correct here)
        self.exit_sound = load_sound("menu_close.wav", parent=self) 
        
        self._sounds.extend([self.move_sound, self.select_sound, self.exit_sound])

        # IMPORTANT: Setting a size policy here ensures it expands within its parent (MainMenuWindow)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        self._init_labels()
        # Initial labels update should be done after the widget is fully placed 
        # in the parent's layout, but we call it here and again in showEvent.
        self.update_labels(initial=True) 

    def _init_labels(self):
        # We assume the parent (MainMenuWindow) sets the stage width/height
        # Use a reasonable default for initial sizing, but rely on self.height() later
        window_width = 600 
        
        for option in self.options:
            lbl = QLabel(option, self)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont(FONT_NAME, self.font_size)
            lbl.setFont(font)
            # Set size based on the assumed window width, not self.width() which might be 0 initially
            lbl.resize(window_width, self.font_size + 20) 

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)
            shadow.setColor(QColor("black"))
            shadow.setOffset(0)
            lbl.setGraphicsEffect(shadow)

            lbl.setStyleSheet("color: white;")
            lbl.show()
            self.labels.append(lbl)

    def update_labels(self, initial=False):
        # FIX: self.height() is now reliable because the parent uses QSizePolicy.Expanding
        if self.height() == 0:
            return
            
        center_y = self.height() // 2 
        
        for i, lbl in enumerate(self.labels):
            distance = i - self.current_index
            
            # Show more labels when the menu is tall, but keep it centered
            if abs(distance) > 2: # Show two items above and below the center (5 total visible)
                lbl.hide()
                continue
            else:
                lbl.show()

            target_y = center_y + distance * (self.font_size + self.spacing)
            target_size = self.font_size * (1.3 if distance == 0 else 1.0)

            # Animate position
            anim_pos = QPropertyAnimation(lbl, b"pos", self)
            anim_pos.setDuration(250)
            # Center X: (self.width() - label.width) / 2
            # Use self.width() now that it's reliably sized by the parent
            center_x = (self.width() - lbl.width()) // 2 
            anim_pos.setEndValue(QPoint(center_x, target_y - int(target_size)//2))
            anim_pos.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anims.append(anim_pos)
            anim_pos.start()

            # Animate font size smoothly (using QTimer for simpler size transition)
            start_size = lbl.font().pointSize()
            steps = 10
            delta = (target_size - start_size)/steps
            for step in range(1, steps+1):
                QTimer.singleShot(step*25, lambda s=start_size+delta*step, l=lbl: l.setFont(QFont(FONT_NAME, int(s))))

    def keyPressEvent(self, event): # type: ignore
        if event.key() == Qt.Key.Key_Up:
            if self.current_index > 0:
                self.current_index -= 1
                self.update_labels()
                if self.move_sound:
                    self.move_sound.play()
        elif event.key() == Qt.Key.Key_Down:
            if self.current_index < len(self.options) - 1:
                self.current_index += 1
                self.update_labels()
                if self.move_sound:
                    self.move_sound.play()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            
            is_exit = (self.current_index == len(self.options) - 1)

            # Play the correct sound
            if is_exit:
                # This uses menu_close.wav, which is correct for exiting
                if self.exit_sound:
                    self.exit_sound.play()
            else:
                # This uses menu_select.wav, which is correct for opening a wizard
                if self.select_sound:
                    self.select_sound.play()
            
            label = self.labels[self.current_index]
            self.play_selection_animation(label)
        elif event.key() == Qt.Key.Key_Escape:
            # For simplicity, we ignore ESC in the main menu carousel itself.
            pass
        else:
            super().keyPressEvent(event)


    def play_selection_animation(self, label):
        """Pulse the label then fade the whole menu out and finally emit option_selected(index)."""
        start_size = label.font().pointSize()
        if start_size <= 0:
            start_size = int(self.font_size)
        end_size = max(1, int(start_size * 1.25))

        size_anim = QVariantAnimation(self)
        size_anim.setStartValue(start_size)
        size_anim.setEndValue(end_size)
        size_anim.setDuration(200)
        size_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        def on_size_changed(value):
            f = label.font()
            f.setPointSize(int(value))
            label.setFont(f)
        size_anim.valueChanged.connect(on_size_changed)

        opacity_effect = QGraphicsOpacityEffect(label)
        label.setGraphicsEffect(opacity_effect)
        op_anim = QVariantAnimation(self)
        op_anim.setStartValue(1.0)
        op_anim.setEndValue(0.0)
        op_anim.setDuration(250)
        op_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        op_anim.valueChanged.connect(lambda v: opacity_effect.setOpacity(float(v)))

        def after_label_anim():
            f = label.font()
            f.setPointSize(start_size)
            label.setFont(f)
            label.setGraphicsEffect(None)
            
            # Fade the whole window out (window is now MainMenuWindow, the parent)
            parent_window = self.parentWidget()
            if parent_window:
                fade = QPropertyAnimation(parent_window, b"windowOpacity", self)
                fade.setDuration(250)
                fade.setStartValue(1.0)
                fade.setEndValue(0.0)
                fade.setEasingCurve(QEasingCurve.Type.OutCubic)

                def after_fade():
                    self.option_selected.emit(self.current_index)


                fade.finished.connect(after_fade)
                self._anims.append(fade)
                fade.start()
            else:
                self.option_selected.emit(self.current_index)


        size_anim.finished.connect(lambda: op_anim.start())
        op_anim.finished.connect(after_label_anim)

        self._anims.extend([size_anim, op_anim])
        size_anim.start()
        
    def showEvent(self, event): # type: ignore
        """
        Overrides showEvent to ensure the menu state is correctly reset
        when returning from a child window, preventing visual glitches.
        """
        # 1. Ensure window opacity is fully reset (now handles by parent MainMenuWindow)
        # self.setWindowOpacity(1.0) 
        
        # 2. Re-show all labels (they might have been hidden/faded out)
        for lbl in self.labels:
            lbl.show()
            
        # 3. Re-run update_labels to reset positions and font sizes correctly
        self.update_labels(initial=True)
        
        super().showEvent(event) # Call the base implementation

    def cleanup(self):
        """Safely stop animations and sounds for the main Carousel Menu."""
        for anim in self._anims:
            try:
                anim.stop()
                anim.deleteLater()
            except Exception:
                pass
        self._anims = []

        for sound in self._sounds:
            if sound:
                try:
                    sound.stop()
                    sound.deleteLater()
                except Exception:
                    pass
        self._sounds = []

    def closeEvent(self, event): # type: ignore
        self.cleanup()
        event.accept()

# ----------------- Task Carousel Window  ----------------- #
class TaskCarouselWindow(StyledWindow):
    """
    Task viewing screen that uses a carousel for selection, now with sorting controls.
    """
    SORT_KEYS = ['ID', 'Status', 'DueDate']
    STATUS_ORDER = {"Not Yet": 0, "Pending": 1, "Completed": 2}

    def __init__(self, manager, parent_menu=None):
        super().__init__("View Tasks", width=1000, height=700, top_padding=10) # Reduced top padding
        self.manager = manager
        self.parent_menu = parent_menu
        if self.parent_menu:
            self.parent_menu.hide()

        self.font_size = 48
        self.spacing = 20
        self.current_index = 0
        self.labels = []
        self.tasks = [] # Store the *sorted* list of tasks
        self.detail_label = None
        self.sort_key = 'ID' # Default sort key
        self.sort_buttons = {}

        self.move_sound = load_sound("move.wav", parent=self)
        self.select_sound = load_sound("select.wav", parent=self)
        self._sounds.extend([self.move_sound, self.select_sound])

        # --- Sort Controls (Inserted at the top of the layout) ---
        self._create_sort_controls()
        
        # Spacer to push carousel down
        self.spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(self.spacer) # type: ignore

        self.load_tasks()
        # The back button is created here. make_back_button now uses the glassmorphism style.
        self.back_button = self.make_back_button() 
        self.back_button.raise_()

    def _create_sort_controls(self):
        """Creates buttons for sorting tasks by different criteria."""
        sort_widget = QWidget()
        sort_layout = QHBoxLayout(sort_widget)
        sort_layout.setContentsMargins(0, 0, 0, 0)
        sort_layout.setSpacing(10)

        sort_layout.addWidget(self.make_label("Sort By:", 18))

        for key in self.SORT_KEYS:
            # Use make_button here for the sort buttons as it was already defined for them
            btn = self.make_button(key, 18) 
            
            # Additional style for active button (which make_button doesn't handle)
            btn.setStyleSheet(btn.styleSheet() + """
                QPushButton[data-active="true"] {
                    background-color: rgba(0, 123, 255, 0.5); /* Blue highlight */
                    border: 1px solid rgba(0, 123, 255, 1.0);
                }
            """)
            
            btn.setProperty("data-active", 'true' if key == self.sort_key else 'false')
            btn.clicked.connect(functools.partial(self._set_sort_key, key))
            self.sort_buttons[key] = btn
            sort_layout.addWidget(btn)

        self.layout.insertWidget(0, sort_widget) # type: ignore

    def _set_sort_key(self, key):
        """Changes the sort key and reloads the task list."""
        if self.sort_key == key:
            return
        
        self.sort_key = key
        
        # Update button styles
        for k, btn in self.sort_buttons.items():
            btn.setProperty("data-active", 'true' if k == self.sort_key else 'false')
            btn.style().polish(btn) # Repolish to apply stylesheet changes

        self.current_index = 0
        self.load_tasks()

    def _sort_tasks(self, task_list):
        """Sorts the task list based on the current sort_key."""
        if self.sort_key == 'ID':
            # ID is implicit in the manager's list order (creation time)
            return task_list

        elif self.sort_key == 'Status':
            # Sort by predefined status order (Not Yet, Pending, Completed)
            return sorted(
                task_list, 
                key=lambda t: self.STATUS_ORDER.get(t.status, 99)
            )

        elif self.sort_key == 'DueDate':
            # Sort by due date (closest first. Empty dates go last.)
            def due_date_sort_key(task):
                if not task.due_date:
                    return datetime.max # Put tasks with no date at the end
                try:
                    return datetime.strptime(task.due_date, "%Y-%m-%d")
                except ValueError:
                    return datetime.max # Invalid dates go at the end too
            
            return sorted(task_list, key=due_date_sort_key)
        
        return task_list

    def refresh_tasks(self):
        """Reload tasks and update labels."""
        self.load_tasks()

    def load_tasks(self):
        """Loads tasks using the ABSOLUTELY CONCISE format and applies sorting."""
        
        # 1. Get and sort tasks
        all_tasks = self.manager.tasks
        self.tasks = self._sort_tasks(all_tasks)

        # 2. Clear old labels
        for lbl in self.labels:
            lbl.hide()
            lbl.setParent(None)
        self.labels = []
        
        # 3. Handle No Tasks case
        if not self.tasks:
            lbl = QLabel("No tasks found", self)
            lbl.setFont(QFont(FONT_NAME, 24))
            lbl.setStyleSheet("color: white;")
            # Align center for this special case
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter) 
            # Center it roughly in the middle, accounting for header
            lbl.move(0, self.height() // 2 - 50)
            lbl.resize(self.width(), 50)
            lbl.show()
            self.labels.append(lbl)
        else:
            for i, task in enumerate(self.tasks):
                
                # Severely truncate long titles (Max 20 chars for carousel)
                display_title = task.title
                if len(display_title) > 20:
                    display_title = display_title[:17] + "..." 
                    
                # The displayed ID (#i+1) is now the task's position in the *sorted* list.
                # Final concise text: [STATUS] #ID - TITLE...
                lbl_text = f"[{task.status.upper()}] #{i+1} - {display_title}"
                # ------------------------------------

                lbl = QLabel(lbl_text, self)
                
                # Align Left for the carousel list
                lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                
                lbl.setFont(QFont(FONT_NAME, self.font_size))
                # Set width to full window width (minus margin) for left alignment to work well
                lbl.resize(self.width() - 40, self.font_size + 20) 

                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(8)
                shadow.setColor(QColor("black"))
                shadow.setOffset(0)
                lbl.setGraphicsEffect(shadow)

                lbl.setStyleSheet("color: white;")
                lbl.show()
                self.labels.append(lbl)

        self.current_index = 0
        self.update_labels()

    def update_labels(self):
        center_y = self.height() // 2
        for i, lbl in enumerate(self.labels):
            distance = i - self.current_index
            if abs(distance) > 1: # Show only two items above and below the center
                lbl.hide()
                continue
            lbl.show()

            target_y = center_y + distance * (self.font_size + self.spacing)
            target_size = self.font_size * (1.3 if distance == 0 else 1.0)

            # Animate position
            anim_pos = QPropertyAnimation(lbl, b"pos", self)
            anim_pos.setDuration(250)
            
            # Set X position to 20 (left margin) for left alignment
            target_x = 20 
            anim_pos.setEndValue(QPoint(target_x, target_y - int(target_size)//2))
            
            anim_pos.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anims.append(anim_pos)  # Save reference for cleanup
            anim_pos.start()

            # Animate font size
            start_size = lbl.font().pointSize()
            steps = 10
            delta = (target_size - start_size) / steps
            for step in range(1, steps + 1):
                QTimer.singleShot(step * 25, lambda s=start_size + delta*step, l=lbl: l.setFont(QFont(FONT_NAME, int(s))))

    def play_selection_animation(self, label):
        """Pulse the selected label, fade it out, then show task details."""
        if not hasattr(self, "_anims"):
            self._anims = []

        start_size = label.font().pointSize()
        if start_size <= 0:
            start_size = int(self.font_size)
        end_size = max(1, int(start_size * 1.25))

        #  Font pulse animation
        size_anim = QVariantAnimation(self)
        size_anim.setStartValue(start_size)
        size_anim.setEndValue(end_size)
        size_anim.setDuration(200)
        size_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        def on_size_changed(value):
            f = label.font()
            f.setPointSize(int(value))
            label.setFont(f)
        size_anim.valueChanged.connect(on_size_changed)

        # Opacity fade
        opacity_effect = QGraphicsOpacityEffect(label)
        label.setGraphicsEffect(opacity_effect)
        op_anim = QVariantAnimation(self)
        op_anim.setStartValue(1.0)
        op_anim.setEndValue(0.0)
        op_anim.setDuration(250)
        op_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        op_anim.valueChanged.connect(lambda v: opacity_effect.setOpacity(float(v)))

        def after_label_anim():
            # Restore font and clean up
            f = label.font()
            f.setPointSize(start_size)
            label.setFont(f)
            label.setGraphicsEffect(None)
            label.hide()
            # Now show task details (after animation)
            self.show_task_details()

        # Chain animations
        size_anim.finished.connect(lambda: op_anim.start())
        op_anim.finished.connect(after_label_anim)

        self._anims.extend([size_anim, op_anim]) # Save references for cleanup
        size_anim.start()

    def keyPressEvent(self, event):
        # --- Handle Task Details View (LOCKED NAVIGATION) ---
        if self.detail_label:
            # ESC closes detail and returns to carousel list
            if event.key() == Qt.Key.Key_Escape:
                # OPTIONAL: Play the back sound when exiting detail view
                if self.back_sound:
                    self.back_sound.play() 
                
                self.detail_label.hide()
                self.detail_label.deleteLater()
                self.detail_label = None
                for lbl in self.labels:
                    lbl.show()
                return
            else:
                # Block all other keys (Up, Down, Enter, etc.) when details are showing
                # This enforces the "Esc or Back Button only" rule for exiting the detail view.
                return

        if event.key() == Qt.Key.Key_Up:
            if self.tasks:
                self.current_index = max(0, self.current_index - 1)
                self.update_labels()
                if self.move_sound:
                    self.move_sound.play()
        elif event.key() == Qt.Key.Key_Down:
            if self.tasks:
                self.current_index = min(len(self.tasks) - 1, self.current_index + 1)
                self.update_labels()
                if self.move_sound:
                    self.move_sound.play()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if not self.tasks or (len(self.labels) == 1 and self.labels[0].text() == "No tasks found"):
                return
            if self.select_sound:
                self.select_sound.play()
            label = self.labels[self.current_index]
            self.play_selection_animation(label)
        elif event.key() == Qt.Key.Key_Escape:
            # If details are not showing, use the base class handler to go back to parent menu
            super().keyPressEvent(event)

    def show_task_details(self):
        if self.detail_label and not self.detail_label.isHidden():
            return # already showing

        # Check if current_index is valid for self.tasks
        if not self.tasks or self.current_index >= len(self.tasks):
            return

        task = self.tasks[self.current_index]

        # Description is at the bottom.
        self.detail_label = QLabel(
            f"Title: {task.title}\n"
            f"Status: {task.status}\n"
            f"Due Date: {task.due_date}\n"
            f"Folder: {task.folder or '-'}\n"
            f"Tags: {', '.join(task.tags) or '-'}\n"
            f"Description: {task.description or '-'}", 
            self
        )
        self.detail_label.setFont(QFont(FONT_NAME, 24))
        self.detail_label.setStyleSheet("color: white;")
        
        # Align Left and Top for the detailed view
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop) 
        
        self.detail_label.setWordWrap(True)
        
        margin_x = 80 # Total horizontal margin (40px on each side)
        margin_y_top = 100 # Top padding from window edge (to clear sort controls)
        margin_y_bottom = 80 # Bottom padding (to clear back button)
        
        new_width = self.width() - margin_x
        new_height = self.height() - margin_y_top - margin_y_bottom
        
        self.detail_label.resize(new_width, new_height)
        self.detail_label.move(margin_x // 2, margin_y_top) # Start position at (40, 100)
        # ---------------------------------------------

        self.detail_label.show()

        # Ensure back button stays on top
        if hasattr(self, 'back_button'):
            self.back_button.raise_()

        # Hide task labels
        for lbl in self.labels:
            lbl.hide()

# -----------------  Custom Styled Task Selection Dialog ----------------- #
class TaskSelectionDialog(QDialog):
    """
    A custom styled dialog for selecting a task ID, replacing QInputDialog 
    to maintain the transparent/frameless style.
    """
    def __init__(self, manager, action_name, parent_menu=None):
        super().__init__(parent_menu)
        self.manager = manager
        self.action_name = action_name
        self.result_index = None # The 0-based index to return
        self.parent_menu = parent_menu
        
        # Apply Frameless, AlwaysOnTop, Transparent properties
        self.setWindowTitle(f"{action_name} Task Selection")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(800, 600)
        self.setModal(True) 
        
        self.layout = QVBoxLayout() # type: ignore
        self.layout.setSpacing(15) # type: ignore
        self.layout.setContentsMargins(40, 40, 40, 40) # type: ignore
        self.setLayout(self.layout) # type: ignore
        
        # Load sounds specific to the dialog
        self.error_sound = load_sound("error.wav", parent=self)
        self.typing_sound = load_sound("typing.wav", parent=self)
        self.success_sound = load_sound("success.wav", parent=self)
        # ==============================================================

        # --- Task List Display ---
        self.layout.addWidget(self._make_styled_label(f"**Current Tasks (1-based index):**", 24)) # type: ignore
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(350)
        # Styled scroll area background
        scroll.setStyleSheet("background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 10px;")
        
        container = QFrame()
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        container_layout.setSpacing(5)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container.setLayout(container_layout)
        
        # Populate task list
        all_tasks = self.manager.tasks 
        if not all_tasks:
            container_layout.addWidget(self._make_styled_label("No tasks available.", 20))
        else:
            for i, task in enumerate(all_tasks):
                # Bold index for readability
                lbl = self._make_styled_label(
                    f"**{i+1}**: {task.title} (Status: {task.status})",
                    20
                )
                container_layout.addWidget(lbl)
        
        scroll.setWidget(container)
        self.layout.addWidget(scroll) # type: ignore
        
        # --- Index Input ---
        self.layout.addWidget(self._make_styled_label(f"Enter the **index** of the task to {action_name.lower()}:", 20)) # type: ignore
        
        self.input_field = self._setup_styled_input()
        self.input_field.returnPressed.connect(self._validate_and_accept)
        self.layout.addWidget(self.input_field) # type: ignore

        # --- Button Bar ---
        button_bar = QHBoxLayout()
        # Using a styled button for OK/Cancel here
        ok_btn = self._make_styled_button("Select", 24)
        ok_btn.clicked.connect(self._validate_and_accept)
        
        cancel_btn = self._make_styled_button("Cancel", 24)
        cancel_btn.clicked.connect(self.reject)
        
        button_bar.addWidget(cancel_btn)
        button_bar.addWidget(ok_btn)
        
        self.layout.addLayout(button_bar) # type: ignore
        
    # Helper methods replicating StyledWindow's style logic
    def _make_styled_label(self, text, font_size=24):
        lbl = QLabel(text)
        lbl.setFont(QFont(FONT_NAME, font_size))
        lbl.setStyleSheet("color: white;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor("black"))
        shadow.setOffset(0)
        lbl.setGraphicsEffect(shadow)
        lbl.setWordWrap(True)
        return lbl

    def _make_styled_button(self, text, font_size=24):
        btn = QPushButton(text)
        btn.setFont(QFont(FONT_NAME, font_size))
        btn.setStyleSheet(
            """
            QPushButton {
                color: #FFFFFF;
                background-color: rgba(255, 255, 255, 0.1); 
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-radius: 12px;
                padding: 10px 20px; 
                outline: 0px; 
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.8);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.2);
                border-style: inset;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            """
        )
        return btn
        
    def _setup_styled_input(self):
        input_field = QLineEdit()
        input_field.setFont(QFont(FONT_NAME, 24))
        input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(0,0,0,0);
                color: white;
                border: none;
                selection-background-color: rgba(255,255,255,50%);
                padding: 5px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor("black"))
        shadow.setOffset(0)
        input_field.setGraphicsEffect(shadow)

        # Connect typing sound
        if self.typing_sound:
            input_field.textChanged.connect(lambda: self.typing_sound.play()) # type: ignore
        
        return input_field

    def _validate_and_accept(self):
        id_str = self.input_field.text().strip()
        all_tasks = self.manager.tasks 

        if not id_str:
            send_notification("Error", "Please enter a task index.")
            if self.error_sound: self.error_sound.play()
            return
            
        try:
            user_index = int(id_str)
            list_index = user_index - 1
            
            if 0 <= list_index < len(all_tasks):
                self.result_index = list_index
                
                if self.success_sound:
                    self.success_sound.play()
                # ===============================================================
                
                self.accept()
            else:
                send_notification(
                    "Error",
                    f"Invalid index: Task #{user_index} does not exist. Range: 1 to {len(all_tasks)}."
                )
                if self.error_sound: self.error_sound.play()
                
        except ValueError:
            send_notification("Error", "Invalid input. Please enter a number.")
            if self.error_sound: self.error_sound.play()
            
    def reject(self):
        """Override reject to ensure sound cleanup on cancel/close."""
        if hasattr(self, 'error_sound') and self.error_sound:
            self.error_sound.deleteLater()
            
        if hasattr(self, 'typing_sound') and self.typing_sound:
            self.typing_sound.deleteLater()
            
        if hasattr(self, 'success_sound') and self.success_sound:
            self.success_sound.deleteLater()
        # =============================================
        
        super().reject()
# ----------------- END Custom Styled Task Selection Dialog ----------------- #

# ---------- GUI Wrappers ----------------- #
class GUIHandler:
    """Manages opening and closing of different GUI windows."""
    def __init__(self, manager):
        self.manager = manager
        self.open_window = None

    def _prompt_for_task_and_index(self, parent, action_name):
        """
        Helper to prompt the user for a 1-indexed task index, 
        using the new styled dialog, and return the 0-indexed list index and the Task object.
        """
        all_tasks = self.manager.tasks 
        
        if not all_tasks:
            # Use QMessageBox for this initial list check as it's outside the main flow
            QMessageBox.information(parent, "Task List", f"There are no tasks to {action_name.lower()}.")
            return None, None, None
            
        # 1. Create and show the new styled dialog
        dialog = TaskSelectionDialog(self.manager, action_name, parent_menu=parent)
        
        # Hide parent menu while the dialog is modal
        parent.hide()
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            list_index = dialog.result_index
            selected_task = all_tasks[list_index]
            
            # Show the parent menu again when the dialog is closed/accepted
            parent.show()
            
            # Use a notification for the final confirmation (more consistent style)
            send_notification(
                f"Task Selected",
                f"You selected task #{list_index + 1}: {selected_task.title}" # type: ignore
            )
            
            # Return 0-based index, Task object, and the parent menu
            return list_index, selected_task, parent 
        else:
            # Dialog rejected (Cancel or closed)
            parent.show() # Show parent menu again
            return None, None, None
    # ====================================================================

    def add_task_gui(self, menu):
        self.open_window = AddTaskWizard(self.manager, parent_menu=menu)
        self.open_window.show()
        # Connect a refresh after task is added
        self.open_window.destroyed.connect(self._refresh_carousel)

    def view_tasks_gui(self, menu):
        # Always create a fresh carousel window to ensure tasks are current
        if self.open_window and isinstance(self.open_window, TaskCarouselWindow):
            self.open_window.close() # Close existing one safely
        self.open_window = TaskCarouselWindow(self.manager, parent_menu=menu)
        self.open_window.show()
        self.open_window.setFocus()

    def edit_task_gui(self, menu):
        """Prompts for index, confirms task title, then launches the EditTaskWizard."""
        # 1. Use the new helper to get the index and task object
        index, task, parent_menu = self._prompt_for_task_and_index(menu, "Edit")
        
        if task is not None:
            # 2. Launch the Edit Task Wizard, passing the 0-based index and task object
            self.open_window = EditTaskWizard(self.manager, index, task, parent_menu=parent_menu)
            self.open_window.show()
            self.open_window.destroyed.connect(self._refresh_carousel)
    # ============================================

    def update_status_gui(self, menu):
        """Prompts for index, confirms task title, then launches the UpdateStatusWizard."""
        # 1. Use the new helper to get the index and task object
        index, task, parent_menu = self._prompt_for_task_and_index(menu, "Update Status")

        if task is not None:
            # 2. Launch the Update Status Wizard, passing the 0-based index and task object
            self.open_window = UpdateStatusWizard(self.manager, index, task, parent_menu=parent_menu)
            self.open_window.show()
    # ================================================

    def delete_task_gui(self, menu):
        self.open_window = DeleteTaskWizard(self.manager, parent_menu=menu)
        self.open_window.show()
        self.open_window.destroyed.connect(self._refresh_carousel)

    def exit_gui(self, menu):
        """Quits the application after a brief delay to play the exit sound."""
        
        # The sound is played by CarouselMenu.keyPressEvent.
        # We only need the delayed quit to ensure the sound has time to play.
        if hasattr(menu, 'carousel_menu') and menu.carousel_menu.exit_sound:
            QTimer.singleShot(100, lambda: QApplication.instance().quit()) # type: ignore
        else:
            QApplication.instance().quit() # type: ignore

    def _refresh_carousel(self):
        # This checks if the carousel window is still the open window, or if it has been closed
        # and replaced by another wizard. If it's a carousel, refresh its content.
        if isinstance(self.open_window, TaskCarouselWindow) and self.open_window is not None:
            self.open_window.refresh_tasks()

# ----------------- Main ----------------- #
if __name__ == "__main__":
    back_to_desktop()  

    # Prevent macOS layer crash
    os.environ["QT_MAC_WANTS_LAYER"] = "1"
    app = QApplication(sys.argv)

    # --- Set Application Icon ---
    icon_path = os.path.join(os.path.dirname(__file__), ICON_FILE)
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print(f"Icon file not found at: {icon_path}. Using default system icon.")
    # ---------------------------------

    # --- Safe font loading after QApplication exists ---
    try:
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    FONT_NAME = families[0]
                    print("Loaded font:", FONT_NAME)
                else:
                    print("Failed to load font, using fallback: Menlo")
                    FONT_NAME = "Menlo"
            else:
                print("Failed to load font, using fallback: Menlo")
                FONT_NAME = "Menlo"
        else:
            print("Font file not found at:", font_path)
            FONT_NAME = "Menlo"
    except Exception as e:
        print("Safe font load failed:", e)
        FONT_NAME = "Menlo"

    app.setFont(QFont(FONT_NAME, 20)) # Set a base font family

    # --- Step : show loading animation first ---
    try:
        # Instantiate the custom loading screen, PASSING THE DURATION
        splash = PixelLoadingOverlay(LOADING_DURATION_MS) 
        splash.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        splash.show()
    except NameError:
        # Fallback if PixelLoadingOverlay is not found (e.g., if loading_bar.py is missing)
        splash = QWidget()
        splash.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        splash.resize(300, 100)
        splash.setStyleSheet("background-color: black;")
        
        loading_label = QLabel("LOADING...", splash)
        loading_label.setFont(QFont(FONT_NAME, 24))
        loading_label.setStyleSheet("color: white;")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.resize(300, 100)
        splash.show()
    # -------------------------------------------------------------------


    # --- Step : run main GUI (scheduled to run after loading finish) ---
    def start_main_app():
        manager = TaskManager()
        gui = GUIHandler(manager)

        options = [
            "Add Task",
            "View Tasks",
            "Edit Task Details",
            "Update Task Status",
            "Delete Task",
            "Exit",
        ]
        callbacks = [
            gui.add_task_gui,
            gui.view_tasks_gui,
            gui.edit_task_gui,
            gui.update_status_gui,
            gui.delete_task_gui,
            gui.exit_gui,
        ]

        # Use the new wrapper window
        menu = MainMenuWindow(manager, options, callbacks)
        
        menu.show()
        menu.setFocus()

        # Connect the main menu's cleanup for safe shutdown
        if hasattr(menu, "cleanup"):
            app.aboutToQuit.connect(menu.cleanup)

    # Use QTimer.singleShot to start the main app and delete the splash screen
    # after the duration defined above.
    QTimer.singleShot(LOADING_DURATION_MS, lambda: (
        start_main_app(),
        splash.deleteLater()
    ))

    sys.exit(app.exec())