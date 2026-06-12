# -*- coding: utf-8 -*-
"""
TodoCard widget module.

Creates a card widget for displaying a single Todo item
with toggle, edit, and delete functionality.
"""

from pathlib import Path
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QSizePolicy
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

from core.models.todo import Todo
from core.services.todo_service import TodoService

ICON_DIR = Path(__file__).parent / "source"


class TodoCard(QFrame):
    """A card widget representing a single Todo item."""

    todo_changed = Signal(str)  # emitted with todo_id when todo is modified
    todo_deleted = Signal(str)  # emitted with todo_id when todo is deleted

    def __init__(self, todo: Todo, service: TodoService, parent=None):
        super().__init__(parent)
        self.todo = todo
        self.service = service
        self.setObjectName("todo_card")
        # Let height be determined by content
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._setup_ui()

    def _setup_ui(self):
        """Build the card layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Checkbox button
        self._checkbox = QPushButton()
        self._checkbox.setObjectName("todo_checkbox")
        self._checkbox.setFixedSize(24, 24)
        self._checkbox.setIconSize(QSize(18, 18))
        self._checkbox.setIcon(self._get_checkbox_icon())
        self._checkbox.clicked.connect(self._toggle_done)
        layout.addWidget(self._checkbox)

        # Text info area
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        # Description
        desc = QLabel(self.todo.description)
        desc.setObjectName("todo_description")
        desc.setWordWrap(True)
        text_layout.addWidget(desc)

        # Info line: notification + repeat
        info_parts = []
        if self.todo.notification:
            # Format: "2026-06-15 17:30"
            info_parts.append(self.todo.notification.replace("T", " "))
        if self.todo.repeat and self.todo.repeat != "none":
            info_parts.append(self.todo.repeat)
        info_text = "  |  ".join(info_parts) if info_parts else ""

        if info_text:
            info = QLabel(info_text)
            info.setObjectName("todo_info")
            text_layout.addWidget(info)

        text_widget = QWidget()
        text_widget.setLayout(text_layout)
        text_widget.setStyleSheet("background: transparent;")
        layout.addWidget(text_widget, 1)

        # Action buttons
        actions_layout = QVBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(4)

        # Edit button
        self._edit_btn = QPushButton()
        self._edit_btn.setObjectName("todo_edit_btn")
        self._edit_btn.setFixedSize(20, 20)
        self._edit_btn.setIconSize(QSize(14, 14))
        self._edit_btn.setIcon(self._load_icon("edit.png"))
        self._edit_btn.clicked.connect(self._edit_todo)
        actions_layout.addWidget(self._edit_btn)

        # Delete button
        self._delete_btn = QPushButton()
        self._delete_btn.setObjectName("todo_delete_btn")
        self._delete_btn.setFixedSize(20, 20)
        self._delete_btn.setIconSize(QSize(14, 14))
        self._delete_btn.setIcon(self._load_icon("delete.png"))
        self._delete_btn.clicked.connect(self._delete_todo)
        actions_layout.addWidget(self._delete_btn)

        actions_widget = QWidget()
        actions_widget.setLayout(actions_layout)
        actions_widget.setStyleSheet("background: transparent;")
        layout.addWidget(actions_widget)

    def _get_checkbox_icon(self):
        """Load checkbox icon based on done state."""
        name = "checkbox_checked.png" if self.todo.done else "checkbox_unchecked.png"
        return self._load_icon(name)

    def _load_icon(self, name):
        """Load icon from source directory."""
        return QIcon(str(ICON_DIR / name))

    def _toggle_done(self):
        """Toggle done state and emit signal."""
        self.service.toggle_todo(self.todo.id)
        self.todo.done = not self.todo.done
        self._checkbox.setIcon(self._get_checkbox_icon())
        self.todo_changed.emit(self.todo.id)

    def _delete_todo(self):
        """Soft-delete todo and emit signal."""
        self.service.soft_delete_todo(self.todo.id)
        self.todo_deleted.emit(self.todo.id)

    def _edit_todo(self):
        """Emit signal for edit (placeholder for future dialog)."""
        # TODO: Open edit dialog
        pass
