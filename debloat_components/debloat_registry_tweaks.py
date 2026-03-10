import sys
import winreg
from utilities.util_logger import logger
from utilities.util_error_popup import show_error_popup
from utilities.util_modify_registry import set_value


REGISTRY_MODIFICATIONS = [
    (winreg.HKEY_CURRENT_USER,
     r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
     "TaskbarAl", winreg.REG_DWORD, 0),
    (winreg.HKEY_CURRENT_USER,
     r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
     "AppsUseLightTheme", winreg.REG_DWORD, 0),
    (winreg.HKEY_CURRENT_USER,
     r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
     "SystemUsesLightTheme", winreg.REG_DWORD, 0),
    (winreg.HKEY_CURRENT_USER,
     r"Software\Microsoft\Windows\CurrentVersion\GameDVR",
     "AppCaptureEnabled", winreg.REG_DWORD, 0),
    (winreg.HKEY_LOCAL_MACHINE,
     r"SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR",
     "Value", winreg.REG_DWORD, 0),
    (winreg.HKEY_CURRENT_USER,
     r"Control Panel\Desktop",
     "MenuShowDelay", winreg.REG_SZ, "0"),
    (winreg.HKEY_CURRENT_USER,
     r"Control Panel\Desktop\WindowMetrics",
     "MinAnimate", winreg.REG_DWORD, 0),
    (winreg.HKEY_CURRENT_USER,
     r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
     "ExtendedUIHoverTime", winreg.REG_DWORD, 1),
    (winreg.HKEY_CURRENT_USER,
     r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
     "HideFileExt", winreg.REG_DWORD, 0),
    (winreg.HKEY_CURRENT_USER,
     r"Control Panel\Desktop",
     "DragFullWindows", winreg.REG_SZ, "1"),
]


def default_registry_changes_payload():
    hive_names = {
        winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER",
        winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
    }
    type_names = {
        winreg.REG_DWORD: "REG_DWORD",
        winreg.REG_SZ: "REG_SZ",
    }
    rows = []
    for hive, key_path, name, value_type, value in REGISTRY_MODIFICATIONS:
        rows.append(
            {
                "hive": hive_names.get(hive, str(hive)),
                "key_path": key_path,
                "name": name,
                "value_type": type_names.get(value_type, str(value_type)),
                "value": value,
            }
        )
    return rows


def _parse_hive(value):
    hive_names = {
        "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
        "HKCU": winreg.HKEY_CURRENT_USER,
        "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
        "HKLM": winreg.HKEY_LOCAL_MACHINE,
    }
    if isinstance(value, int):
        return value
    text = str(value).strip().upper()
    return hive_names.get(text)


def _parse_value_type(value):
    type_names = {
        "REG_DWORD": winreg.REG_DWORD,
        "DWORD": winreg.REG_DWORD,
        "REG_SZ": winreg.REG_SZ,
        "SZ": winreg.REG_SZ,
    }
    if isinstance(value, int):
        return value
    text = str(value).strip().upper()
    return type_names.get(text)


def _coerce_registry_modifications(registry_changes):
    if registry_changes is None:
        return list(REGISTRY_MODIFICATIONS)
    if isinstance(registry_changes, dict):
        if isinstance(registry_changes.get("modifications"), list):
            rows = registry_changes.get("modifications")
        elif isinstance(registry_changes.get("items"), list):
            rows = registry_changes.get("items")
        else:
            raise ValueError("registry_changes must contain a list in 'modifications' or 'items'.")
    elif isinstance(registry_changes, list):
        rows = registry_changes
    else:
        raise ValueError("registry_changes must be a list or object.")
    if not rows:
        raise ValueError("registry_changes is empty.")
    out = []
    for idx, raw in enumerate(rows):
        if not isinstance(raw, dict):
            raise ValueError(f"registry_changes[{idx}] must be an object.")
        hive = _parse_hive(raw.get("hive"))
        key_path = str(raw.get("key_path", "")).strip()
        name = str(raw.get("name", "")).strip()
        value_type = _parse_value_type(raw.get("value_type"))
        value = raw.get("value")
        if hive is None or not key_path or not name or value_type is None:
            raise ValueError(
                f"registry_changes[{idx}] must include valid hive, key_path, name, and value_type."
            )
        out.append((hive, key_path, name, value_type, value))
    return out



def main(registry_changes=None):
    try:
        modifications = _coerce_registry_modifications(registry_changes)
    except Exception as e:
        logger.error(f"Invalid registry changes payload: {e}")
        try:
            show_error_popup(
                f"Invalid registry changes payload.\n\n{e}",
                allow_continue=False
            )
        except Exception:
            pass
        sys.exit(1)
    for hive, key_path, name, value_type, value in modifications:
        try:
            logger.info(f"Applying registry tweak: {key_path}\\{name} = {value!r} (type={value_type})")
            set_value(hive, key_path, name, value, value_type)
            logger.info(f"Successfully set {name}")
        except Exception as e:
            logger.error(f"Failed to apply registry tweak {name}: {e}")
            try:
                show_error_popup(
                    f"Failed to apply registry tweak:\n{key_path}\\{name}\n\n{e}",
                    allow_continue=False
                )
            except Exception:
                pass
            sys.exit(1)

    logger.info("All registry tweaks applied successfully.")



if __name__ == "__main__":
    main()
