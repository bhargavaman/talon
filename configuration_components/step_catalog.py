import copy


BROWSER_OPTIONS = [
    {
        "name": "Edge",
        "icon": "../../media/browser_edge.png",
        "packageId": "microsoft-edge",
        "tooltip": (
            "Edge is not recommended unless necessary for your purposes, as it is very "
            "invasive to your privacy and embeds ads."
        ),
    },
    {
        "name": "Waterfox",
        "icon": "../../media/browser_waterfox.png",
        "packageId": "waterfox",
        "tooltip": (
            "Waterfox is recommended over Firefox, but not Brave. It's based on Firefox, "
            "but removes tracking and telemetry."
        ),
    },
    {
        "name": "Brave",
        "icon": "../../media/browser_brave.png",
        "packageId": "brave",
        "tooltip": "Brave is the recommended browser, as it is the closest to Chrome while respecting your privacy.",
    },
    {
        "name": "LibreWolf",
        "icon": "../../media/browser_librewolf.png",
        "packageId": "librewolf",
        "tooltip": (
            "LibreWolf is only recommended for tech-savvy users. It is designed for "
            "maximum privacy and security, but can be harder to use."
        ),
    },
    {
        "name": "Firefox",
        "icon": "../../media/browser_firefox.png",
        "packageId": "firefox",
        "tooltip": (
            "Firefox is not recommended unless necessary for your purposes, as it includes "
            "telemetry and sponsored content by default."
        ),
    },
]

BROWSER_TOOLTIPS = {browser["packageId"]: browser["tooltip"] for browser in BROWSER_OPTIONS}

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

STEP_PRESENTATION = {
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
            'receiving security updates, leaving out non-security "feature" updates. It '
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
    "developer-mode": {
        "text": "Developer mode (hide installation overlay)",
        "tooltip": "When enabled, Talon runs without showing the full-screen install overlay.",
    },
}

DEFAULT_WINUTIL_CONFIG = {
    "WPFTweaks": [
        "WPFTweaksActivity",
        "WPFTweaksConsumerFeatures",
        "WPFTweaksDisableBGapps",
        "WPFTweaksLocation",
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
        "WPFTweaksRemoveGallery",
        "WPFTweaksDeBloat",
        "WPFTweaksRemoveCopilot",
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


def default_winutil_config():
    return copy.deepcopy(DEFAULT_WINUTIL_CONFIG)


def default_winutil_tweaks():
    return list(DEFAULT_WINUTIL_CONFIG["WPFTweaks"])


def default_win11debloat_args():
    return list(DEFAULT_WIN11DEBLOAT_ARGS)


def default_win11debloat_args_text() -> str:
    return " ".join(DEFAULT_WIN11DEBLOAT_ARGS)


def browser_tooltip(package_id: str) -> str:
    return BROWSER_TOOLTIPS.get(package_id, "No browser selected yet.")


def browser_step_text(browser_name: str) -> str:
    return f"Install web browser: {browser_name}"


def to_title_label(key: str) -> str:
    parts = str(key).replace("-", " ").split()
    return " ".join(p[:1].upper() + p[1:] for p in parts)
