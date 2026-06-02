import copy
import json
import os
import sys

from configuration_components.localization import t


def _slug_key(slug: str) -> str:
    return str(slug).replace("-", "_")


BROWSER_OPTIONS = [
    {
        "name": "Edge",
        "icon": "../../media/browser_edge.png",
        "packageId": "microsoft-edge",
        "tooltipKey": "browsers.edge.tooltip",
    },
    {
        "name": "Waterfox",
        "icon": "../../media/browser_waterfox.png",
        "packageId": "waterfox",
        "tooltipKey": "browsers.waterfox.tooltip",
    },
    {
        "name": "Brave",
        "icon": "../../media/browser_brave.png",
        "packageId": "brave",
        "tooltipKey": "browsers.brave.tooltip",
    },
    {
        "name": "LibreWolf",
        "icon": "../../media/browser_librewolf.png",
        "packageId": "librewolf",
        "tooltipKey": "browsers.librewolf.tooltip",
    },
    {
        "name": "Firefox",
        "icon": "../../media/browser_firefox.png",
        "packageId": "firefox",
        "tooltipKey": "browsers.firefox.tooltip",
    },
]

BROWSER_TOOLTIP_KEYS = {browser["packageId"]: browser["tooltipKey"] for browser in BROWSER_OPTIONS}

STEP_SLUGS = [
    "remove-edge-permanently",
    "uninstall-outlook-onedrive",
    "browser-installation",
    "debloat-windows-phase-one",
    "debloat-windows-phase-two",
    "registry-tweaks",
    "configure-updates",
    "apply-background",
]

BOOL_OPTION_SLUGS = ["developer-mode"]
STANDARD_PRESET_KEY = "standard"

STEP_PRESENTATION = {
    "remove-edge-permanently": {
        "textKey": "steps.remove_edge_permanently.text",
        "tooltipKey": "steps.remove_edge_permanently.tooltip",
    },
    "uninstall-outlook-onedrive": {
        "textKey": "steps.uninstall_outlook_onedrive.text",
        "tooltipKey": "steps.uninstall_outlook_onedrive.tooltip",
    },
    "browser-installation": {
        "textKey": "steps.browser_installation.text",
        "tooltipKey": "steps.browser_installation.tooltip",
    },
    "debloat-windows-phase-one": {
        "textKey": "steps.debloat_windows_phase_one.text",
        "tooltipKey": "steps.debloat_windows_phase_one.tooltip",
    },
    "debloat-windows-phase-two": {
        "textKey": "steps.debloat_windows_phase_two.text",
        "tooltipKey": "steps.debloat_windows_phase_two.tooltip",
    },
    "registry-tweaks": {
        "textKey": "steps.registry_tweaks.text",
        "tooltipKey": "steps.registry_tweaks.tooltip",
    },
    "configure-updates": {
        "textKey": "steps.configure_updates.text",
        "tooltipKey": "steps.configure_updates.tooltip",
    },
    "apply-background": {
        "textKey": "steps.apply_background.text",
        "tooltipKey": "steps.apply_background.tooltip",
    },
    "developer-mode": {
        "textKey": "steps.developer_mode.text",
        "tooltipKey": "steps.developer_mode.tooltip",
    },
}

DEFAULT_WINUTIL_CONFIG = {
    "WPFTweaks": [
        "WPFTweaksActivity",
        "WPFTweaksConsumerFeatures",
        "WPFTweaksDisableBGapps",
        "WPFTweaksTelemetry",
        "WPFTweaksWPBT",
        "WPFTweaksWidget",
        "WPFTweaksServices",
        "WPFTweaksDisableExplorerAutoDiscovery",
        "WPFTweaksDisplay",
        "WPFTweaksRightClickMenu",
        "WPFTweaksRevertStartMenu",
        "WPFTweaksRemoveOneDrive",
        "WPFTweaksXboxRemoval",
        "WPFTweaksRemoveHome",
        "WPFTweaksDeBloat",
        "WPFTweaksWindowsAI",
        "WPFTweaksDisableStoreSearch",
    ]
}

DEFAULT_WIN11DEBLOAT_ARGS = [
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
    "-DisableEdgeAI",
    "-DisableStickyKeys",
    "-DisableEdgeAds",
    "-DisableBraveBloat",
    "-DisableRecall",
    "-DisableAISvcAutoStart",
    "-DisableClickToDo",
    "-DisableSnapLayouts",
    "-DisableSearchHistory",
    "-DisableDeliveryOptimization",
]

