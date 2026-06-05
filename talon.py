import os
import subprocess
import sys
import threading
import json
import tempfile
import time
import winreg
from types import SimpleNamespace
from configuration_components import install_plan
from configuration_components.localization import t
from screens import load as load_screen
from utilities.util_logger import logger
from utilities.util_error_popup import show_error_popup
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, QEvent, QTimer, Qt, pyqtSignal
from utilities.util_admin_check import ensure_admin
import preinstall_components.pre_checks as pre_checks
import debloat_components.debloat_remove_edge as debloat_remove_edge
import debloat_components.debloat_uninstall_outlook_onedrive as debloat_uninstall_outlook_onedrive
import debloat_components.debloat_browser_installation as debloat_browser_installation
import debloat_components.debloat_execute_winutil as debloat_execute_winutil
import debloat_components.debloat_execute_win11debloat as debloat_execute_win11debloat
import debloat_components.debloat_registry_tweaks as debloat_registry_tweaks
import debloat_components.debloat_configure_updates as debloat_configure_updates
import debloat_components.debloat_apply_background as debloat_apply_background
from ui_components.ui_base_full import UIBaseFull
from ui_components.ui_header_text import UIHeaderText
from ui_components.ui_title_text import UITitleText
from ui_components.ui_loading_spinner import UILoadingSpinner

_INSTALL_UI_BASE = None
TALON_VERSION = "2026.6.2.17"
_COMPLETION_REGISTRY_PATH = r"Software\RavenTechnologiesGroup\Talon"
DEBLOAT_STEPS = [
	(
		"remove-edge-permanently",
		"app.install_overlay.remove_edge",
		debloat_remove_edge.main,
	),
	(
		"uninstall-outlook-onedrive",
		"app.install_overlay.uninstall_outlook_onedrive",
		debloat_uninstall_outlook_onedrive.main,
	),
	(
		"browser-installation",
		"app.install_overlay.browser_installation",
		debloat_browser_installation.main,
	),
	(
		"debloat-windows-phase-one",
		"app.install_overlay.debloat_windows_phase_one",
		debloat_execute_winutil.main,
	),
	(
		"debloat-windows-phase-two",
		"app.install_overlay.debloat_windows_phase_two",
		debloat_execute_win11debloat.main,
	),
	(
		"registry-tweaks",
		"app.install_overlay.registry_tweaks",
		debloat_registry_tweaks.main,
	),
	(
		"configure-updates",
		"app.install_overlay.configure_updates",
		debloat_configure_updates.main,
	),
	(
		"apply-background",
		"app.install_overlay.apply_background",
		debloat_apply_background.main,
	),
]


def _launch_developer_console(raw_args) -> bool:
	script_path = os.path.abspath(__file__)
	python_cmd = [sys.executable, script_path] + list(raw_args)
	command_line = subprocess.list2cmdline(python_cmd)
	env = dict(os.environ)
	env["TALON_DEV_CONSOLE"] = "1"
	try:
		subprocess.Popen(
			["cmd.exe", "/k", command_line],
			creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
			env=env,
		)
		return True
	except Exception as e:
		logger.exception(f"Failed to launch developer console window: {e}")
		show_error_popup(
			t("errors.developer_console_failed", {"error": e}),
			allow_continue=False,
		)
		return False

def parse_args(argv=None):
	def _parse_bool(value: str) -> bool:
		v = str(value).strip().lower()
		if v in ("1", "true", "yes", "on"):
			return True
		if v in ("0", "false", "no", "off"):
			return False
		raise ValueError(f"Invalid boolean value: {value}")

	raw = sys.argv[1:] if argv is None else list(argv)
	args = SimpleNamespace()
	args.developer_mode = False
	args.headless = False
	args.dry_run = False
	args.config = None
	for slug, _, _ in DEBLOAT_STEPS:
		setattr(args, f"skip_{slug.replace('-', '_')}_step", False)

	step_lookup = {slug: f"skip_{slug.replace('-', '_')}_step" for slug, _, _ in DEBLOAT_STEPS}
	alias_lookup = {
		"developer-mode": "developer_mode",
		"headless": "headless",
		"dry-run": "dry_run",
		"config": "config",
	}

	for token in raw:
		if "=" not in token:
			raise SystemExit(
				f"Invalid argument '{token}'. Use key=value format, e.g. configure-updates=false."
			)
		key, value = token.split("=", 1)
		key = key.strip().lower()
		value = value.strip()

		if key in alias_lookup:
			attr = alias_lookup[key]
			if attr == "config":
				args.config = value
			else:
				setattr(args, attr, _parse_bool(value))
			continue

		if key in step_lookup:
			enabled = _parse_bool(value)
			setattr(args, step_lookup[key], not enabled)
			continue

		raise SystemExit(
			f"Unknown argument key '{key}'. Supported keys: developer-mode, headless, dry-run, config, "
			+ ", ".join(step_lookup.keys())
		)

	return args

