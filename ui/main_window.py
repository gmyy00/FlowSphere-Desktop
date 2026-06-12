# -*- coding: utf-8 -*-
"""
主窗口模块 / Main Window Module

提供应用程序主窗口，包含标题栏、搜索栏和待办事项列表。
Provides the main application window with title bar, search bar, and todo list.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QSize

from core.services.todo_service import TodoService
from ui.todo_card import TodoCard
from ui.recycle_bin import RecycleBinWindow
from ui.base_window import BaseFramelessWindow

# 图标目录 / Icon directory
ICON_DIR = Path(__file__).parent / "source"


class MainWindow(BaseFramelessWindow):
    """
    应用程序主窗口类。
    Main application window class.

    管理标题栏、搜索功能和待办事项卡片列表。
    Manages title bar, search functionality, and todo card list.
    """

    def __init__(self):
        super().__init__("FlowSphere", (500, 500))

        # 初始化待办事项服务 / Initialize todo service
        data_dir = str(Path(__file__).parent.parent / "data")
        self.service = TodoService(data_dir)

        # 主卡片容器 / Main card container
        container = QWidget()
        container.setObjectName("card")
        self.setCentralWidget(container)

        # 标题栏布局 / Header layout
        header = self._create_header("Todos")

        # 回收站按钮 / Recycle bin button
        self._recycle_bin_btn = QPushButton()
        self._recycle_bin_btn.setObjectName("pin_btn")
        self._recycle_bin_btn.setFixedSize(24, 24)
        self._recycle_bin_btn.setIconSize(QSize(18, 18))
        self._recycle_bin_btn.setIcon(self._load_icon("delete-fill.png"))
        self._recycle_bin_btn.clicked.connect(self._open_recycle_bin)
        header.insertWidget(header.count() - 2, self._recycle_bin_btn)

        # 主垂直布局 / Main vertical layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)

        # 搜索输入框 / Search input field
        self._search_input = QLineEdit()
        self._search_input.setObjectName("search")
        self._search_input.setPlaceholderText("Search...")
        self._search_input.textChanged.connect(self._on_search)
        layout.addWidget(self._search_input)

        # 水平分隔线 / Horizontal separator line
        line = QFrame()
        line.setObjectName("separator")
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)

        # 可滚动的待办事项列表 / Scrollable todo list
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

        # 加载待办事项 / Load todos
        self._load_todos()

    def _load_todos(self, todos=None):
        """
        加载待办事项卡片到列表。
        Load todo cards into the list.

        Args:
            todos: 待办事项列表，None 时加载全部 / Todo list, loads all when None
        """
        # 清除现有卡片 / Clear existing cards
        while self._todo_layout.count():
            item = self._todo_layout.takeAt(0)
            if item and (widget := item.widget()):
                widget.deleteLater()

        if todos is None:
            todos = self.service.list_todos()

        for todo in todos:
            card = TodoCard(todo, self.service)
            card.todo_changed.connect(self._on_todo_changed)
            card.todo_deleted.connect(self._on_todo_deleted)
            self._todo_layout.addWidget(card)

    def _on_search(self, text):
        """
        搜索输入框内容变化时的处理。
        Handle search input text changes.

        Args:
            text: 搜索关键词 / Search keyword
        """
        if not text.strip():
            self._load_todos()
        else:
            todos = self.service.search_todos_by_description(text)
            self._load_todos(todos)

    def _on_todo_changed(self, todo_id):
        """
        待办事项状态变化时的处理。
        Handle todo state changes.
        卡片已自行更新，无需额外操作。
        Card updated itself, no additional action needed.

        Args:
            todo_id: 待办事项 ID / Todo item ID
        """
        pass

    def _on_todo_deleted(self, todo_id):
        """
        待办事项被删除时，从列表中移除。
        When a todo is deleted, remove it from the list.

        Args:
            todo_id: 待办事项 ID / Todo item ID
        """
        for i in range(self._todo_layout.count()):
            item = self._todo_layout.itemAt(i)
            if not item:
                continue
            widget = item.widget()
            if not isinstance(widget, TodoCard):
                continue
            if widget.todo.id == todo_id:
                self._todo_layout.removeWidget(widget)
                widget.deleteLater()
                break

    def _open_recycle_bin(self):
        """打开回收站窗口。 / Open recycle bin window."""
        self._recycle_bin = RecycleBinWindow()
        self._recycle_bin.show()
