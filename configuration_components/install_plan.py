import json
import os
import re
import tempfile

import debloat_components.debloat_registry_tweaks as debloat_registry_tweaks
from configuration_components import step_catalog


INSTALL_PLAN_VERSION = 1


def talon_dir() -> str:
    return os.path.join(os.environ.get("TEMP", tempfile.gettempdir()), "talon")


def install_plan_path() -> str:
    return os.path.join(talon_dir(), "install_plan.json")


def metadata_keys() -> tuple:
    return ("winutil_config", "win11debloat_args", "registry_changes", "applied_background_path")


def default_registry_changes():
    try:
        return debloat_registry_tweaks.default_registry_changes_payload()
    except Exception:
        return []


def normalize_win11debloat_args_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip())


def format_win11debloat_args_for_editor(value) -> str:
    if isinstance(value, list):
        cleaned = [str(v).strip() for v in value if str(v).strip()]
        return "\n".join(cleaned)
    compact = re.sub(r"\s+", " ", str(value).strip())
    if not compact:
        return ""
    return "\n".join([part for part in compact.split(" ") if part])


def normalize_winutil_config(value):
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
    return step_catalog.default_winutil_config()


def normalize_registry_changes(value):
    if value is None:
        return default_registry_changes()
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return default_registry_changes()
        try:
            value = json.loads(stripped)
        except Exception:
            return default_registry_changes()
    if isinstance(value, (dict, list)):
        return value
    return default_registry_changes()


def normalize_metadata_fields(data: dict):
    if not isinstance(data, dict):
        return
    data["winutil_config"] = normalize_winutil_config(data.get("winutil_config"))
    args_raw = data.get("win11debloat_args", step_catalog.default_win11debloat_args_text())
    if isinstance(args_raw, list):
        args_raw = " ".join([str(v).strip() for v in args_raw if str(v).strip()])
    data["win11debloat_args"] = normalize_win11debloat_args_text(
        args_raw if str(args_raw).strip() else step_catalog.default_win11debloat_args_text()
    )
    data["registry_changes"] = normalize_registry_changes(data.get("registry_changes"))
    data["applied_background_path"] = str(data.get("applied_background_path", "")).strip()


def build_install_plan(browser_name: str = "None", browser_package: str = "", include_browser_install: bool = False) -> dict:
    items = []
    for slug in step_catalog.BOOL_OPTION_SLUGS + step_catalog.STEP_SLUGS:
        present = step_catalog.STEP_PRESENTATION.get(slug, {})
        item = {
            "key": slug,
            "text": str(present.get("text", step_catalog.to_title_label(slug))),
            "tooltip": str(present.get("tooltip", "")),
            "enabled": False if slug in step_catalog.BOOL_OPTION_SLUGS else True,
        }
        if slug == "browser-installation":
            item["text"] = step_catalog.browser_step_text(browser_name)
            item["tooltip"] = step_catalog.browser_tooltip(browser_package)
            item["enabled"] = bool(include_browser_install)
        items.append(item)
    return {
        "version": INSTALL_PLAN_VERSION,
        "selected_browser_name": browser_name,
        "selected_browser_package": browser_package,
        "include_browser_install": include_browser_install,
        "items": items,
        "winutil_config": step_catalog.default_winutil_config(),
        "win11debloat_args": step_catalog.default_win11debloat_args_text(),
        "registry_changes": default_registry_changes(),
        "applied_background_path": "",
    }


def normalize_item(item) -> dict:
    if isinstance(item, dict):
        return {
            "key": str(item.get("key", "")),
            "text": str(item.get("text", "")),
            "tooltip": str(item.get("tooltip", "")),
            "enabled": bool(item.get("enabled", False)),
        }
    return {"key": "", "text": str(item), "tooltip": "", "enabled": False}


