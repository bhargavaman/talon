import ast
import json
import os
import re
import sys
import tempfile
import threading
from pathlib import Path

from PyQt5.QtCore import QObject, QTimer, QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication, QFileDialog

import debloat_components.debloat_registry_tweaks as debloat_registry_tweaks
import preinstall_components.pre_checks as pre_checks
from utilities.util_admin_check import is_admin, run_as_admin
from utilities.util_error_popup import show_error_popup
from utilities.util_internet_check import has_internet

_BROWSER_TOOLTIPS = {
    "brave": (
        "Brave is the recommended browser, as it is the closest to Chrome while "
        "respecting your privacy."
    ),
    "microsoft-edge": (
        "Edge is not recommended unless necessary for your purposes, as it is very "
        "invasive to your privacy and embeds ads."
    ),
    "waterfox": (
        "Waterfox is recommended over Firefox, but not Brave. It's based on Firefox, "
        "but removes tracking and telemetry."
    ),
    "librewolf": (
        "LibreWolf is only recommended for tech-savvy users. It is designed for "
        "maximum privacy and security, but can be harder to use."
    ),
    "firefox": (
        "Firefox is not recommended unless necessary for your purposes, as it includes "
        "telemetry and sponsored content by default."
    ),
}

_DEFAULT_STEP_PRESENTATION = {
    "remove-edge-permanently": {
        "text": "Remove Microsoft Edge permanently",
        "tooltip": (
            "Uninstalls Microsoft Edge, and ensures it doesn't come back. You can always "
            "reinstall it yourself if you want. Apps that rely on it (msedgewebview2) will still work."
        ),
    },
    "uninstall-outlook-onedrive": {
        "text": "Uninstall Outlook & OneDrive",
        "tooltip": (
            "Uninstalls the Outlook app and OneDrive, as many people do not use them. "
            "You can always reinstall them yourself if you want."
        ),
    },
    "browser-installation": {
        "text": "Install web browser",
        "tooltip": "No browser selected yet.",
    },
    "debloat-windows-phase-one": {
        "text": "Debloat Windows phase one (WinUtil)",
        "tooltip": (
            "Talon uses a popular and well-established tool, WinUtil by ChrisTitusTech, "
            "as part of its debloating process. The whole process is automated, so you "
            "don't need to do anything. It is not recommended to remove this step."
        ),
    },
    "debloat-windows-phase-two": {
        "text": "Debloat Windows phase two (Win11Debloat)",
        "tooltip": (
            "Talon uses a popular and well-established tool, Win11Debloat by Raphire, as "
            "part of its debloating process. The whole process is automated, so you don't "
            "need to do anything. It is not recommended to remove this step."
        ),
    },
    "registry-tweaks": {
        "text": "Make visual adjustments to desktop",
        "tooltip": (
            "Modifies the Windows Registry to make your desktop look and feel better, "
            "including but not limited to changing your taskbar to be left-aligned, setting "
            "your theme to dark theme, removing delay in menus, and showing file extensions."
        ),
    },
    "configure-updates": {
        "text": "Set security-only update policy",
        "tooltip": (
            "In order to prevent Windows updates from reintroducing bloat and undoing the "
            "changes made, Talon sets an update policy on your system which results in only "
            "receiving security updates, leaving out non-security \"feature\" updates. It "
            "lasts permanently on Windows Pro, but only 365 days on Windows Home."
        ),
    },
    "apply-background": {
        "text": "Apply desktop background",
        "tooltip": (
            "To complete the look of a freshly debloated system, Talon sets your desktop "
            "background to a custom Raven-branded one. The exact desktop background of "
            "choice is configurable in the Advanced settings."
        ),
    },
}

_DEFAULT_OPTION_PRESENTATION = {
    "developer-mode": {
        "text": "Developer mode (hide installation overlay)",
        "tooltip": "When enabled, Talon runs without showing the full-screen install overlay.",
    }
}

