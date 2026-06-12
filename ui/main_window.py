from pathlib import Path
import ctypes
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from core.services.todo_service import TodoService
from ui.todo_card import TodoCard

STYLE_PATH = Path(__file__).parent / "style.qss"
ICON_DIR = Path(__file__).parent / "source"

# Win32 API
user32 = ctypes.windll.user32
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
HWND_TOPMOST = ctypes.c_void_p(-1)
HWND_NOTOPMOST = ctypes.c_void_p(-2)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowSphere")
        # Frameless window with transparent background
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(350, 550)

        # Track mouse position for window dragging
        self._drag_pos = None

        # Initialize todo service
        data_dir = str(Path(__file__).parent.parent / "data")
        self.service = TodoService(data_dir)

        # Load external stylesheet
        self.setStyleSheet(STYLE_PATH.read_text())

        # Main card container
        container = QWidget()
        container.setObjectName("card")
        self.setCentralWidget(container)

        # Header layout: title + pin/close buttons
        header = QHBoxLayout()
        header.setContentsMargins(16, 12, 16, 0)

        title = QLabel("Todos")
        title.setObjectName("title")
        header.addWidget(title)

        header.addStretch()

        # Pin button: toggles always-on-top state
        pin_btn = QPushButton()
        pin_btn.setObjectName("pin_btn")
        pin_btn.setCheckable(True)
        pin_btn.setFixedSize(24, 24)
        pin_btn.setIconSize(QSize(18, 18))
        pin_btn.setIcon(self._pin_icon(False))
        pin_btn.clicked.connect(self.toggle_pin)
        self._pin_btn = pin_btn
        header.addWidget(pin_btn)

        # Close button: terminates the application
        self._close_btn = QPushButton()
        self._close_btn.setObjectName("close_btn")
        self._close_btn.setFixedSize(24, 24)
        self._close_btn.setIconSize(QSize(18, 18))
        self._close_btn.setIcon(self._close_icon())
        self._close_btn.clicked.connect(self.close)
        header.addWidget(self._close_btn)

        # Main vertical layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)

        # Search input field
        self._search_input = QLineEdit()
        self._search_input.setObjectName("search")
        self._search_input.setPlaceholderText("Search...")
        self._search_input.textChanged.connect(self._on_search)
        layout.addWidget(self._search_input)

        # Horizontal separator line
        line = QFrame()
        line.setObjectName("separator")
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)

        # Scrollable todo list
        scroll = QScrollArea()
        scroll.setObjectName("todo_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._todo_list = QWidget()
        self._todo_list.setObjectName("todo_list")
        self._todo_layout = QVBoxLayout(self._todo_list)
        self._todo_layout.setContentsMargins(0, 0, 0, 0)
        self._todo_layout.setSpacing(4)
        self._todo_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self._todo_list)

        layout.addWidget(scroll, 1)

        # Load todos
        self._load_todos()

    def _load_todos(self, todos=None):
        """Populate the list with todo cards."""
        # Clear existing cards
        while self._todo_layout.count():
            item = self._todo_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if todos is None:
            todos = self.service.list_todos()

        for todo in todos:
            card = TodoCard(todo, self.service)
            card.todo_changed.connect(self._on_todo_changed)
            card.todo_deleted.connect(self._on_todo_deleted)
            self._todo_layout.addWidget(card)

    def _on_search(self, text):
        """Filter todos by search text."""
        if not text.strip():
            self._load_todos()
        else:
            todos = self.service.search_todos_by_description(text)
            self._load_todos(todos)

    def _on_todo_changed(self, todo_id):
        """Handle todo state change."""
        pass  # Card already updated itself

    def _on_todo_deleted(self, todo_id):
        """Remove deleted todo from list."""
        for i in range(self._todo_layout.count()):
            item = self._todo_layout.itemAt(i)
            widget = item.widget()
            if widget and hasattr(widget, 'todo') and widget.todo.id == todo_id:
                self._todo_layout.removeWidget(widget)
                widget.deleteLater()
                break

    # --- Window dragging support ---

    def mousePressEvent(self, event):
        # Record starting position on left click
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Move window relative to mouse delta
        if self._drag_pos is not None:
            self.move(self.pos() + event.position().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Stop dragging on mouse release
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def toggle_pin(self, checked):
        """Toggle always-on-top via Win32 API (no flicker)."""
        self._pin_btn.setIcon(self._pin_icon(checked))
        hwnd = ctypes.c_void_p(int(self.winId()))
        insert_after = HWND_TOPMOST if checked else HWND_NOTOPMOST
        user32.SetWindowPos(hwnd, insert_after, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

    def _pin_icon(self, pinned):
        """Load pin icon based on state."""
        name = "pin-fill.png" if pinned else "pin.png"
        return QIcon(str(ICON_DIR / name))

    def _close_icon(self):
        """Load close icon."""
        return QIcon(str(ICON_DIR / "close.png"))
