from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont
from utilities.util_load_font import load_font



class UIHeaderText(QLabel):

    def __init__(self, text: str, parent=None, top_margin: int = 180, font_size: int = 24, follow_parent_resize: bool = True):
        base_font = load_font("inter_regular.ttf")
        super().__init__(text, parent)
        family = base_font.family()
        font = QFont(family, font_size, QFont.Normal)
        self.setFont(font)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("color: white; background-color: transparent;")
        self.setAlignment(Qt.AlignCenter)
        self._top_margin = top_margin
        self._update_position()
        if parent is not None and follow_parent_resize:
            parent.installEventFilter(self)

    def _update_position(self):
        parent = self.parent()
        if not parent:
            return
        total_width = parent.width()
        fm = self.fontMetrics()
        height = fm.height()
        self.setGeometry(0, self._top_margin, total_width, height)

    def eventFilter(self, obj, event):
        if obj is self.parent() and event.type() == QEvent.Resize:
            self._update_position()
        return super().eventFilter(obj, event)
