import os
import sys
import json
import ssl
import tempfile
import urllib.request
import urllib.parse
from utilities.util_logger import logger
from utilities.util_powershell_handler import run_powershell_command
from utilities.util_error_popup import show_error_popup

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


def _is_url(value: str) -> bool:
    try:
        p = urllib.parse.urlparse(value)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def _download_config(url: str) -> str:
    logger.info(f"Downloading config from: {url}")
    ctx = None
    if url.lower().startswith("https"):
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            ctx = ssl.create_default_context()
    request = urllib.request.Request(url, headers={"User-Agent": "Talon/1.0"})
    with urllib.request.urlopen(request, timeout=30, context=ctx) as resp:
        data = resp.read()
    try:
        json.loads(data.decode("utf-8-sig"))
    except Exception as e:
        raise RuntimeError(f"Downloaded config is not valid JSON: {e}")
    fd, tmp_path = tempfile.mkstemp(prefix="talon_config_", suffix=".json")
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    logger.info(f"Saved downloaded config to: {tmp_path}")
    return tmp_path


def _load_json_config(path: str, label: str):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {label} config: {e}")
        try:
            show_error_popup(
                f"Failed to load {label} config.\n{e}",
                allow_continue=False,
            )
        except Exception:
            pass
        sys.exit(1)


