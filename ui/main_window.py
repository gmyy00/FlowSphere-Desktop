# -*- coding: utf-8 -*-
"""
主窗口模块 / Main Window Module

提供应用程序主窗口，包含标题栏、搜索栏和待办事项列表。
Provides the main application window with title bar, search bar, and todo list.
"""

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

# 样式表路径 / Stylesheet path
STYLE_PATH = Path(__file__).parent / "style.qss"
# 图标目录 / Icon directory
ICON_DIR = Path(__file__).parent / "source"

# Win32 API 常量，用于窗口置顶 / Win32 API constants for window always-on-top
user32 = ctypes.windll.user32
SWP_NOMOVE = 0x0002      # 不移动位置 / Don't move position
SWP_NOSIZE = 0x0001      # 不改变大小 / Don't change size
SWP_NOACTIVATE = 0x0010  # 不激活窗口 / Don't activate window
HWND_TOPMOST = ctypes.c_void_p(-1)    # 置顶 / Topmost
HWND_NOTOPMOST = ctypes.c_void_p(-2)  # 取消置顶 / Not topmost


class MainWindow(QMainWindow):
    """
    应用程序主窗口类。
    Main application window class.

    管理标题栏、搜索功能和待办事项卡片列表。
    Manages title bar, search functionality, and todo card list.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowSphere")
        # 无边框透明背景窗口 / Frameless window with transparent background
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(350, 550)

        # 记录鼠标位置用于拖拽 / Track mouse position for window dragging
        self._drag_pos = None

        # 初始化待办事项服务 / Initialize todo service
        data_dir = str(Path(__file__).parent.parent / "data")
        self.service = TodoService(data_dir)

        # 加载外部样式表 / Load external stylesheet
        self.setStyleSheet(STYLE_PATH.read_text())

        # 主卡片容器 / Main card container
        container = QWidget()
        container.setObjectName("card")
        self.setCentralWidget(container)

        # 标题栏布局：标题 + 置顶/关闭按钮 / Header layout: title + pin/close buttons
        header = QHBoxLayout()
        header.setContentsMargins(16, 12, 16, 0)

        title = QLabel("Todos")
        title.setObjectName("title")
        header.addWidget(title)

        header.addStretch()

        # 置顶按钮：切换窗口置顶状态 / Pin button: toggles always-on-top state
        pin_btn = QPushButton()
        pin_btn.setObjectName("pin_btn")
        pin_btn.setCheckable(True)
        pin_btn.setFixedSize(24, 24)
        pin_btn.setIconSize(QSize(18, 18))
        pin_btn.setIcon(self._pin_icon(False))
        pin_btn.clicked.connect(self.toggle_pin)
        self._pin_btn = pin_btn
        header.addWidget(pin_btn)

        # 关闭按钮：关闭应用 / Close button: terminates the application
        self._close_btn = QPushButton()
        self._close_btn.setObjectName("close_btn")
        self._close_btn.setFixedSize(24, 24)
        self._close_btn.setIconSize(QSize(18, 18))
        self._close_btn.setIcon(self._close_icon())
        self._close_btn.clicked.connect(self.close)
        header.addWidget(self._close_btn)

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

    # --- 窗口拖拽支持 / Window dragging support ---

    def mousePressEvent(self, event):
        # 左键点击时记录起始位置 / Record starting position on left click
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # 根据鼠标移动量移动窗口 / Move window relative to mouse delta
        if self._drag_pos is not None:
            self.move(self.pos() + event.position().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # 鼠标释放时停止拖拽 / Stop dragging on mouse release
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def toggle_pin(self, checked):
        """
        通过 Win32 API 切换窗口置顶（无闪烁）。
        Toggle always-on-top via Win32 API (no flicker).

        Args:
            checked: 是否选中 / Whether checked
        """
        self._pin_btn.setIcon(self._pin_icon(checked))
        hwnd = ctypes.c_void_p(int(self.winId()))
        insert_after = HWND_TOPMOST if checked else HWND_NOTOPMOST
        user32.SetWindowPos(hwnd, insert_after, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

    def _pin_icon(self, pinned):
        """
        根据状态加载置顶图标。
        Load pin icon based on state.

        Args:
            pinned: 是否已置顶 / Whether pinned
        """
        name = "pin-fill.png" if pinned else "pin.png"
        return QIcon(str(ICON_DIR / name))

    def _close_icon(self):
        """加载关闭图标。 / Load close icon."""
        return QIcon(str(ICON_DIR / "close.png"))
