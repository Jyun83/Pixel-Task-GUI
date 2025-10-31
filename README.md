# 🧠 Pixel Task GUI

**Pixel Task GUI** is a task management system that combines a clean CLI, a modern PyQt6 graphical interface, and a macOS-style background notifier.  
It helps users create, edit, view, and manage their daily tasks efficiently, with smooth animations and notifications.

---

## 🌟 Features

- 🪄 **Interactive GUI (PyQt6)** — Beautiful task management wizards with animations.  
- 🔔 **Background Notifications** — Uses `rumps` and threading to alert users about due tasks.  
- 💻 **Command-Line Interface (CLI)** — Fully functional text-based version for quick usage.  
- 🎨 **Custom Fonts & Sounds** — Personalized visual and audio feedback via `.ttf` and `.wav` assets.  
- 🧩 **Modular Design** — Clean folder structure for easy maintenance and future scalability.  

---

## 🧱 Project Structure

```
project/
├── task_manager.py              # Core logic for managing tasks (add, edit, delete, view)
├── task.py                      # Task class with attributes and methods like is_due_soon()
├── notifier.py                  # Handles desktop notifications
├── menu_bar.py                  # macOS menu bar app (using rumps)
├── menu_cli.py                  # Command-line interface entry point
├── menu_gui.py                  # GUI entry point (PyQt6)
│
├── assets/
│   ├── custom_font.ttf
│   ├── notification_sound.wav
│
├── utils/
│   ├── helpers.py               # Helper functions (e.g., clear_screen)
│   └── background.py            # Background thread for notifications
│
├── ui/
│   ├── add_task.py              # CLI interface for adding tasks
│   ├── view_tasks.py            # CLI interface for viewing and filtering tasks
│   ├── update_menu.py           # Interface for updating task statuses
│   ├── edit_task.py             # Interface for editing existing tasks
│   ├── delete_task.py           # Interface for deleting tasks
│   ├── check_deadline.py        # Interface for showing due/overdue tasks
│   └── __init__.py
│
├── tasks.json                   # Data file storing all tasks
└── README.md
```

---

## ⚙️ Installation

### 1. Clone or Download
```bash
git clone https://github.com/Jyun83/FIT1045-Project.git
cd project
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt`, you can install manually:
```bash
pip install PyQt6 rumps plyer pync
```

---

## 🚀 Running the Application

### 💡 Option 1: Launch Background Menu Bar App
```bash
python3 menu_bar.py
```

### 💡 Option 2: Launch GUI Interface
```bash
python3 menu_gui.py
```

### 💡 Option 3: Use Command-Line Version
```bash
python3 menu_cli.py
```

---

## 🧩 Key Components Overview

### `task_manager.py`
Manages core logic for adding, editing, deleting, and retrieving tasks.  
Ensures consistent synchronization with the `tasks.json` file.

### `notifier.py`
Uses `plyer` and `pync` for sending desktop notifications about upcoming or overdue tasks.

### `menu_bar.py`
Implements a macOS-style menu bar using the **rumps** library.
Includes:
- Background thread toggling (`toggle_notification`)
- Quit option for easy app shutdown

### `menu_gui.py`
The main graphical interface using **PyQt6**, featuring:
- Custom fonts via `QFontDatabase`
- Animated progress/loading screen (`PixelLoadingOverlay`)
- Wizard-style windows for different task operations

### `ui/` Folder
Contains modular CLI interfaces for performing each specific action (add, edit, delete, view, etc.).

---

## 🎨 Assets

The `assets/` directory contains:
- `.ttf` — Custom font file registered using `QFontDatabase`
- `.wav` — Notification or feedback sounds loaded via a `load_sound()` helper

Make sure the relative paths in your GUI classes point to these files correctly.

---

## 💡 Technical Highlights

- Built with **PyQt6** for GUI and animation support  
- **Thread-safe background notifier** with daemon threads  
- **MVC-inspired structure** — clear separation of data, logic, and interface  
- **Cross-component communication** via signals (`pyqtSignal`) and timers (`QTimer`)  
- **macOS integration** using **rumps** for status bar control  

---

## 🔮 Future Improvements

- Cross-platform system tray (Windows/Linux support)  
- Task categories and color themes  
- Persistent user preferences  
- Cloud sync (e.g., with Google Tasks API)  

---

## 🧑‍💻 Author

**Pixel Task GUI**  
Developed by *Fish Ahh* — an international student from Taiwan studying in Malaysia.  
Focused on improving Python, GUI development, and English writing skills.

---

## 🪪 License

This project is open-source and available under the MIT License.