def run_screen(module_name: str):
	logger.debug(f"Launching screen: {module_name}")
	try:
		mod = load_screen(module_name)
	except ImportError:
		script_file = f"{module_name}.py"
		script_path = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			"screens",
			script_file,
		)
		try:
			subprocess.run([sys.executable, script_path], check=True)
		except Exception as e:
			logger.error(f"Failed to launch screen {script_file}: {e}")
			show_error_popup(
				t("errors.screen_launch_failed", {"module_name": module_name, "error": e}),
				allow_continue=False,
			)
			sys.exit(1)
		return
	try:
		return mod.main()
	except SystemExit:
		return False
	except Exception as e:
		logger.exception(f"Exception in screen '{module_name}': {e}")
		show_error_popup(
			t("errors.screen_unexpected", {"module_name": module_name, "error": e}),
			allow_continue=False,
		)
		sys.exit(1)


def _install_plan_path() -> str:
	return install_plan.install_plan_path()


def _load_install_plan() -> dict:
	return install_plan.load_install_plan()


def _build_execution_steps_from_plan(plan: dict):
	step_lookup = {slug: (message, func) for slug, message, func in DEBLOAT_STEPS}
	items = plan.get("items", [])
	selected_browser = str(plan.get("selected_browser_package", "")).strip()
	ordered = []
	if isinstance(items, list):
		for raw in items:
			if not isinstance(raw, dict):
				continue
			key = str(raw.get("key", "")).strip()
			enabled = bool(raw.get("enabled", False))
			if key not in step_lookup:
				continue
			if key == "browser-installation" and not selected_browser:
				enabled = False
			ordered.append((key, enabled) + step_lookup[key])
	return ordered


def _execution_config_path(args, plan: dict):
	if args.config:
		return args.config, False
	try:
		winutil_cfg = plan.get("winutil_config")
		if not isinstance(winutil_cfg, (dict, list)):
			return None, False
		raw_args = str(plan.get("win11debloat_args", "")).strip()
		win11_args = [part for part in raw_args.split() if part]
		payload = {
			"WinUtil": winutil_cfg,
			"Win11Debloat": {"Args": win11_args},
		}
		fd, tmp_path = tempfile.mkstemp(prefix="talon_install_plan_runtime_", suffix=".json")
		with os.fdopen(fd, "w", encoding="utf-8") as f:
			json.dump(payload, f, indent=2)
		return tmp_path, True
	except Exception:
		return None, False

def _build_install_ui():
	app = QApplication.instance() or QApplication(sys.argv)
	base = UIBaseFull()
	for overlay in base.overlays:
		overlay.setWindowOpacity(0.8)
	overlay = base.primary_overlay
	title_label = UITitleText(t("app.install_overlay.title"), parent=overlay)
	UIHeaderText(
		t("app.install_overlay.guidance"),
		parent=overlay,
	)
	status_label = UIHeaderText("", parent=overlay, follow_parent_resize=False)

	class StatusResizer(QObject):
		def __init__(self, parent, label, bottom_margin):
			super().__init__(parent)
			self.parent = parent
			self.label = label
			self.bottom_margin = bottom_margin
			parent.installEventFilter(self)
			self._update_position()
		def eventFilter(self, obj, event):
			if obj is self.parent and event.type() == QEvent.Resize:
				self._update_position()
			return False
		def _update_position(self):
			w = self.parent.width()
			fm = self.label.fontMetrics()
			h = fm.height()
			y = self.parent.height() - self.bottom_margin - h
			self.label.setGeometry(0, y, w, h)

	StatusResizer(overlay, status_label, bottom_margin=title_label._top_margin)
	spinner = UILoadingSpinner(overlay, dim_background=False, dim_opacity=0.0, duration_ms=1800, block_input=True)

	class _SpinnerBus(QObject):
		start = pyqtSignal()
		stop = pyqtSignal()
		raiseit = pyqtSignal()
		set_msg = pyqtSignal(str)
		quit_later = pyqtSignal()
	bus = _SpinnerBus()
	bus.start.connect(spinner.start, Qt.QueuedConnection)
	bus.stop.connect(spinner.stop, Qt.QueuedConnection)
	bus.raiseit.connect(spinner.raise_, Qt.QueuedConnection)
	bus.set_msg.connect(status_label.setText, Qt.QueuedConnection)
	bus.quit_later.connect(lambda: QTimer.singleShot(2500, app.quit), Qt.QueuedConnection)
	base.show()
	status_label.raise_()
	spinner.raise_()
	return app, status_label, base, spinner, bus

def _update_status(bus, label: UIHeaderText, message: str):
	if label is None:
		print(message)
		return
	bus.set_msg.emit(message)
	bus.raiseit.emit()

def _record_debloat_completion():
	epoch_utc = int(time.time())
	access = winreg.KEY_WRITE
	if hasattr(winreg, "KEY_WOW64_64KEY"):
		access |= winreg.KEY_WOW64_64KEY
	with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, _COMPLETION_REGISTRY_PATH, 0, access) as key:
		winreg.SetValueEx(key, "Version", 0, winreg.REG_SZ, TALON_VERSION)
		winreg.SetValueEx(key, "DebloatRanUtc", 0, winreg.REG_QWORD, epoch_utc)
	logger.info(
		f"Recorded Talon completion marker: HKLM\\{_COMPLETION_REGISTRY_PATH} "
		f"Version={TALON_VERSION}, DebloatRanUtc={epoch_utc}"
	)


