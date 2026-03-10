import os
import ctypes
import subprocess
import sys
import threading
import json
import tempfile
from types import SimpleNamespace
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
DEBLOAT_STEPS = [
	(
		"remove-edge-permanently",
		"Removing Microsoft Edge permanently...",
		debloat_remove_edge.main,
	),
	(
		"uninstall-outlook-onedrive",
		"Uninstalling Outlook and OneDrive...",
		debloat_uninstall_outlook_onedrive.main,
	),
	(
		"browser-installation",
		"Installing your chosen browser...",
		debloat_browser_installation.main,
	),
	(
		"debloat-windows-phase-one",
		"Debloating Windows phase one (WinUtil)...",
		debloat_execute_winutil.main,
	),
	(
		"debloat-windows-phase-two",
		"Debloating Windows phase two (Win11Debloat)...",
		debloat_execute_win11debloat.main,
	),
	(
		"registry-tweaks",
		"Making some visual tweaks...",
		debloat_registry_tweaks.main,
	),
	(
		"configure-updates",
		"Configuring Windows Update policies...",
		debloat_configure_updates.main,
	),
	(
		"apply-background",
		"Setting your desktop background...",
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
			f"Failed to launch Developer Mode console window.\n{e}",
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
	args.config = None
	for slug, _, _ in DEBLOAT_STEPS:
		setattr(args, f"skip_{slug.replace('-', '_')}_step", False)

	step_lookup = {slug: f"skip_{slug.replace('-', '_')}_step" for slug, _, _ in DEBLOAT_STEPS}
	alias_lookup = {
		"developer-mode": "developer_mode",
		"headless": "headless",
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
			f"Unknown argument key '{key}'. Supported keys: developer-mode, headless, config, "
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
				f"Failed to launch screen '{module_name}'.\n{e}",
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
			f"An unexpected error occurred in screen '{module_name}'.\n{e}",
			allow_continue=False,
		)
		sys.exit(1)


def _install_plan_path() -> str:
	return os.path.join(os.environ.get("TEMP", tempfile.gettempdir()), "talon", "install_plan.json")


def _load_install_plan() -> dict:
	path = _install_plan_path()
	if not os.path.isfile(path):
		return {}
	try:
		with open(path, "r", encoding="utf-8") as f:
			data = json.load(f)
		return data if isinstance(data, dict) else {}
	except Exception:
		return {}


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
		if not isinstance(winutil_cfg, dict):
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
	title_label = UITitleText("Talon is installing", parent=overlay)
	UIHeaderText(
		"Please don't use your keyboard or mouse. You can watch as Talon works.",
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
	bus = _SpinnerBus()
	bus.start.connect(spinner.start, Qt.QueuedConnection)
	bus.stop.connect(spinner.stop, Qt.QueuedConnection)
	bus.raiseit.connect(spinner.raise_, Qt.QueuedConnection)
	bus.set_msg.connect(status_label.setText, Qt.QueuedConnection)
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

def _enable_shutdown_privilege():
	advapi32 = ctypes.windll.advapi32
	kernel32 = ctypes.windll.kernel32
	token = ctypes.c_void_p()
	if not advapi32.OpenProcessToken(kernel32.GetCurrentProcess(), 0x0020 | 0x0008, ctypes.byref(token)):
		raise ctypes.WinError()
	try:
		luid = ctypes.c_longlong()
		if not advapi32.LookupPrivilegeValueW(None, "SeShutdownPrivilege", ctypes.byref(luid)):
			raise ctypes.WinError()
		class LUID_AND_ATTRIBUTES(ctypes.Structure):
			_fields_ = [("Luid", ctypes.c_longlong), ("Attributes", ctypes.c_ulong)]
		class TOKEN_PRIVILEGES(ctypes.Structure):
			_fields_ = [("PrivilegeCount", ctypes.c_ulong), ("Privileges", LUID_AND_ATTRIBUTES * 1)]
		tp = TOKEN_PRIVILEGES()
		tp.PrivilegeCount = 1
		tp.Privileges[0].Luid = luid.value
		tp.Privileges[0].Attributes = 0x00000002
		if not advapi32.AdjustTokenPrivileges(token, False, ctypes.byref(tp), 0, None, None):
			raise ctypes.WinError()
	finally:
		kernel32.CloseHandle(token)

def _restart_windows():
	_enable_shutdown_privilege()
	user32 = ctypes.windll.user32
	if not user32.ExitWindowsEx(0x00000002, 0x80000000):
		raise ctypes.WinError()

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
	if args.config:
		config_path = os.path.abspath(args.config)
		if not os.path.isfile(config_path):
			msg = f"Config file not found: {config_path}"
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
		start_requested = bool(run_screen("screen_initial_blank"))
		if not start_requested:
			logger.info("Initial window closed without Start; exiting before debloat process starts.")
			return
		plan = _load_install_plan()
		execution_steps = _build_execution_steps_from_plan(plan)
		if not execution_steps:
			msg = "Install plan has no executable steps. Open Talon UI and configure at least one step."
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
		runtime_config_path, runtime_config_is_temp = _execution_config_path(args, plan)
	else:
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
				_update_status(bus, status_label, message)
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
							"An unexpected error occurred during installation.\nCheck the log for details.",
							allow_continue=False,
						)
					return
			if args.headless or args.developer_mode:
				if args.headless:
					msg = "Suppressing system restart due to headless mode."
				else:
					msg = "Suppressing system restart due to developer mode."
				_update_status(bus, status_label, msg)
				if bus is not None:
					bus.stop.emit()
				return
			else:
				_update_status(bus, status_label, "Restarting system...")
				if bus is not None:
					bus.stop.emit()
				try:
					_restart_windows()
				except Exception as e:
					logger.exception(f"Failed to restart system: {e}")
					if not args.headless:
						show_error_popup(
							"Failed to restart the system.\nCheck the log for details.",
							allow_continue=False,
						)
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
