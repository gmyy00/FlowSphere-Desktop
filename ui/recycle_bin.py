# -*- coding: utf-8 -*-
"""
回收站窗口模块 / Recycle Bin Window Module

创建回收站窗口，显示已删除的待办事项。
Creates the recycle bin window for displaying deleted todos.
"""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PySide6.QtCore import Qt

from ui.base_window import BaseFramelessWindow
from ui.deleted_todo_card import DeletedTodoCard
from core.services.todo_service import TodoService


class RecycleBinWindow(BaseFramelessWindow):
    """
    回收站窗口类。
    Recycle bin window class.

    显示已删除的待办事项，支持恢复和永久删除。
    Displays deleted todos with restore and permanent delete functionality.
    """

    def __init__(self, parent=None):
        super().__init__("Recycle Bin", (300, 400))

        # 初始化待办事项服务 / Initialize todo service
        data_dir = str(Path(__file__).parent.parent / "data")
        self.service = TodoService(data_dir)

        # 主卡片容器 / Main card container
        container = QWidget()
        container.setObjectName("card")
        self.setCentralWidget(container)

        # 主垂直布局 / Main vertical layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self._create_header("Recycle Bin"))

        # 可滚动的已删除待办事项列表 / Scrollable deleted todo list
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

        # 加载已删除的待办事项 / Load deleted todos
        self._load_deleted_todos()

    def _load_deleted_todos(self):
        """加载已删除的待办事项卡片到列表。 / Load deleted todo cards into the list."""
        # 清除现有卡片 / Clear existing cards
        while self._todo_layout.count():
            item = self._todo_layout.takeAt(0)
            if item and (widget := item.widget()):
                widget.deleteLater()

        # 获取已删除的待办事项 / Get deleted todos
        todos = self.service.list_deleted_todos()

        for todo in todos:
            card = DeletedTodoCard(todo, self.service)
            card.todo_recovered.connect(self._on_todo_recovered)
            card.todo_permanently_deleted.connect(self._on_todo_permanently_deleted)
            self._todo_layout.addWidget(card)

    def _on_todo_recovered(self, todo_id):
        """
        待办事项被恢复时，从列表中移除。
        When a todo is restored, remove it from the list.

        Args:
            todo_id: 待办事项 ID / Todo item ID
        """
        self._remove_card_by_id(todo_id)

    def _on_todo_permanently_deleted(self, todo_id):
        """
        待办事项被永久删除时，从列表中移除。
        When a todo is permanently deleted, remove it from the list.

        Args:
            todo_id: 待办事项 ID / Todo item ID
        """
        self._remove_card_by_id(todo_id)

    def _remove_card_by_id(self, todo_id):
        """
        根据 ID 从列表中移除卡片。
        Remove card from list by ID.

        Args:
            todo_id: 待办事项 ID / Todo item ID
        """
        for i in range(self._todo_layout.count()):
            item = self._todo_layout.itemAt(i)
            if not item:
                continue
            widget = item.widget()
            if not isinstance(widget, DeletedTodoCard):
                continue
            if widget.todo.id == todo_id:
                self._todo_layout.removeWidget(widget)
                widget.deleteLater()
                break