def main(argv=None):
	raw_args = sys.argv[1:] if argv is None else list(argv)
	args = parse_args(argv)
	if (
		args.developer_mode
		and not args.headless
		and os.environ.get("TALON_DEV_CONSOLE") != "1"
	):
		if _launch_developer_console(raw_args):
			return
		sys.exit(1)
	if args.headless:
		args.developer_mode = True
		args.skip_browser_installation_step = True
	if args.dry_run:
		os.environ["TALON_DRY_RUN"] = "1"
		logger.info("Dry-run mode enabled; execution steps will be previewed without modifying the system.")
	if args.config:
		config_path = os.path.abspath(args.config)
		if not os.path.isfile(config_path):
			msg = t("errors.config_not_found", {"path": config_path})
			logger.error(msg)
			show_error_popup(msg, allow_continue=False)
			sys.exit(1)
		args.config = config_path
	plan = {}
	runtime_config_path = args.config
	runtime_config_is_temp = False
	runtime_registry_changes = None
	runtime_selected_browser_package = ""
	runtime_applied_background_path = ""
	execution_steps = [(slug, True, message, func) for slug, message, func in DEBLOAT_STEPS]
	if not args.headless:
		start_requested = bool(run_screen("screen_configuration"))
		if not start_requested:
			logger.info("Initial window closed without Start; exiting before debloat process starts.")
			return
		plan = _load_install_plan()
		execution_steps = _build_execution_steps_from_plan(plan)
		if not execution_steps:
			msg = t("errors.empty_execution_plan")
			logger.error(msg)
			show_error_popup(msg, allow_continue=False)
			return
		runtime_registry_changes = plan.get("registry_changes")
		runtime_selected_browser_package = str(plan.get("selected_browser_package", "")).strip()
		runtime_applied_background_path = str(plan.get("applied_background_path", "")).strip()
		for raw in plan.get("items", []):
			if isinstance(raw, dict) and str(raw.get("key", "")).strip() == "developer-mode":
				if bool(raw.get("enabled", False)):
					args.developer_mode = True
				break
		if not args.dry_run:
			runtime_config_path, runtime_config_is_temp = _execution_config_path(args, plan)
	else:
		if not args.dry_run:
			ensure_admin()
			pre_checks.main()
	app = None
	status_label = None
	spinner = None
	bus = None
	if not args.developer_mode:
		global _INSTALL_UI_BASE
		app, status_label, _INSTALL_UI_BASE, spinner, bus = _build_install_ui()

	def _cleanup_runtime_config():
		if not runtime_config_is_temp or not runtime_config_path:
			return
		try:
			if os.path.isfile(runtime_config_path):
				os.remove(runtime_config_path)
		except Exception as e:
			logger.warning(f"Failed to clean temporary runtime config '{runtime_config_path}': {e}")

	def debloat_sequence():
		try:
			if bus is not None:
				bus.start.emit()
				bus.raiseit.emit()
			for slug, enabled, message, func in execution_steps:
				if not enabled:
					logger.info(f"Skipping {slug} step (disabled in install_plan)")
					continue
				if getattr(args, f"skip_{slug.replace('-', '_')}_step", False):
					logger.info(f"Skipping {slug} step")
					continue
				_update_status(bus, status_label, t(message))
				if args.dry_run:
					logger.info(f"Dry-run: would run {slug} step")
					if not args.headless and not args.developer_mode:
						time.sleep(0.8)
					continue
				try:
					if slug in ("debloat-windows-phase-one", "debloat-windows-phase-two"):
						func(runtime_config_path)
					elif slug == "browser-installation":
						func(runtime_selected_browser_package)
					elif slug == "registry-tweaks":
						func(runtime_registry_changes)
					elif slug == "apply-background":
						func(runtime_applied_background_path)
					else:
						func()
				except Exception:
					logger.exception("Debloat step failed")
					if bus is not None:
						bus.stop.emit()
					if not args.headless:
						show_error_popup(
							t("errors.installation_unexpected"),
							allow_continue=False,
						)
					return
			if args.dry_run:
				msg = t("app.install_overlay.dry_run_complete")
				_update_status(bus, status_label, msg)
				if bus is not None:
					bus.stop.emit()
					bus.quit_later.emit()
				return
			try:
				_record_debloat_completion()
			except Exception as e:
				logger.exception(f"Failed to record Talon completion marker: {e}")
				if not args.headless:
					show_error_popup(
						t("errors.completion_marker_failed", {"error": e}),
						allow_continue=True,
					)
			_update_status(bus, status_label, t("app.install_overlay.complete_no_restart"))
			if bus is not None:
				bus.stop.emit()
				bus.quit_later.emit()
			return
		finally:
			_cleanup_runtime_config()

	if args.developer_mode or args.headless:
		debloat_sequence()
	else:
		def start_thread():
			threading.Thread(target=debloat_sequence, daemon=True).start()
		QTimer.singleShot(0, start_thread)
		sys.exit(app.exec_())

if __name__ == "__main__":
	main()