def normalize_imported_plan(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Install plan must be a JSON object.")
    incoming_version = payload.get("version", INSTALL_PLAN_VERSION)
    if not isinstance(incoming_version, int):
        raise ValueError("Install plan field 'version' must be an integer.")
    if incoming_version < 1:
        raise ValueError("Install plan field 'version' must be >= 1.")
    if "items" not in payload:
        raise ValueError("Install plan is missing required field: items.")
    if not isinstance(payload.get("items"), list):
        raise ValueError("Install plan field 'items' must be a list.")

    normalized = build_install_plan(
        browser_name=str(payload.get("selected_browser_name", "None")),
        browser_package=str(payload.get("selected_browser_package", "")),
        include_browser_install=bool(payload.get("include_browser_install", False)),
    )
    normalized["version"] = incoming_version
    default_keys = {item["key"] for item in normalized["items"]}
    imported_by_key = {}
    unknown_items = []
    for raw in payload.get("items", []):
        n = normalize_item(raw)
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
        set_item_enabled(normalized, "browser-installation", False)
    normalized["include_browser_install"] = is_item_enabled(normalized, "browser-installation")
    for key in metadata_keys():
        if key in payload:
            normalized[key] = payload.get(key)
    normalize_metadata_fields(normalized)
    return normalized


def ensure_install_plan_file():
    os.makedirs(talon_dir(), exist_ok=True)
    path = install_plan_path()
    if not os.path.isfile(path):
        save_install_plan(build_install_plan())
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("plan root must be an object")
        items = data.get("items", [])
        if not isinstance(items, list):
            raise ValueError("install plan items is not a list")
        normalized = build_install_plan(
            browser_name=str(data.get("selected_browser_name", "None")),
            browser_package=str(data.get("selected_browser_package", "")),
            include_browser_install=bool(data.get("include_browser_install", False)),
        )
        existing_version = data.get("version", INSTALL_PLAN_VERSION)
        normalized["version"] = existing_version if isinstance(existing_version, int) and existing_version >= 1 else INSTALL_PLAN_VERSION
        existing_enabled_by_key = {}
        for raw in items:
            n = normalize_item(raw)
            if n["key"]:
                existing_enabled_by_key[n["key"]] = bool(n["enabled"])
        for item in normalized["items"]:
            if item["key"] in existing_enabled_by_key:
                item["enabled"] = existing_enabled_by_key[item["key"]]
        if not normalized["selected_browser_package"]:
            set_item_enabled(normalized, "browser-installation", False)
        normalized["include_browser_install"] = is_item_enabled(normalized, "browser-installation")
        for key in metadata_keys():
            if key in data:
                normalized[key] = data.get(key)
        normalize_metadata_fields(normalized)
        save_install_plan(normalized)
    except Exception:
        save_install_plan(build_install_plan())


def reset_install_plan_defaults():
    os.makedirs(talon_dir(), exist_ok=True)
    save_install_plan(build_install_plan())


def load_install_plan() -> dict:
    ensure_install_plan_file()
    try:
        with open(install_plan_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("plan root must be an object")
        if not isinstance(data.get("items", []), list):
            data["items"] = []
        original = json.dumps(data, sort_keys=True)
        normalize_metadata_fields(data)
        if json.dumps(data, sort_keys=True) != original:
            save_install_plan(data)
        return data
    except Exception:
        return build_install_plan()


def save_install_plan(data: dict):
    os.makedirs(talon_dir(), exist_ok=True)
    with open(install_plan_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def find_item_index(items: list, key: str) -> int:
    for i, item in enumerate(items):
        if normalize_item(item)["key"] == key:
            return i
    return -1


def set_item_enabled(data: dict, key: str, enabled: bool):
    items = [normalize_item(item) for item in data.get("items", [])]
    for item in items:
        if item["key"] == key:
            item["enabled"] = bool(enabled)
            break
    data["items"] = items


def is_item_enabled(data: dict, key: str) -> bool:
    for item in data.get("items", []):
        n = normalize_item(item)
        if n["key"] == key:
            return bool(n["enabled"])
    return False


def enabled_plan_keys(data: dict) -> list:
    keys = []
    selected_browser = str(data.get("selected_browser_package", "")).strip()
    for item in data.get("items", []):
        n = normalize_item(item)
        if not n["key"] or not n["enabled"]:
            continue
        if n["key"] == "browser-installation" and not selected_browser:
            continue
        keys.append(n["key"])
    return keys


def visible_enabled_items(data: dict) -> list:
    out = []
    for item in data.get("items", []):
        n = normalize_item(item)
        if not n["enabled"]:
            continue
        if n["key"] == "browser-installation" and not data.get("selected_browser_package", ""):
            continue
        out.append({"key": n["key"], "text": n["text"], "tooltip": n["tooltip"]})
    return out


def set_browser(package_id: str, browser_name: str):
    data = load_install_plan()
    items = [normalize_item(item) for item in data.get("items", [])]
    idx = find_item_index(items, "browser-installation")
    if idx >= 0:
        items[idx]["text"] = step_catalog.browser_step_text(browser_name)
        items[idx]["tooltip"] = step_catalog.browser_tooltip(package_id)
        items[idx]["enabled"] = True
    data["items"] = items
    data["selected_browser_name"] = browser_name
    data["selected_browser_package"] = package_id
    data["include_browser_install"] = True
    save_install_plan(data)


def skip_browser_install():
    data = load_install_plan()
    set_item_enabled(data, "browser-installation", False)
    data["selected_browser_name"] = "None"
    data["selected_browser_package"] = ""
    data["include_browser_install"] = False
    save_install_plan(data)


def apply_internet_availability(available: bool):
    if available:
        return
    data = load_install_plan()
    set_item_enabled(data, "browser-installation", False)
    data["include_browser_install"] = False
    save_install_plan(data)

