# -*- coding: utf-8 -*-
"""
无边框窗口基类模块 / Base Frameless Window Module

提供可拖拽、可置顶的无边框窗口基类。
Provides a draggable, pinnable frameless window base class.
"""

from pathlib import Path
import ctypes
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

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


class BaseFramelessWindow(QMainWindow):
    """
    无边框窗口基类。
    Base frameless window class.

    提供窗口拖拽、置顶切换等通用功能。
    Provides common features like window dragging and pin toggle.
    """

    def __init__(self, title, size=(350, 550)):
        super().__init__()
        self.setWindowTitle(title)
        # 无边框透明背景窗口 / Frameless window with transparent background
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(*size)

        # 记录鼠标位置用于拖拽 / Track mouse position for window dragging
        self._drag_pos = None

        # 加载外部样式表 / Load external stylesheet
        self.setStyleSheet(STYLE_PATH.read_text())

    # --- 窗口拖拽支持 / Window dragging support ---

    def mousePressEvent(self, event):
        """左键点击时记录起始位置。 / Record starting position on left click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """根据鼠标移动量移动窗口。 / Move window relative to mouse delta."""
        if self._drag_pos is not None:
            self.move(self.pos() + event.position().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放时停止拖拽。 / Stop dragging on mouse release."""
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

    def _load_icon(self, name):
        """
        从源目录加载图标。
        Load icon from source directory.

        Args:
            name: 图标文件名 / Icon filename
        """
        return QIcon(str(ICON_DIR / name))

    def _create_header(self, title_text):
        """
        创建标题栏布局。
        Create header layout.

        Args:
            title_text: 标题文本 / Title text

        Returns:
            QHBoxLayout: 标题栏布局 / Header layout
        """
        header = QHBoxLayout()
        header.setContentsMargins(16, 12, 16, 0)

        title = QLabel(title_text)
        title.setObjectName("title")
        header.addWidget(title)

        header.addStretch()

        # 置顶按钮 / Pin button
        self._pin_btn = QPushButton()
        self._pin_btn.setObjectName("pin_btn")
        self._pin_btn.setCheckable(True)
        self._pin_btn.setFixedSize(24, 24)
        self._pin_btn.setIconSize(QSize(18, 18))
        self._pin_btn.setIcon(self._pin_icon(False))
        self._pin_btn.clicked.connect(self.toggle_pin)
        header.addWidget(self._pin_btn)

        # 关闭按钮 / Close button
        close_btn = QPushButton()
        close_btn.setObjectName("close_btn")
        close_btn.setFixedSize(24, 24)
        close_btn.setIconSize(QSize(18, 18))
        close_btn.setIcon(self._close_icon())
        close_btn.clicked.connect(self.close)
        header.addWidget(close_btn)

        return header
