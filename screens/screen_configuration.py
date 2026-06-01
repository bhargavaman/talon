import sys
import threading
from pathlib import Path

from PyQt5.QtCore import QObject, QTimer, QUrl, pyqtSignal
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication

from configuration_components.preflight import run_configuration_preflight
from configuration_components.qt_bridge import ConfigurationBridge
from configuration_components.localization import LocalizationBridge


class CheckSignals(QObject):
    checks_passed = pyqtSignal(bool)
    checks_failed = pyqtSignal(str)
    relaunching = pyqtSignal()


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.warnings.connect(lambda errs: [print(f"[configuration] {e.toString()}") for e in errs])
    bridge = ConfigurationBridge()
    i18n = LocalizationBridge()
    engine.rootContext().setContextProperty("bridge", bridge)
    engine.rootContext().setContextProperty("i18n", i18n)
    qml_path = Path(__file__).resolve().parents[1] / "ui" / "configuration" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        raise RuntimeError(f"Failed to load QML: {qml_path}")

    root = engine.rootObjects()[0]
    signals = CheckSignals()

    def _on_checks_passed(internet_available: bool):
        root.setProperty("internetAvailable", bool(internet_available))
        root.setProperty("currentPage", 1)

    signals.checks_passed.connect(_on_checks_passed)
    signals.checks_failed.connect(lambda message: print(f"[configuration] check flow failed: {message}"))
    signals.checks_failed.connect(lambda _message: app.quit())
    signals.relaunching.connect(app.quit)

    def run_checks():
        try:
            internet_available, relaunched = run_configuration_preflight()
            if relaunched:
                signals.relaunching.emit()
                return
            bridge.set_internet_available(internet_available)
            signals.checks_passed.emit(internet_available)
        except BaseException as e:
            signals.checks_failed.emit(str(e))

    QTimer.singleShot(0, lambda: threading.Thread(target=run_checks, daemon=True).start())
    app.exec_()
    return bool(bridge.start_requested)


if __name__ == "__main__":
    sys.exit(0 if main() else 0)
