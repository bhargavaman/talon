import json
import os

from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication, QFileDialog

from configuration_components import install_plan, step_catalog
from configuration_components.localization import t
from utilities.util_error_popup import show_error_popup


class ConfigurationBridge(QObject):
    def __init__(self):
        super().__init__()
        self.start_requested = False
        install_plan.reset_install_plan_defaults()

    def set_internet_available(self, available: bool):
        try:
            install_plan.apply_internet_availability(available)
        except Exception:
            return

    @pyqtSlot(result="QVariantList")
    def getBrowserOptions(self):
        return step_catalog.browser_options()

    @pyqtSlot(result="QVariantList")
    def getInstallPlanItems(self):
        try:
            return install_plan.visible_enabled_items(install_plan.load_install_plan())
        except Exception:
            return install_plan.visible_enabled_items(install_plan.build_install_plan())

    @pyqtSlot(result="QVariantList")
    def getPresetOptions(self):
        return step_catalog.preset_options()

    @pyqtSlot(result=str)
    def getSelectedPresetKey(self):
        try:
            data = install_plan.load_install_plan()
            return str(data.get("selected_preset_key", step_catalog.STANDARD_PRESET_KEY))
        except Exception:
            return step_catalog.STANDARD_PRESET_KEY

    @pyqtSlot(result="QVariantMap")
    def getExecutionPlan(self):
        try:
            data = install_plan.load_install_plan()
        except Exception:
            data = install_plan.build_install_plan()
        return {
            "version": int(data.get("version", install_plan.INSTALL_PLAN_VERSION)),
            "enabled_keys": install_plan.enabled_plan_keys(data),
            "metadata": {
                "selected_browser_package": str(data.get("selected_browser_package", "")),
                "selected_browser_name": str(data.get("selected_browser_name", "None")),
                "winutil_config": data.get("winutil_config", step_catalog.default_winutil_config()),
                "win11debloat_args": str(data.get("win11debloat_args", step_catalog.default_win11debloat_args_text())),
                "registry_changes": data.get("registry_changes", install_plan.default_registry_changes()),
                "applied_background_path": str(data.get("applied_background_path", "")),
            },
        }

    @pyqtSlot(result="QVariantList")
    def getAdvancedArgs(self):
        try:
            data = install_plan.load_install_plan()
            items = [install_plan.normalize_item(item) for item in data.get("items", [])]
        except Exception:
            items = [install_plan.normalize_item(item) for item in install_plan.build_install_plan()["items"]]
        out = []
        known_keys = set(step_catalog.BOOL_OPTION_SLUGS + step_catalog.STEP_SLUGS)
        try:
            data = install_plan.load_install_plan()
        except Exception:
            data = {}
        for it in items:
            label = it["text"]
            if it["key"] in known_keys:
                if it["key"] == "browser-installation":
                    if str(data.get("selected_browser_package", "")).strip():
                        label = step_catalog.browser_step_text(str(data.get("selected_browser_name", "None")))
                    else:
                        label = step_catalog.step_text(it["key"])
                else:
                    label = step_catalog.step_text(it["key"])
            out.append({"key": it["key"], "label": label, "value": bool(it["enabled"])})
        return out

    @pyqtSlot(str)
    def toggleAdvancedArg(self, key: str):
        try:
            data = install_plan.load_install_plan()
            items = [install_plan.normalize_item(item) for item in data.get("items", [])]
            for item in items:
                if item["key"] == key:
                    item["enabled"] = not bool(item["enabled"])
                    break
            data["selected_preset_key"] = "custom"
            if not data.get("selected_browser_package", ""):
                for item in items:
                    if item["key"] == "browser-installation":
                        item["enabled"] = False
                        break
            data["items"] = items
            data["include_browser_install"] = any(
                item["key"] == "browser-installation" and bool(item["enabled"]) for item in items
            )
            install_plan.save_install_plan(data)
        except Exception:
            return

    @pyqtSlot(int)
    def removeInstallPlanItem(self, index: int):
        try:
            data = install_plan.load_install_plan()
            items = [install_plan.normalize_item(item) for item in data.get("items", [])]
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
                data["selected_preset_key"] = "custom"
            data["items"] = items
            data["include_browser_install"] = any(
                item["key"] == "browser-installation" and bool(item["enabled"]) for item in items
            )
            install_plan.save_install_plan(data)
        except Exception:
            return

    @pyqtSlot(str)
    @pyqtSlot(str, str)
    def selectBrowser(self, package_id: str, browser_name: str = "Unknown"):
        install_plan.set_browser(package_id, browser_name)

    @pyqtSlot()
    def skipBrowserInstall(self):
        install_plan.skip_browser_install()

    @pyqtSlot()
    def resetInstallPlanDefaults(self):
        install_plan.reset_install_plan_defaults()

    @pyqtSlot(str)
    def selectPreset(self, preset_key: str):
        try:
            install_plan.apply_preset(preset_key)
        except Exception:
            return

    @pyqtSlot()
    def importInstallPlan(self):
        try:
            path, _ = QFileDialog.getOpenFileName(None, t("configuration.dialogs.import_plan_title"), "", t("configuration.dialogs.json_files_filter"))
            if not path:
                return
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            install_plan.save_install_plan(install_plan.normalize_imported_plan(payload))
        except Exception as e:
            show_error_popup(t("errors.import_plan_failed", {"error": e}), allow_continue=True)

    @pyqtSlot()
    def importWinUtilConfig(self):
        try:
            path, _ = QFileDialog.getOpenFileName(None, t("configuration.dialogs.import_winutil_title"), "", t("configuration.dialogs.json_files_filter"))
            if not path:
                return
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if not isinstance(payload, (dict, list)):
                raise ValueError(t("errors.winutil_config_invalid"))
            data = install_plan.load_install_plan()
            data["winutil_config"] = install_plan.normalize_winutil_config(payload)
            install_plan.save_install_plan(data)
        except Exception as e:
            show_error_popup(t("errors.import_winutil_failed", {"error": e}), allow_continue=True)

    @pyqtSlot()
    def exportInstallPlan(self):
        try:
            data = install_plan.load_install_plan()
            path, _ = QFileDialog.getSaveFileName(None, t("configuration.dialogs.export_plan_title"), "install_plan.json", t("configuration.dialogs.json_files_filter"))
            if not path:
                return
            if not path.lower().endswith(".json"):
                path = f"{path}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            show_error_popup(t("errors.export_plan_failed", {"error": e}), allow_continue=True)

    @pyqtSlot()
    def setAppliedBackground(self):
        try:
            path, _ = QFileDialog.getOpenFileName(
                None,
                t("configuration.dialogs.set_background_title"),
                "",
                t("configuration.dialogs.image_files_filter"),
            )
            if not path:
                return
            if not os.path.isfile(path):
                raise ValueError(t("errors.background_file_missing"))
            data = install_plan.load_install_plan()
            data["applied_background_path"] = os.path.abspath(path)
            install_plan.save_install_plan(data)
        except Exception as e:
            show_error_popup(t("errors.set_background_failed", {"error": e}), allow_continue=True)

    @pyqtSlot()
    def startDebloat(self):
        self.start_requested = True
        app = QApplication.instance()
        if app is not None:
            app.quit()

    @pyqtSlot(result=str)
    def getWin11DebloatArgsText(self):
        try:
            data = install_plan.load_install_plan()
            return install_plan.format_win11debloat_args_for_editor(data.get("win11debloat_args", ""))
        except Exception:
            return ""

    @pyqtSlot(str, result=bool)
    def saveWin11DebloatArgsText(self, text: str):
        try:
            data = install_plan.load_install_plan()
            data["win11debloat_args"] = install_plan.normalize_win11debloat_args_text(text)
            install_plan.save_install_plan(data)
            return True
        except Exception as e:
            show_error_popup(t("errors.save_win11_args_failed", {"error": e}), allow_continue=True)
            return False

    @pyqtSlot(result=str)
    def getRegistryChangesText(self):
        try:
            data = install_plan.load_install_plan()
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
                    raise ValueError(t("errors.registry_changes_invalid"))
            data = install_plan.load_install_plan()
            data["registry_changes"] = parsed
            install_plan.save_install_plan(data)
            return True
        except Exception as e:
            show_error_popup(t("errors.save_registry_changes_failed", {"error": e}), allow_continue=True)
            return False
