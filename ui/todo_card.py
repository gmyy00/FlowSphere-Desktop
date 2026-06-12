# -*- coding: utf-8 -*-
"""
待办事项卡片模块 / Todo Card Widget Module

创建用于显示单个待办事项的卡片组件，支持切换完成状态、编辑和删除功能。
Creates a card widget for displaying a single Todo item
with toggle, edit, and delete functionality.
"""

from pathlib import Path
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QSizePolicy
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

from core.models.todo import Todo
from core.services.todo_service import TodoService

# 图标目录 / Icon directory
ICON_DIR = Path(__file__).parent / "source"


class TodoCard(QFrame):
    """
    待办事项卡片组件。
    Todo card widget.

    显示单个待办事项的描述、提醒时间、重复规则，并支持切换完成状态和删除。
    Displays a single todo's description, notification time, repeat rule,
    with support for toggling done state and deletion.
    """

    # 信号：待办事项被修改，传递 todo_id / Signal: todo modified, emits todo_id
    todo_changed = Signal(str)
    # 信号：待办事项被删除，传递 todo_id / Signal: todo deleted, emits todo_id
    todo_deleted = Signal(str)

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

        # 复选框按钮 / Checkbox button
        self._checkbox = QPushButton()
        self._checkbox.setObjectName("todo_checkbox")
        self._checkbox.setFixedSize(24, 24)
        self._checkbox.setIconSize(QSize(18, 18))
        self._checkbox.setIcon(self._get_checkbox_icon())
        self._checkbox.clicked.connect(self._toggle_done)
        layout.addWidget(self._checkbox)

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
        text_widget.setStyleSheet("background: transparent;")
        layout.addWidget(text_widget, 1)

        # 操作按钮区域 / Action buttons area
        actions_layout = QVBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(4)

        # 编辑按钮 / Edit button
        self._edit_btn = QPushButton()
        self._edit_btn.setObjectName("todo_edit_btn")
        self._edit_btn.setFixedSize(20, 20)
        self._edit_btn.setIconSize(QSize(14, 14))
        self._edit_btn.setIcon(self._load_icon("edit.png"))
        self._edit_btn.clicked.connect(self._edit_todo)
        actions_layout.addWidget(self._edit_btn)

        # 删除按钮 / Delete button
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
        """
        根据完成状态加载复选框图标。
        Load checkbox icon based on done state.
        """
        name = "checkbox_checked.png" if self.todo.done else "checkbox_unchecked.png"
        return self._load_icon(name)

    def _load_icon(self, name):
        """
        从源目录加载图标。
        Load icon from source directory.

        Args:
            name: 图标文件名 / Icon filename
        """
        return QIcon(str(ICON_DIR / name))

    def _toggle_done(self):
        """切换完成状态并发送信号。 / Toggle done state and emit signal."""
        self.service.toggle_todo(self.todo.id)
        self.todo.done = not self.todo.done
        self._checkbox.setIcon(self._get_checkbox_icon())
        self.todo_changed.emit(self.todo.id)

    def _delete_todo(self):
        """软删除待办事项并发送信号。 / Soft-delete todo and emit signal."""
        self.service.soft_delete_todo(self.todo.id)
        self.todo_deleted.emit(self.todo.id)

    def _edit_todo(self):
        """
        编辑待办事项（预留接口，待后续实现编辑对话框）。
        Edit todo (placeholder for future edit dialog).
        """
        # TODO: 打开编辑对话框 / Open edit dialog
        pass