_STANDARD_PRESET_FALLBACK = {
    "preset_key": STANDARD_PRESET_KEY,
    "preset_name": "Standard",
    "version": 1,
    "selected_preset_key": STANDARD_PRESET_KEY,
    "selected_browser_name": "None",
    "selected_browser_package": "",
    "include_browser_install": False,
    "items": [{"key": slug, "enabled": False if slug in BOOL_OPTION_SLUGS else True} for slug in BOOL_OPTION_SLUGS + STEP_SLUGS],
    "winutil_config": copy.deepcopy(DEFAULT_WINUTIL_CONFIG),
    "win11debloat_args": " ".join(DEFAULT_WIN11DEBLOAT_ARGS),
    "registry_changes": None,
    "applied_background_path": "",
}


def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _candidate_preset_dirs():
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(os.path.join(os.path.dirname(sys.executable), "presets"))
    candidates.append(os.path.join(_repo_root(), "presets"))
    candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "presets"))
    return [os.path.abspath(path) for path in candidates]


def presets_dir() -> str:
    for path in _candidate_preset_dirs():
        if os.path.isdir(path):
            return path
    return _candidate_preset_dirs()[0]


def _normalize_preset(raw, fallback_key: str) -> dict:
    if not isinstance(raw, dict):
        return {}
    key = str(raw.get("preset_key", raw.get("selected_preset_key", fallback_key))).strip() or fallback_key
    name = str(raw.get("preset_name", raw.get("name", to_title_label(key)))).strip() or to_title_label(key)
    plan = copy.deepcopy(raw)
    plan["selected_preset_key"] = key
    plan.pop("preset_key", None)
    plan.pop("preset_name", None)
    plan.pop("name", None)
    if not isinstance(plan.get("version"), int):
        return {}
    if not isinstance(plan.get("items"), list):
        return {}
    return {
        "key": key,
        "name": name,
        "plan": plan,
    }


def _load_preset_file(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return _normalize_preset(json.load(f), os.path.splitext(os.path.basename(path))[0])
    except Exception:
        return {}


def available_presets() -> list:
    presets = []
    root = presets_dir()
    if os.path.isdir(root):
        names = sorted(os.listdir(root), key=lambda name: (name != f"{STANDARD_PRESET_KEY}.json", name.lower()))
        for name in names:
            if not name.endswith(".json"):
                continue
            preset = _load_preset_file(os.path.join(root, name))
            if preset:
                presets.append(preset)
    if not any(preset["key"] == STANDARD_PRESET_KEY for preset in presets):
        presets.insert(0, _normalize_preset(_STANDARD_PRESET_FALLBACK, STANDARD_PRESET_KEY))
    return presets


def preset_options() -> list:
    return [{"key": preset["key"], "name": preset["name"]} for preset in available_presets()]


def preset_by_key(key: str) -> dict:
    wanted = str(key or STANDARD_PRESET_KEY).strip()
    for preset in available_presets():
        if preset["key"] == wanted:
            return copy.deepcopy(preset)
    return _normalize_preset(_STANDARD_PRESET_FALLBACK, STANDARD_PRESET_KEY)


def default_winutil_config():
    return copy.deepcopy(DEFAULT_WINUTIL_CONFIG)


def default_winutil_tweaks():
    return list(DEFAULT_WINUTIL_CONFIG["WPFTweaks"])


def default_win11debloat_args():
    return list(DEFAULT_WIN11DEBLOAT_ARGS)


def default_win11debloat_args_text() -> str:
    return " ".join(DEFAULT_WIN11DEBLOAT_ARGS)


def browser_tooltip(package_id: str) -> str:
    return t(BROWSER_TOOLTIP_KEYS.get(package_id, "steps.browser_installation.tooltip"))


def browser_step_text(browser_name: str) -> str:
    return t("steps.browser_installation.text_with_browser", {"browser_name": browser_name})


def browser_options():
    out = []
    for browser in BROWSER_OPTIONS:
        item = dict(browser)
        item["tooltip"] = t(item.pop("tooltipKey"))
        out.append(item)
    return out


def step_text(slug: str) -> str:
    present = STEP_PRESENTATION.get(slug, {})
    key = present.get("textKey", f"steps.{_slug_key(slug)}.text")
    value = t(key)
    return to_title_label(slug) if value == key else value


def step_tooltip(slug: str) -> str:
    present = STEP_PRESENTATION.get(slug, {})
    key = present.get("tooltipKey", f"steps.{_slug_key(slug)}.tooltip")
    value = t(key)
    return "" if value == key else value


def to_title_label(key: str) -> str:
    parts = str(key).replace("-", " ").split()
    return " ".join(p[:1].upper() + p[1:] for p in parts)
