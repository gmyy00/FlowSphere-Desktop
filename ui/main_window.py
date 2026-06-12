from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtCore import Qt, QPoint

STYLE_PATH = Path(__file__).parent / "style.qss"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowSphere")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 500)

        self._drag_pos = None

        self.setStyleSheet(STYLE_PATH.read_text())

        container = QWidget()
        container.setObjectName("card")
        self.setCentralWidget(container)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(self.pos() + event.position().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)