_DEFAULT_WINUTIL_CONFIG = {
    "WPFTweaks": [
        "WPFTweaksActivity",
        "WPFTweaksConsumerFeatures",
        "WPFTweaksDisableBGapps",
        "WPFTweaksLocation",
        "WPFTweaksTelemetry",
        "WPFTweaksWPBT",
        "WPFTweaksWidget",
        "WPFTweaksServices",
        "WPFTweaksDeleteTempFiles",
        "WPFTweaksDisableExplorerAutoDiscovery",
        "WPFTweaksDisplay",
        "WPFTweaksRightClickMenu",
        "WPFTweaksRevertStartMenu",
        "WPFTweaksRemoveOneDrive",
        "WPFTweaksXboxRemoval",
        "WPFTweaksRemoveHome",
        "WPFTweaksRemoveGallery",
        "WPFTweaksDeBloat",
        "WPFTweaksRemoveCopilot",
    ]
}

_DEFAULT_WIN11DEBLOAT_ARGS = [
    "-Silent",
    "-RemoveApps",
    "-RemoveGamingApps",
    "-DisableTelemetry",
    "-DisableBing",
    "-DisableSuggestions",
    "-DisableLockscreenTips",
    "-RevertContextMenu",
    "-TaskbarAlignLeft",
    "-HideSearchTb",
    "-DisableWidgets",
    "-DisableCopilot",
    "-ClearStartAllUsers",
    "-DisableDVR",
    "-DisableStartRecommended",
    "-ExplorerToThisPC",
    "-DisableMouseAcceleration",
    "-DisableDesktopSpotlight",
    "-DisableSettings365Ads",
    "-DisableSettingsHome",
    "-DisablePaintAI",
    "-DisableNotepadAI",
    "-DisableStickyKeys",
]

_INSTALL_PLAN_VERSION = 1