def _write_temp_config(data: dict, prefix: str) -> str:
    fd, tmp_path = tempfile.mkstemp(prefix=prefix, suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logger.info(f"Saved generated config to: {tmp_path}")
    return tmp_path


def _extract_winutil_config(data):
    if not isinstance(data, dict):
        return None
    if "winutil_config" in data:
        value = data.get("winutil_config")
        if isinstance(value, dict) and "payload" in value:
            value = value.get("payload")
        if isinstance(value, dict) and "WinUtil" in value and isinstance(value["WinUtil"], dict):
            return value["WinUtil"]
        if isinstance(value, dict):
            return value
        logger.warning("install_plan winutil_config is not an object; ignoring.")
        return None
    if "WinUtil" in data:
        if isinstance(data["WinUtil"], dict):
            return data["WinUtil"]
        logger.warning("WinUtil config is not an object; ignoring.")
        return None
    if "Win11Debloat" in data:
        winutil_data = {key: value for key, value in data.items() if key != "Win11Debloat"}
        if winutil_data:
            return winutil_data
        return None
    return data


def _extract_win11debloat_args(data):
    if not isinstance(data, dict):
        return None
    if "win11debloat_args" in data:
        value = data.get("win11debloat_args")
        if isinstance(value, str):
            parsed = [part for part in value.split() if part]
            return parsed
        if isinstance(value, list):
            cleaned = [arg for arg in value if isinstance(arg, str)]
            if len(cleaned) != len(value):
                logger.warning("install_plan win11debloat_args contain non-string entries; ignoring invalid entries.")
            return cleaned
        logger.warning("install_plan win11debloat_args are not a string or list; ignoring.")
        return None
    if "Win11Debloat" not in data:
        return None
    win11 = data["Win11Debloat"]
    if isinstance(win11, dict):
        if "Args" in win11:
            args = win11["Args"]
        elif "args" in win11:
            args = win11["args"]
        else:
            return None
    else:
        args = win11
    if isinstance(args, list):
        if not args:
            return []
        cleaned = [arg for arg in args if isinstance(arg, str)]
        if len(cleaned) != len(args):
            logger.warning("Win11Debloat args contain non-string entries; ignoring invalid entries.")
        if cleaned:
            return cleaned
        return None
    if isinstance(args, str):
        return [args]
    logger.warning("Win11Debloat args are not a list or string; ignoring.")
    return None


def _prepare_context(config_path=None):
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        components_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(components_dir)

    if config_path and isinstance(config_path, str) and _is_url(config_path):
        try:
            config_path = _download_config(config_path)
        except Exception as e:
            logger.error(f"Failed to download config: {e}")
            try:
                show_error_popup(
                    f"Failed to download config from URL.\n{e}",
                    allow_continue=False,
                )
            except Exception:
                pass
            sys.exit(1)

    user_config = None
    if config_path:
        if not os.path.exists(config_path):
            logger.error(f"Config not found: {config_path}")
            try:
                show_error_popup(
                    f"Config not found:\n{config_path}",
                    allow_continue=False,
                )
            except Exception:
                pass
            sys.exit(1)
        user_config = _load_json_config(config_path, "custom")
        logger.info(f"Using custom config: {config_path}")
    else:
        logger.info("Using embedded defaults from install_plan/runtime.")

    return base_path, user_config


def run_winutil(config_path=None):
    base_path, user_config = _prepare_context(config_path)

    winutil_config = None
    if user_config is not None:
        winutil_config = _extract_winutil_config(user_config)
        if winutil_config is None:
            logger.info("Custom config has no WinUtil config; using embedded default WinUtil config.")
    if winutil_config is None:
        winutil_config = _DEFAULT_WINUTIL_CONFIG

    winutil_config_path = _write_temp_config(winutil_config, "talon_winutil_")
    logger.info(f"Using WinUtil config: {winutil_config_path}")
    winutil_path = os.path.join(base_path, "external_scripts", "winutil.ps1")
    if not os.path.exists(winutil_path):
        logger.error(f"Bundled WinUtil script not found: {winutil_path}")
        try:
            show_error_popup(
                f"Bundled WinUtil script not found:\n{winutil_path}",
                allow_continue=False,
            )
        except Exception:
            pass
        sys.exit(1)

    cmd = f"& '{winutil_path}' -Config '{winutil_config_path}' -Run -NoUI"
    logger.info("Executing ChrisTitusTech WinUtil")
    try:
        run_powershell_command(
            cmd,
            monitor_output=True,
            termination_str="Tweaks are Finished",
        )
        logger.info("Successfully executed ChrisTitusTech WinUtil")
    except Exception as e:
        logger.error(f"Failed to execute ChrisTitusTech WinUtil: {e}")
        try:
            show_error_popup(
                f"Failed to execute ChrisTitusTech WinUtil:\n{e}",
                allow_continue=False,
            )
        except Exception:
            pass
        sys.exit(1)


def run_win11debloat(config_path=None):
    base_path, user_config = _prepare_context(config_path)

    win11debloat_args = None
    if user_config is not None:
        win11debloat_args = _extract_win11debloat_args(user_config)
        if win11debloat_args is None:
            logger.info("Custom config has no Win11Debloat args; using embedded default Win11Debloat args.")
    if win11debloat_args is None:
        win11debloat_args = list(_DEFAULT_WIN11DEBLOAT_ARGS)

    win11debloat_path = os.path.join(
        base_path, "external_scripts", "Raphire-Win11Debloat-c523386", "Win11Debloat.ps1"
    )
    if not os.path.exists(win11debloat_path):
        logger.error(f"Bundled Win11Debloat script not found: {win11debloat_path}")
        try:
            show_error_popup(
                f"Bundled Win11Debloat script not found:\n{win11debloat_path}",
                allow_continue=False,
            )
        except Exception:
            pass
        sys.exit(1)

    cmd = f"& '{win11debloat_path}'"
    if win11debloat_args:
        cmd = f"{cmd} {' '.join(win11debloat_args)}"

    logger.info("Executing Raphi Win11Debloat")
    try:
        run_powershell_command(cmd)
        logger.info("Successfully executed Raphi Win11Debloat")
    except Exception as e:
        logger.error(f"Failed to execute Raphi Win11Debloat: {e}")
        try:
            show_error_popup(
                f"Failed to execute Raphi Win11Debloat:\n{e}",
                allow_continue=False,
            )
        except Exception:
            pass
        sys.exit(1)


def main(config_path=None):
    run_winutil(config_path)
    run_win11debloat(config_path)
    logger.info("All external debloat scripts executed successfully.")


if __name__ == "__main__":
    main()
