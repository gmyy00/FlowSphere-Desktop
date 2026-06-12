# -*- coding: utf-8 -*-
"""
已删除待办事项卡片模块 / Deleted Todo Card Widget Module

创建用于显示已删除待办事项的卡片组件，支持恢复和永久删除功能。
Creates a card widget for displaying a deleted Todo item
with restore and permanent delete functionality.
"""

from pathlib import Path
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QSizePolicy
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

from core.models.todo import Todo
from core.services.todo_service import TodoService

# 图标目录 / Icon directory
ICON_DIR = Path(__file__).parent / "source"


class DeletedTodoCard(QFrame):
    """
    已删除待办事项卡片组件。
    Deleted todo card widget.

    显示已删除待办事项的描述、提醒时间、重复规则，并支持恢复和永久删除。
    Displays a deleted todo's description, notification time, repeat rule,
    with support for restore and permanent deletion.
    """

    # 信号：待办事项被恢复，传递 todo_id / Signal: todo restored, emits todo_id
    todo_recovered = Signal(str)
    # 信号：待办事项被永久删除，传递 todo_id / Signal: todo permanently deleted, emits todo_id
    todo_permanently_deleted = Signal(str)

    def __init__(self, todo: Todo, service: TodoService, parent=None):
        """
        初始化卡片。
        Initialize the card.

        Args:
            todo: 待办事项数据对象 / Todo data object
            service: 待办事项服务实例 / Todo service instance
            parent: 父组件 / Parent widget
        """
        super().__init__(parent)
        self.todo = todo
        self.service = service
        self.setObjectName("todo_card")
        # 高度由内容决定 / Height determined by content
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._setup_ui()

    def _setup_ui(self):
        """构建卡片布局。 / Build the card layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 文本信息区域 / Text info area
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        # 描述文本 / Description text
        desc = QLabel(self.todo.description)
        desc.setObjectName("todo_description")
        desc.setWordWrap(True)
        text_layout.addWidget(desc)

        # 信息行：提醒时间 + 重复规则 / Info line: notification + repeat
        info_parts = []
        if self.todo.notification:
            # 格式化：将 T 替换为空格 / Format: replace T with space
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
        layout.addWidget(text_widget, 1)

        # 操作按钮区域 / Action buttons area
        actions_layout = QVBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(4)

        # 恢复按钮 / Restore button
        self._restore_btn = QPushButton()
        self._restore_btn.setObjectName("todo_restore_btn")
        self._restore_btn.setFixedSize(20, 20)
        self._restore_btn.setIconSize(QSize(14, 14))
        self._restore_btn.setIcon(self._load_icon("restore.png"))
        self._restore_btn.clicked.connect(self._restore_todo)
        actions_layout.addWidget(self._restore_btn)

        # 永久删除按钮 / Purge button
        self._purge_btn = QPushButton()
        self._purge_btn.setObjectName("todo_purge_btn")
        self._purge_btn.setFixedSize(20, 20)
        self._purge_btn.setIconSize(QSize(14, 14))
        self._purge_btn.setIcon(self._load_icon("purge.png"))
        self._purge_btn.clicked.connect(self._purge_todo)
        actions_layout.addWidget(self._purge_btn)

        actions_widget = QWidget()
        actions_widget.setObjectName("todo_actions")
        actions_widget.setLayout(actions_layout)
        layout.addWidget(actions_widget)

    def _load_icon(self, name):
        """
        从源目录加载图标。
        Load icon from source directory.

        Args:
            name: 图标文件名 / Icon filename
        """
        return QIcon(str(ICON_DIR / name))

    def _restore_todo(self):
        """恢复待办事项并发送信号。 / Restore todo and emit signal."""
        self.service.restore_todo(self.todo.id)
        self.todo_recovered.emit(self.todo.id)

    def _purge_todo(self):
        """永久删除待办事项并发送信号。 / Permanently delete todo and emit signal."""
        self.service.permanent_delete_todo(self.todo.id)
        self.todo_permanently_deleted.emit(self.todo.id)