class InitialScreenBridge(QObject):
    def __init__(self):
        super().__init__()
        self.start_requested = False
        self._reset_install_plan_defaults()

    @staticmethod
    def _talon_dir() -> str:
        temp_root = os.environ.get("TEMP", tempfile.gettempdir())
        return os.path.join(temp_root, "talon")

    @classmethod
    def _install_plan_path(cls) -> str:
        return os.path.join(cls._talon_dir(), "install_plan.json")

    @staticmethod
    def _metadata_keys() -> tuple:
        return ("winutil_config", "win11debloat_args", "registry_changes", "applied_background_path")

    @classmethod
    def _default_win11debloat_args_text(cls) -> str:
        return " ".join(_DEFAULT_WIN11DEBLOAT_ARGS)

    @staticmethod
    def _normalize_win11debloat_args_text(text: str) -> str:
        return re.sub(r"\s+", " ", str(text).strip())

    @staticmethod
    def _format_win11debloat_args_for_editor(value) -> str:
        if isinstance(value, list):
            cleaned = [str(v).strip() for v in value if str(v).strip()]
            return "\n".join(cleaned)
        compact = re.sub(r"\s+", " ", str(value).strip())
        if not compact:
            return ""
        return "\n".join([part for part in compact.split(" ") if part])

    @staticmethod
    def _default_winutil_config():
        return json.loads(json.dumps(_DEFAULT_WINUTIL_CONFIG))

    @staticmethod
    def _default_registry_changes():
        try:
            return debloat_registry_tweaks.default_registry_changes_payload()
        except Exception:
            return []

    @classmethod
    def _normalize_winutil_config(cls, value):
        if isinstance(value, dict) and "payload" in value:
            payload = value.get("payload")
            if isinstance(payload, (dict, list)):
                value = payload
        if isinstance(value, dict) and "WinUtil" in value and isinstance(value["WinUtil"], dict):
            value = value["WinUtil"]
        if isinstance(value, list):
            tweaks = [str(v).strip() for v in value if str(v).strip()]
            return {"WPFTweaks": tweaks}
        if isinstance(value, dict):
            normalized = {}
            for key, raw_val in value.items():
                if key == "WPFTweaks" and isinstance(raw_val, list):
                    normalized[key] = [str(v).strip() for v in raw_val if str(v).strip()]
                else:
                    normalized[key] = raw_val
            return normalized
        return cls._default_winutil_config()

    @classmethod
    def _normalize_registry_changes(cls, value):
        if value is None:
            return cls._default_registry_changes()
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return cls._default_registry_changes()
            try:
                value = json.loads(stripped)
            except Exception:
                return cls._default_registry_changes()
        if isinstance(value, (dict, list)):
            return value
        return cls._default_registry_changes()

    @classmethod
    def _normalize_metadata_fields(cls, data: dict):
        if not isinstance(data, dict):
            return
        data["winutil_config"] = cls._normalize_winutil_config(data.get("winutil_config"))
        args_raw = data.get("win11debloat_args", cls._default_win11debloat_args_text())
        if isinstance(args_raw, list):
            args_raw = " ".join([str(v).strip() for v in args_raw if str(v).strip()])
        data["win11debloat_args"] = cls._normalize_win11debloat_args_text(
            args_raw if str(args_raw).strip() else cls._default_win11debloat_args_text()
        )
        data["registry_changes"] = cls._normalize_registry_changes(data.get("registry_changes"))
        data["applied_background_path"] = str(data.get("applied_background_path", "")).strip()

    @staticmethod
    def _browser_tooltip(browser_package: str) -> str:
        return _BROWSER_TOOLTIPS.get(browser_package, "No browser selected yet.")

    @staticmethod
    def _to_title_label(key: str) -> str:
        parts = str(key).replace("-", " ").split()
        return " ".join(p[:1].upper() + p[1:] for p in parts)

    @classmethod
    def _discover_step_slugs(cls) -> list:
        talon_path = Path(__file__).resolve().parents[1] / "talon.py"
        fallback = [
            "remove-edge-permanently",
            "uninstall-outlook-onedrive",
            "browser-installation",
            "debloat-windows-phase-one",
            "debloat-windows-phase-two",
            "registry-tweaks",
            "configure-updates",
            "apply-background",
        ]
        try:
            src = talon_path.read_text(encoding="utf-8")
            tree = ast.parse(src, filename=str(talon_path))
            for node in tree.body:
                if not isinstance(node, ast.Assign):
                    continue
                if not any(isinstance(t, ast.Name) and t.id == "DEBLOAT_STEPS" for t in node.targets):
                    continue
                if not isinstance(node.value, (ast.List, ast.Tuple)):
                    continue
                slugs = []
                for item in node.value.elts:
                    if not isinstance(item, (ast.List, ast.Tuple)) or len(item.elts) < 1:
                        continue
                    first = item.elts[0]
                    if isinstance(first, ast.Constant) and isinstance(first.value, str):
                        slugs.append(first.value)
                return slugs or fallback
        except Exception:
            return fallback
        return fallback

    @classmethod
    def _discover_bool_option_slugs(cls, step_slugs: list) -> list:
        talon_path = Path(__file__).resolve().parents[1] / "talon.py"
        fallback = ["developer-mode"]
        try:
            src = talon_path.read_text(encoding="utf-8")
            tree = ast.parse(src, filename=str(talon_path))
            for fn in tree.body:
                if not isinstance(fn, ast.FunctionDef) or fn.name != "parse_args":
                    continue
                for node in fn.body:
                    if not isinstance(node, ast.Assign):
                        continue
                    if not any(isinstance(t, ast.Name) and t.id == "alias_lookup" for t in node.targets):
                        continue
                    if not isinstance(node.value, ast.Dict):
                        continue
                    keys = []
                    for k in node.value.keys:
                        if isinstance(k, ast.Constant) and isinstance(k.value, str):
                            keys.append(k.value)
                    result = []
                    for key in keys:
                        if key in ("headless", "config"):
                            continue
                        if key in step_slugs:
                            continue
                        result.append(key)
                    return result or fallback
        except Exception:
            return fallback
        return fallback

    @classmethod
    def _step_presentation_overrides(cls) -> dict:
        overrides = dict(_DEFAULT_STEP_PRESENTATION)
        for k, v in _DEFAULT_OPTION_PRESENTATION.items():
            overrides[k] = dict(v)
        custom_path = Path(__file__).resolve().parents[1] / "configs" / "step_presentation.json"
        if not custom_path.is_file():
            return overrides
        try:
            raw = json.loads(custom_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                for key, value in raw.items():
                    if not isinstance(value, dict):
                        continue
                    text = value.get("text")
                    tooltip = value.get("tooltip")
                    entry = dict(overrides.get(key, {}))
                    if text is not None:
                        entry["text"] = str(text)
                    if tooltip is not None:
                        entry["tooltip"] = str(tooltip)
                    overrides[key] = entry
        except Exception:
            pass
        return overrides

    @staticmethod
    def _browser_step_text(browser_name: str) -> str:
        return f"Install web browser: {browser_name}"

    @classmethod
    def _build_install_plan(
        cls,
        browser_name: str = "None",
        browser_package: str = "",
        include_browser_install: bool = False,
    ) -> dict:
        slugs = cls._discover_step_slugs()
        option_slugs = cls._discover_bool_option_slugs(slugs)
        presentation = cls._step_presentation_overrides()
        items = []
        for slug in option_slugs + slugs:
            present = presentation.get(slug, {})
            text = str(present.get("text", cls._to_title_label(slug)))
            tooltip = str(present.get("tooltip", ""))
            enabled = False if slug in option_slugs else True
            item = {"key": slug, "text": text, "tooltip": tooltip, "enabled": enabled}
            if slug == "browser-installation":
                item["text"] = cls._browser_step_text(browser_name)
                item["tooltip"] = cls._browser_tooltip(browser_package)
                item["enabled"] = bool(include_browser_install)
            items.append(item)

        return {
            "version": _INSTALL_PLAN_VERSION,
            "selected_browser_name": browser_name,
            "selected_browser_package": browser_package,
            "include_browser_install": include_browser_install,
            "items": items,
            "winutil_config": cls._default_winutil_config(),
            "win11debloat_args": cls._default_win11debloat_args_text(),
            "registry_changes": cls._default_registry_changes(),
            "applied_background_path": "",
        }

    @staticmethod
    def _normalize_item(item) -> dict:
        if isinstance(item, dict):
            return {
                "key": str(item.get("key", "")),
                "text": str(item.get("text", "")),
                "tooltip": str(item.get("tooltip", "")),
                "enabled": bool(item.get("enabled", False)),
            }
        return {"key": "", "text": str(item), "tooltip": "", "enabled": False}

    def _normalize_imported_plan(self, payload: dict) -> dict:
        if not isinstance(payload, dict):
            raise ValueError("Install plan must be a JSON object.")
        incoming_version = payload.get("version", _INSTALL_PLAN_VERSION)
        if not isinstance(incoming_version, int):
            raise ValueError("Install plan field 'version' must be an integer.")
        if incoming_version < 1:
            raise ValueError("Install plan field 'version' must be >= 1.")
        if "items" not in payload:
            raise ValueError("Install plan is missing required field: items.")
        if not isinstance(payload.get("items"), list):
            raise ValueError("Install plan field 'items' must be a list.")

        browser_name = str(payload.get("selected_browser_name", "None"))
        browser_package = str(payload.get("selected_browser_package", ""))
        include_browser_install = bool(payload.get("include_browser_install", False))
        normalized = self._build_install_plan(
            browser_name=browser_name,
            browser_package=browser_package,
            include_browser_install=include_browser_install,
        )
        normalized["version"] = incoming_version

        default_keys = {item["key"] for item in normalized["items"]}
        imported_by_key = {}
        unknown_items = []
        for raw in payload.get("items", []):
            n = self._normalize_item(raw)
            if not n["key"]:
                continue
            if n["key"] in default_keys:
                imported_by_key[n["key"]] = n
            else:
                unknown_items.append(n)

        for item in normalized["items"]:
            imported = imported_by_key.get(item["key"])
            if imported is None:
                continue
            item["text"] = imported["text"] or item["text"]
            item["tooltip"] = imported["tooltip"] or item["tooltip"]
            item["enabled"] = bool(imported["enabled"])
        normalized["items"].extend(unknown_items)

        if not normalized["selected_browser_package"]:
            for item in normalized["items"]:
                if item["key"] == "browser-installation":
                    item["enabled"] = False
                    break
        normalized["include_browser_install"] = any(
            it["key"] == "browser-installation" and bool(it["enabled"])
            for it in normalized["items"]
        )
        for key in self._metadata_keys():
            if key in payload:
                normalized[key] = payload.get(key)
        self._normalize_metadata_fields(normalized)
        return normalized

    def _ensure_install_plan_file(self):
        os.makedirs(self._talon_dir(), exist_ok=True)
        plan_path = self._install_plan_path()
        if not os.path.isfile(plan_path):
            with open(plan_path, "w", encoding="utf-8") as f:
                json.dump(self._build_install_plan(), f, indent=2)
            return
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("plan root must be an object")
            items = data.get("items", [])
            if not isinstance(items, list):
                raise ValueError("install plan items is not a list")

            normalized = self._build_install_plan(
                browser_name=str(data.get("selected_browser_name", "None")),
                browser_package=str(data.get("selected_browser_package", "")),
                include_browser_install=bool(data.get("include_browser_install", False)),
            )
            existing_version = data.get("version", _INSTALL_PLAN_VERSION)
            if not isinstance(existing_version, int) or existing_version < 1:
                existing_version = _INSTALL_PLAN_VERSION
            normalized["version"] = existing_version
            existing_enabled_by_key = {}
            for raw in items:
                n = self._normalize_item(raw)
                if n["key"]:
                    existing_enabled_by_key[n["key"]] = bool(n["enabled"])
            for item in normalized["items"]:
                if item["key"] in existing_enabled_by_key:
                    item["enabled"] = existing_enabled_by_key[item["key"]]
            if not normalized["selected_browser_package"]:
                for item in normalized["items"]:
                    if item["key"] == "browser-installation":
                        item["enabled"] = False
                        break
            normalized["include_browser_install"] = any(
                it["key"] == "browser-installation" and bool(it["enabled"])
                for it in normalized["items"]
            )
            for key in self._metadata_keys():
                if key in data:
                    normalized[key] = data.get(key)
            self._normalize_metadata_fields(normalized)
            with open(plan_path, "w", encoding="utf-8") as f:
                json.dump(normalized, f, indent=2)
        except Exception:
            with open(plan_path, "w", encoding="utf-8") as f:
                json.dump(self._build_install_plan(), f, indent=2)

    def _reset_install_plan_defaults(self):
        os.makedirs(self._talon_dir(), exist_ok=True)
        with open(self._install_plan_path(), "w", encoding="utf-8") as f:
            json.dump(
                self._build_install_plan(
                    browser_name="None",
                    browser_package="",
                    include_browser_install=False,
                ),
                f,
                indent=2,
            )

    def _load_install_plan(self) -> dict:
        self._ensure_install_plan_file()
        try:
            with open(self._install_plan_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("plan root must be an object")
            if not isinstance(data.get("items", []), list):
                data["items"] = []
            original = json.dumps(data, sort_keys=True)
            self._normalize_metadata_fields(data)
            if json.dumps(data, sort_keys=True) != original:
                self._save_install_plan(data)
            return data
        except Exception:
            return self._build_install_plan()

    def _save_install_plan(self, data: dict):
        with open(self._install_plan_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def set_internet_available(self, available: bool):
        if available:
            return
        try:
            data = self._load_install_plan()
            items = [self._normalize_item(item) for item in data.get("items", [])]
            for item in items:
                if item["key"] == "browser-installation":
                    item["enabled"] = False
                    break
            data["items"] = items
            data["include_browser_install"] = False
            self._save_install_plan(data)
        except Exception:
            return

    @classmethod
    def _find_browser_item_index(cls, items: list) -> int:
        for i, item in enumerate(items):
            n = cls._normalize_item(item)
            if n["key"] == "browser-installation":
                return i
        return -1

    @staticmethod
    def _enabled_plan_keys(data: dict) -> list:
        keys = []
        selected_browser = str(data.get("selected_browser_package", "")).strip()
        for item in data.get("items", []):
            n = InitialScreenBridge._normalize_item(item)
            if not n["key"] or not n["enabled"]:
                continue
            if n["key"] == "browser-installation" and not selected_browser:
                continue
            keys.append(n["key"])
        return keys

    @pyqtSlot(result="QVariantList")
    def getInstallPlanItems(self):
        try:
            data = self._load_install_plan()
            out = []
            for item in data.get("items", []):
                n = self._normalize_item(item)
                if not n["enabled"]:
                    continue
                if n["key"] == "browser-installation" and not data.get("selected_browser_package", ""):
                    continue
                out.append({"key": n["key"], "text": n["text"], "tooltip": n["tooltip"]})
            return out
        except Exception:
            fallback = self._build_install_plan()
            return [
                {"key": i["key"], "text": i["text"], "tooltip": i["tooltip"]}
                for i in fallback["items"]
                if i.get("enabled", False)
            ]

    @pyqtSlot(result="QVariantMap")
    def getExecutionPlan(self):
        try:
            data = self._load_install_plan()
        except Exception:
            data = self._build_install_plan()
        return {
            "version": int(data.get("version", _INSTALL_PLAN_VERSION)),
            "enabled_keys": self._enabled_plan_keys(data),
            "metadata": {
                "selected_browser_package": str(data.get("selected_browser_package", "")),
                "selected_browser_name": str(data.get("selected_browser_name", "None")),
                "winutil_config": data.get("winutil_config", self._default_winutil_config()),
                "win11debloat_args": str(data.get("win11debloat_args", self._default_win11debloat_args_text())),
                "registry_changes": data.get("registry_changes", self._default_registry_changes()),
                "applied_background_path": str(data.get("applied_background_path", "")),
            },
        }

    @pyqtSlot(result="QVariantList")
    def getAdvancedArgs(self):
        try:
            data = self._load_install_plan()
            items = [self._normalize_item(item) for item in data.get("items", [])]
            return [{"key": it["key"], "label": it["text"], "value": bool(it["enabled"])} for it in items]
        except Exception:
            return [{"key": i["key"], "label": i["text"], "value": bool(i["enabled"])} for i in self._build_install_plan()["items"]]

    @pyqtSlot(str)
    def toggleAdvancedArg(self, key: str):
        try:
            data = self._load_install_plan()
            items = [self._normalize_item(item) for item in data.get("items", [])]
            for it in items:
                if it["key"] == key:
                    it["enabled"] = not bool(it["enabled"])
                    break
            if not data.get("selected_browser_package", ""):
                for it in items:
                    if it["key"] == "browser-installation":
                        it["enabled"] = False
                        break
            data["items"] = items
            data["include_browser_install"] = any(it["key"] == "browser-installation" and bool(it["enabled"]) for it in items)
            self._save_install_plan(data)
        except Exception:
            return

    @pyqtSlot(int)
    def removeInstallPlanItem(self, index: int):
        try:
            data = self._load_install_plan()
            items = [self._normalize_item(item) for item in data.get("items", [])]
            enabled_items = []
            for item in items:
                if item["enabled"]:
                    if item["key"] == "browser-installation" and not data.get("selected_browser_package", ""):
                        continue
                    enabled_items.append(item)
            if 0 <= index < len(enabled_items):
                remove_key = enabled_items[index]["key"]
                for item in items:
                    if item["key"] == remove_key:
                        item["enabled"] = False
                        break
            data["items"] = items
            data["include_browser_install"] = any(it["key"] == "browser-installation" and bool(it["enabled"]) for it in items)
            self._save_install_plan(data)
        except Exception:
            return

    @pyqtSlot(str)
    @pyqtSlot(str, str)
    def selectBrowser(self, package_id: str, browser_name: str = "Unknown"):
        data = self._load_install_plan()
        items = [self._normalize_item(item) for item in data.get("items", [])]
        idx = self._find_browser_item_index(items)
        if idx >= 0:
            items[idx]["text"] = self._browser_step_text(browser_name)
            items[idx]["tooltip"] = self._browser_tooltip(package_id)
            items[idx]["enabled"] = True
        data["items"] = items
        data["selected_browser_name"] = browser_name
        data["selected_browser_package"] = package_id
        data["include_browser_install"] = True
        self._save_install_plan(data)

    @pyqtSlot()
    def skipBrowserInstall(self):
        data = self._load_install_plan()
        items = [self._normalize_item(item) for item in data.get("items", [])]
        idx = self._find_browser_item_index(items)
        if idx >= 0:
            items[idx]["enabled"] = False
        data["items"] = items
        data["selected_browser_name"] = "None"
        data["selected_browser_package"] = ""
        data["include_browser_install"] = False
        self._save_install_plan(data)

    @pyqtSlot()
    def resetInstallPlanDefaults(self):
        self._reset_install_plan_defaults()

    @pyqtSlot()
    def importInstallPlan(self):
        try:
            path, _ = QFileDialog.getOpenFileName(None, "Import Talon Install Plan", "", "JSON Files (*.json);;All Files (*)")
            if not path:
                return
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            normalized = self._normalize_imported_plan(payload)
            self._save_install_plan(normalized)
        except Exception as e:
            show_error_popup(f"Failed to import install plan:\n{e}", allow_continue=True)

    @pyqtSlot()
    def importWinUtilConfig(self):
        try:
            path, _ = QFileDialog.getOpenFileName(None, "Import WinUtil Config", "", "JSON Files (*.json);;All Files (*)")
            if not path:
                return
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if not isinstance(payload, (dict, list)):
                raise ValueError("WinUtil config must be a JSON object or array.")
            data = self._load_install_plan()
            data["winutil_config"] = self._normalize_winutil_config(payload)
            self._save_install_plan(data)
        except Exception as e:
            show_error_popup(f"Failed to import WinUtil config:\n{e}", allow_continue=True)

    @pyqtSlot()
    def exportInstallPlan(self):
        try:
            data = self._load_install_plan()
            path, _ = QFileDialog.getSaveFileName(None, "Export As Install Plan", "install_plan.json", "JSON Files (*.json);;All Files (*)")
            if not path:
                return
            if not path.lower().endswith(".json"):
                path = f"{path}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            show_error_popup(f"Failed to export install plan:\n{e}", allow_continue=True)

    @pyqtSlot()
    def setAppliedBackground(self):
        try:
            path, _ = QFileDialog.getOpenFileName(
                None,
                "Set Applied Background",
                "",
                "Images (*.png *.jpg *.jpeg *.bmp *.webp);;All Files (*)",
            )
            if not path:
                return
            if not os.path.isfile(path):
                raise ValueError("Selected image file does not exist.")
            data = self._load_install_plan()
            data["applied_background_path"] = os.path.abspath(path)
            self._save_install_plan(data)
        except Exception as e:
            show_error_popup(f"Failed to set applied background:\n{e}", allow_continue=True)

    @pyqtSlot()
    def startDebloat(self):
        self.start_requested = True
        app = QApplication.instance()
        if app is not None:
            app.quit()

    @pyqtSlot(result=str)
    def getWin11DebloatArgsText(self):
        try:
            data = self._load_install_plan()
            return self._format_win11debloat_args_for_editor(data.get("win11debloat_args", ""))
        except Exception:
            return ""

    @pyqtSlot(str, result=bool)
    def saveWin11DebloatArgsText(self, text: str):
        try:
            data = self._load_install_plan()
            data["win11debloat_args"] = self._normalize_win11debloat_args_text(text)
            self._save_install_plan(data)
            return True
        except Exception as e:
            show_error_popup(f"Failed to save Win11Debloat arguments:\n{e}", allow_continue=True)
            return False

    @pyqtSlot(result=str)
    def getRegistryChangesText(self):
        try:
            data = self._load_install_plan()
            value = data.get("registry_changes", None)
            if value is None:
                return ""
            if isinstance(value, str):
                return value
            return json.dumps(value, indent=2)
        except Exception:
            return ""

    @pyqtSlot(str, result=bool)
    def saveRegistryChangesText(self, text: str):
        try:
            raw = str(text).strip()
            parsed = None
            if raw:
                parsed = json.loads(raw)
                if not isinstance(parsed, (dict, list)):
                    raise ValueError("Registry changes must be a JSON object or array.")
            data = self._load_install_plan()
            data["registry_changes"] = parsed
            self._save_install_plan(data)
            return True
        except Exception as e:
            show_error_popup(f"Failed to save registry changes:\n{e}", allow_continue=True)
            return False


class CheckSignals(QObject):
    checks_passed = pyqtSignal(bool)
    checks_failed = pyqtSignal(str)
    relaunching = pyqtSignal()


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.warnings.connect(lambda errs: [print(f"[QML] {e.toString()}") for e in errs])
    bridge = InitialScreenBridge()
    engine.rootContext().setContextProperty("bridge", bridge)
    qml_path = Path(__file__).resolve().parents[1] / "ui" / "initial" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        raise RuntimeError(f"Failed to load QML: {qml_path}")

    root = engine.rootObjects()[0]
    signals = CheckSignals()

    def _on_checks_passed(internet_available: bool):
        root.setProperty("internetAvailable", bool(internet_available))
        root.setProperty("currentPage", 1)

    signals.checks_passed.connect(_on_checks_passed)
    signals.checks_failed.connect(lambda message: print(f"[initial_blank] check flow failed: {message}"))
    signals.checks_failed.connect(lambda _message: app.quit())
    signals.relaunching.connect(app.quit)

    def run_checks():
        try:
            if not is_admin():
                run_as_admin()
                signals.relaunching.emit()
                return
            pre_checks.main()
            internet_available = has_internet()
            bridge.set_internet_available(internet_available)
            signals.checks_passed.emit(internet_available)
        except BaseException as e:
            signals.checks_failed.emit(str(e))

    QTimer.singleShot(0, lambda: threading.Thread(target=run_checks, daemon=True).start())
    app.exec_()
    return bool(bridge.start_requested)


if __name__ == "__main__":
    sys.exit(0 if main() else 0)
