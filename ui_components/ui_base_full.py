import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from utilities.util_load_font import load_font



class UIBaseFull:
    def __init__(self):
        load_font("inter_regular.ttf")
        self._create_overlays()

    def _create_overlays(self):
        screens = QGuiApplication.screens()
        if not screens:
            screens = [QGuiApplication.primaryScreen()]
        primary = QGuiApplication.primaryScreen()
        self.overlays = []
        for screen in screens:
            overlay = QMainWindow()
            overlay.setWindowFlags(
                Qt.Window |
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnTopHint
            )
            overlay.setGeometry(screen.geometry())
            overlay.setStyleSheet("background-color: black;")
            overlay.setObjectName(f"overlay_{screen.name()}")
            overlay.is_primary = (screen == primary)
            if overlay.is_primary:
                self.primary_overlay = overlay
            self.overlays.append(overlay)
        if not hasattr(self, "primary_overlay") and self.overlays:
            self.primary_overlay = self.overlays[0]

    def show(self):
        for overlay in self.overlays:
            overlay.showFullScreen()



if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)
    base = UIBaseFull()
    base.show()
    sys.exit(app.exec_())
