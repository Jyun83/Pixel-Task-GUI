import sys
import os
from typing import Optional

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QProgressBar, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtSignal, QEasingCurve
from PyQt6.QtGui import QFont, QFontDatabase

class PixelLoadingOverlay(QWidget):
    """A pixel-style loading overlay widget that displays animated text and a progress bar.

    This widget shows a fade-in effect, a typing animation for a given text,
    and a progress bar that fills over a set duration. When the animation
    completes, it automatically fades out and emits a `finished` signal.

    Attributes:
        finished (pyqtSignal): Emitted when the loading animation finishes and fades out.
        duration_ms (int): Total duration of the progress bar animation in milliseconds.
        fade_duration_ms (int): Duration for fade-in and fade-out transitions.
        full_text (str): The complete text to display with the typing effect.
        pixel_font (QFont): The font used for the displayed text.
    """

    finished = pyqtSignal()

    def __init__(self, duration_ms: int, text: str = "LOADING...", font_path: Optional[str] = None) -> None:
        """Initializes the PixelLoadingOverlay with the given duration and text.

        Args:
            duration_ms (int): Duration for the progress bar animation (in milliseconds).
            text (str, optional): Text displayed with typing effect. Defaults to "LOADING...".
            font_path (Optional[str], optional): Path to a custom font file. If not provided,
                uses a default monospace font.
        """
        super().__init__()

        self.duration_ms: int = duration_ms
        self.fade_duration_ms: int = 800  # milliseconds for fade in/out
        self.full_text: str = text
        self.char_index: int = 0

        # --- Transparent frameless window ---
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # --- Load pixel font if available ---
        font_name = "Menlo"
        if font_path and os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_name = QFontDatabase.applicationFontFamilies(font_id)[0]

        self.pixel_font: QFont = QFont(font_name, 48, QFont.Weight.Bold)

        # --- Layout setup ---
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(60, 60, 60, 60)

        # --- Typing label ---
        self.label = QLabel("", self)
        self.label.setFont(self.pixel_font)
        self.label.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Progress bar ---
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedSize(600, 32)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.1);
                border: 4px solid white;
                border-radius: 0px;  /* pixel style */
            }
            QProgressBar::chunk {
                background-color: white;
                border-radius: 0px;
                margin: 0px;
            }
        """)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Center the overlay ---
        screen = QApplication.primaryScreen().geometry() # type: ignore
        self.resize(720, 240)
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

        # --- Animation and timer placeholders ---
        self.fade_in_anim: Optional[QPropertyAnimation] = None
        self.fade_out_anim: Optional[QPropertyAnimation] = None
        self.typing_timer: Optional[QTimer] = None
        self.progress_anim: Optional[QPropertyAnimation] = None

        # --- Start all animations ---
        self.start_animation()

    # ---------------------------------------------------------------------

    def start_animation(self) -> None:
        """Starts the fade-in, typing, and progress animations."""
        self.setWindowOpacity(0.0)

        # Fade in animation
        self.fade_in_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self.fade_in_anim.setDuration(self.fade_duration_ms)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        self.fade_in_anim.start()

        # Typing animation
        self.char_index = 0
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self.type_next_char)
        self.typing_timer.start(200)

        # Progress bar animation
        self.progress_anim = QPropertyAnimation(self.progress, b"value", self)
        self.progress_anim.setDuration(self.duration_ms)
        self.progress_anim.setStartValue(0)
        self.progress_anim.setEndValue(100)
        self.progress_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.progress_anim.finished.connect(self.fade_out)
        self.progress_anim.start()

    # ---------------------------------------------------------------------

    def type_next_char(self) -> None:
        """Displays the next character in the typing animation."""
        if self.char_index < len(self.full_text):
            current_text = self.full_text[:self.char_index + 1]
            self.char_index += 1
            self.label.setText(current_text)
        else:
            if self.typing_timer is not None and self.typing_timer.isActive():
                self.typing_timer.stop()


    # ---------------------------------------------------------------------

    def fade_out(self) -> None:
        """Triggers a fade-out effect after the animation finishes."""
        if self.typing_timer and self.typing_timer.isActive():
            self.typing_timer.stop()

        if self.fade_out_anim:
            self.fade_out_anim.stop()
            self.fade_out_anim.deleteLater()

        self.fade_out_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self.fade_out_anim.setDuration(self.fade_duration_ms)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        self.fade_out_anim.finished.connect(self._on_fade_finished)
        self.fade_out_anim.start()

    # ---------------------------------------------------------------------

    def _on_fade_finished(self) -> None:
        """Cleans up resources and emits the `finished` signal."""
        for anim in [self.fade_in_anim, self.fade_out_anim, self.progress_anim]:
            if anim:
                try:
                    anim.stop()
                    anim.deleteLater()
                except Exception:
                    pass

        if self.typing_timer and self.typing_timer.isActive():
            self.typing_timer.stop()

        self.close()
        self.finished.emit()

    # ---------------------------------------------------------------------

    def closeEvent(self, event) -> None:  # type: ignore
        """Ensures all timers and animations stop before closing."""
        self._on_fade_finished()
        event.accept()

# ---------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)

    overlay = PixelLoadingOverlay(
        duration_ms=3000,
        text="LOADING...",
        font_path="/Users/turing/Desktop/Monash/FIT1045/Code/D/DisposableDroidBB.ttf"
    )
    overlay.show()

    def safe_exit() -> None:
        """Safely exit the app after a short delay (prevents macOS crash)."""
        QTimer.singleShot(150, app.quit)

    overlay.finished.connect(safe_exit)
    sys.exit(app.exec())
