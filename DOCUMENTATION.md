
# Talon Documentation
This documentation aims to explain exactly what Talon and Talon Lite do, and how, for both non-tech savvy users and tech savvy users to understand the utility.

Talon is our flagship software utility which makes the process of 'debloating' Windows as easy as 2 clicks on new, freshly installed Windows 11 Home or Professional systems only. Completely disables and removes AI, spying and telemetry, disables pointless processes running in the background and other useless Microsoft nonsense, and optimizes your system for better performance. Talon Lite is a variant which works on Windows 10, already in-use systems, or versions of Windows 11 that are not Home or Professional by skipping some changes made by the full version of Talon that are tailored for Windows 11 Home and Professional.

## Table of Contents

- [For Non-Tech Savvy Users](#for-non-tech-savvy-users)
- [For Tech-Savvy Users](#for-tech-savvy-users)
    - [Talon Command Line Arguments](#talon-command-line-arguments)
    - [Step 1: Execute Raven Scripts](#step-1-execute-raven-scripts)
    - [Step 2: Browser Installation](#step-2-browser-installation)
    - [Step 3: Execute External Scripts](#step-3-execute-external-scripts)
    - [Step 4: Registry Tweaks](#step-4-registry-tweaks)
    - [Step 5: Configure Updates](#step-5-configure-updates)
    - [Step 6: Apply Background](#step-6-apply-background)
    - [Apps Removed by Win11Debloat](#apps-removed-by-win11debloat)
- [Talon Development](#talon-development)
- [Talon FAQ](#talon-faq)
- [Documentation Credits](#credits)


# For Non-Tech Savvy Users

Talon can be used on "fresh" installs of Windows 11 Home or Professional. A fresh installation of Windows is one which is not tampered with beyond the standard de facto setup. This guarantees a consistent and stable environment for Talon to operate. Installing programs, changing settings, etc., can result in unexpected behavior during Talon's installation.

This is not the case for Talon Lite, which is designed and tested to work on already in-use systems, on Windows 10 or 11, and any version of them (Education, Enterprise, LTSC, etc.).

If you run into any problems or have any questions that aren't covered in this documentation, feel free to [contact us](https://ravendevteam.org/contact/). We're happy to help.



| De-bloat step                                                           | Talon | Talon Lite |
|-------------------------------------------------------------------------|:-----:|:----------:|
| Uninstall Microsoft Edge                                                |   X   |     X      |
| Uninstall Outlook and OneDrive                                          |   X   |            |
| Install your browser of choice                                          |   X   |            |
| Adjust system appearance to be more performant                          |   X   |     X      |
| Remove all Microsoft Store apps                                         |   X   |            |
| Set many background services to only run when needed                    |   X   |     X      |
| Stop Windows from auto-installing apps or games without your permission |   X   |     X      |
| Remove Copilot and Recall                                               |   X   |     X      |
| Disable telemetry                                                       |   X   |     X      |
| Disable background apps from MS Store                                   |   X   |     X      |
| Remove Home from file explorer and set 'This PC' as default             |   X   |     X      |
| Remove Gallery from file explorer                                       |   X   |            |
| Bring back the Windows 10 right-click menu                              |   X   |            |
| Disable location tracking                                               |   X   |     X      |
| Disables vendor startup scripts                                         |   X   |            |
| Disable GameDVR                                                         |   X   |            |
| Disable Explorer Automatic Folder Discovery                             |   X   |            |
| Removes apps listed [here](#apps-removed-by-win11debloat)               |   X   |     X      |
| Disable activity history and targeted ads                               |   X   |     X      |
| Disable Bing, Bing AI, and Cortana                                      |   X   |     X      |
| Disable Tips, Tricks, and Suggestions                                   |   X   |     X      |
| Align taskbar icons to the left (Windows 11 only)                       |   X   |            |
| Hide search icon from taskbar (Windows 11 only)                         |   X   |            |
| Disable widgets on taskbar and lock screen                              |   X   |     X      |
| Remove all pinned apps from the start menu                              |   X   |            |
| Disable Xbox screen recording                                           |   X   |            |
| Disable recommended section in the start menu (Windows 11 only)         |   X   |     X      |
| Turn off mouse acceleration                                             |   X   |     X      |
| Disable Windows Spotlight desktop background option                     |   X   |            |
| Disable Microsoft 365 ads in Settings Home (Windows 11 only)            |   X   |            |
| Hide the Settings Home page (Windows 11 only)                           |   X   |            |
| Disable AI features in Paint (Windows 11 only)                          |   X   |            |
| Disable AI features in Notepad (Windows 11 only)                        |   X   |            |
| Disable Sticky Keys (Windows 11 only)                                   |   X   |            |
| Left-align taskbar                                                      |   X   |            |
| Disable Xbox Game Bar                                                   |   X   |            |
| Enable dark mode                                                        |   X   |            |
| Enable file extensions in Explorer                                      |   X   |     X      |
| Disable non-security updates                                            |   X   |     X      |
| Apply Talon desktop background                                          |   X   |            |

# For Tech Savvy Users

This section delves further in-depth into how Talon / Talon Lite work and what exactly they do.

### Talon Command Line Arguments

| Argument                          | Talon | Talon Lite | Description |
|-----------------------------------|:-----:|:----------:|-------------|
| `--skip-execute-raven-scripts`    |   X   |     X      | Skips the Execute Raven Scripts step. |
| `--skip-browser-installation`     |   X   |     X      | Skips the Browser Installation step. |
| `--skip-execute-external-scripts` |   X   |     X      | Skips the Execute External Scripts step. |
| `--skip-registry-tweaks`          |   X   |     X      | Skips the Registry Tweaks step. |
| `--skip-configure-updates`        |   X   |     X      | Skips the Configure Updates step. |
| `--skip-apply-background`         |   X   |     X      | Skips the Apply Background step. |
| `--developer-mode`                |   X   |     X      | Run without the installing overlay. |
| `--headless`                      |   X   |            | Run unattended (no UI, no prompts, skip browser install, runs offline, no restart). |
| `--config [path\|url]`            |   X   |            | Pass a custom config file to use instead of the default Talon configuration. If you pass a URL, an internet connection will be required. |


### Step 1: Execute Raven Scripts
Can be skipped with the `--skip-execute-raven-scripts-step` flag.  

| Script | Talon | Talon Lite |
|--------|:-----:|:----------:|
| edge_vanisher.ps1 ([source code](https://github.com/ravendevteam/talon/blob/main/debloat_raven_scripts/edge_vanisher.ps1))     |   X   |     X      |
| uninstall_oo.ps1 ([source code](https://github.com/ravendevteam/talon/blob/main/debloat_raven_scripts/uninstall_oo.ps1))      |   X   |            |

edge_vanisher.ps1
-----------------
| De-bloat step                                       | Details                                |
|-----------------------------------------------------|----------------------------------------|
| Remove folders and shortcuts used by Microsoft Edge | Removes:<ul><li>`%LOCALAPPDATA%\Microsoft\Edge`</li><li>`%ProgramFiles(x86)%\Microsoft\Edge`</li><li>`%ProgramFiles(x86)%\Microsoft\EdgeCore`</li><li>`%ProgramData%\Microsoft\Windows\Start Menu\Programs\Microsoft Edge.lnk`</li><li>`%PUBLIC%\Desktop\Microsoft Edge.lnk`</li></ul> |
| Remove registry entries                             | Removes:<ul><li>`HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe`</li><li>`HKLM:\SOFTWARE\Microsoft\Edge`</li><li>`HKLM:\SOFTWARE\WOW6432Node\Microsoft\Edge`</li><li>`HKCU:\Software\Microsoft\Edge`</li></ul> |
| Creates Dummy folders | Re-creates these folders with ownership to prevent Windows from using them:<ul><li>`%ProgramFiles(x86)%\Microsoft\Edge`</li><li>`%ProgramFiles(x86)%\Microsoft\Edge\Application`</li></ul> |

uninstall_oo.ps1  (Talon only)
----------------
| **Outlook** | De-bloat step  | Details                                |
|-------------|----------------|----------------------------------------|
|| Remove Outlook apps         | Removes packages that match the patterns:<ul><li>`*Microsoft.Office.Outlook*`</li><li>`*Microsoft.OutlookForWindows*`</li></ul>                        |
|| Remove Outlook folders      | Removes folders in `C:\Program Files\WindowsApps\` that match the pattern `Microsoft.OutlookForWindows*`                                      |
|| Remove Outlook shortcuts    | Removes these files:<ul><li>`%ProgramData%\Microsoft\Windows\Start Menu\Programs\Outlook.lnk`</li><li>`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Outlook.lnk`</li><li>`%ProgramData%\Microsoft\Windows\Start Menu\Programs\Microsoft Office\Outlook.lnk`</li><li>`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Microsoft Office\Outlook.lnk`</li><li>`%PUBLIC%\Desktop\Outlook.lnk`</li><li>`%USERPROFILE%\Desktop\Outlook.lnk`</li><li>`%PUBLIC%\Desktop\Microsoft Outlook.lnk`</li><li>`%USERPROFILE%\Desktop\Microsoft Outlook.lnk`</li><li>`%PUBLIC%\Desktop\Outlook (New).lnk`</li><li>`%USERPROFILE%\Desktop\Outlook (New).lnk`</li><li>`%ProgramData%\Microsoft\Windows\Start Menu\Programs\Outlook (New).lnk`</li><li>`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Outlook (New).lnk`</li></ul> |

| **Taskbar** | De-bloat step | Details |
|-------------|---------------|---------|
|| Modifies Registries | Sets value of property `ShowTaskViewButton` in entry `HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced` to `DWord: 0`.<br>Removes properties `Favorites`, `FavoritesResolve`, `FavoritesRemovedChanges`, `TaskbarWinXP`, and `PinnedItems` from these registry entries:<ul><li>`HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Taskband`</li><li>`HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\TaskbarMRU`</li><li>`HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\TaskBar`</li><li>`HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced`</li></ul> |
|| Removes files and directories | <ul><li>`%LOCALAPPDATA%\Microsoft\Windows\Shell\LayoutModification.xml`</li><li>`%LOCALAPPDATA%\Microsoft\Windows\Explorer\iconcache*`</li><li>`%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache*`</li></ul> |

| **OneDrive** | De-bloat step | Details |
|--------------|---------------|---------|
|| Uninstalls OneDrive | Attempts to use the official uninstall scripts:<ul><li>`%SYSTEMROOT%\SysWOW64\OneDriveSetup.exe /uninstall`</li><li>`%SYSTEMROOT%\System32\OneDriveSetup.exe /uninstall`</li></ul> |
|| Deletes OneDrive-related folders and files | Removes:<ul><li>`%ProgramData%\Microsoft\Windows\Start Menu\Programs\OneDrive.lnk`</li><li>`%APPDATA%\Microsoft\Windows\Start Menu\Programs\OneDrive.lnk`</li><li>`%PUBLIC%\Desktop\OneDrive.lnk`</li><li>`%USERPROFILE%\Desktop\OneDrive.lnk`</li><li>`%USERPROFILE%\OneDrive`</li><li>`%LOCALAPPDATA%\Microsoft\OneDrive`</li><li>`%ProgramData%\Microsoft\OneDrive`</li><li>`%SystemDrive%\OneDriveTemp`</li></ul> |
|| Restarts File Explorer |  |

### Step 2: Browser Installation
Can be skipped with the `--skip-browser-installation-step` flag.

> This step is only run in Talon, not Talon Lite

| De-bloat step                                      | Details |
|----------------------------------------------------|---------|
| Install [chocolatey](https://chocolatey.org/about) | chocolatey is a package manager for Windows used by Talon to install the browser |
| Install [vcredist](https://learn.microsoft.com/en-us/cpp/Windows/latest-supported-vc-redist?view=msvc-170) with chocolatey | vcredist, better know as the *Microsoft C++ Redistributable* contains many libraries that several Windows apps depend on, including some of the available browser options |
| Install browser with chocolatey |  |

### Step 3: Execute External Scripts
Can be skipped with the `--skip-execute-external-scripts-step` flag.

| **WinUtil**   | Argument       | Talon | Talon Lite | Details                   |
|-------------|------------------|:-----:|:----------:|---------------------------|
|| WPFTweaksDisplay              |   X   |      X     | Sets display settings for performance |
|| WPFTweaksDisableLMS1          |   X   |      X     | Disables an Intel system that allows remote control capabilities |
|| WPFTweaksAH                   |   X   |      X     | Disable Activity History, which tracks what apps you use and when, this data is used to suggest stuff to you in the recommendation section of the Start Menu, and is included in telemetry |
|| WPFTweaksServices             |   X   |      X     | Many background running services sit idly and take up resources pointlessly. Turns many background system services that don't need to be running all the time to manual, so they only run when they need to, then exit after |
|| WPFTweaksConsumerFeatures     |   X   |      X     | Stops Windows from auto-installing apps or games without your permission |
|| WPFTweaksRemoveCopilot        |   X   |      X     | Removes Microsoft Copilot AI |
|| WPFTweaksWifi                 |   X   |      X     | Disables WifiSense,  |
|| WPFTweaksTele                 |   X   |      X     | Disables Microsoft Telemetry. Note: This will lock many Edge Browser settings. Microsoft spies heavily on you when using the Edge browser. |
|| WPFTweaksDisableBGapps        |   X   |      X     | Disables all Microsoft Store apps from running in the background |
|| WPFTweaksRecallOff            |   X   |      X     | Disables Recall |
|| WPFTweaksRemoveHome           |   X   |            | Removes the Home from Explorer and sets This PC as default |
|| WPFTweaksRemoveGallery        |   X   |            | Removes the Gallery from Explorer and sets This PC as default |
|| WPFTweaksRemoveOnedrive       |   X   |            | Removes OneDrive |
|| WPFTweaksRightClickMenu       |   X   |            | Brings back the Windows 10 right-click menu |
|| WPFTweaksLoc                  |   X   |            | Disables location tracking |
|| WPFTweaksDisableWpbtExecution |   X   |            | Disables Manufacturer-provided startup scripts |
|| WPFTweaksDVR                  |   X   |            | Disables GameDVR, a part of the Xbox Game Bar that always records your screen. Disabling this reduces overhead and improves consistent frame times and input latency |
|| WPFTweaksDeBloat              |   X   |            | This will remove ALL Microsoft store apps other than the essentials |
|| WPFTweaksDisableExplorerAutoDiscovery |   X   |            | Disables Explorer Automatic Folder Discovery as it can slow down loading times |


| **Win11Debloat** | Argument | Talon | Talon Lite | Details             |
|------------------|----------|:-----:|:----------:|---------------------|
|| Silent                     |   X   |     X      | Runs without output |
|| RemoveApps                 |   X   |     X      | Removes all apps listed [here](#apps-removed-by-win11debloat) |
|| RemoveGamingApps           |   X   |            | Remove the Xbox App and Xbox Game Bar |
|| DisableTelemetry           |   X   |     X      | Disable telemetry, diagnostic data, activity history, app-launch tracking & targeted ads |
|| DisableBing                |   X   |     X      | Disable & remove Bing web search, Bing AI and Cortana from Windows search |
|| DisableSuggestions         |   X   |     X      | Disable tips, tricks, suggestions and ads in start, settings, notifications and File Explorer |
|| DisableLockscreenTips      |   X   |     X      | Disable tips & tricks on the lockscreen |
|| RevertContextMenu          |   X   |            | Restore the old Windows 10 style context menu (Windows 11 only) |
|| TaskbarAlignLeft           |   X   |            | Align taskbar icons to the left (Windows 11 only) |
|| HideSearchTb               |   X   |            | Hide search icon from the taskbar (Windows 11 only) |
|| DisableWidgets             |   X   |     X      | Disable widgets on the taskbar & lockscreen |
|| DisableCopilot             |   X   |     X      | Disable & remove Microsoft Copilot |
|| ClearStartAllUsers         |   X   |            | Remove all pinned apps from the start menu for all existing and new users |
|| DisableDVR                 |   X   |            | Disable Xbox game/screen recording |
|| DisableStartRecommended    |   X   |     X      | Disable the recommended section in the start menu (Windows 11 only) |
|| ExplorerToThisPC           |   X   |     X      | Change the default location that File Explorer opens to 'This PC' |
|| DisableMouseAcceleration   |   X   |     X      | Turn off Enhance Pointer Precision (mouse acceleration) |
|| DisableDesktopSpotlight    |   X   |            | Disable the Windows Spotlight desktop background option |
|| DisableSettings365Ads      |   X   |            | Disable Microsoft 365 ads in Settings Home (Windows 11 only) |
|| DisableSettingsHome        |   X   |            | Completely hide the Settings 'Home' page (Windows 11 only) |
|| DisablePaintAI             |   X   |            | Disable AI features in Paint (Windows 11 only) |
|| DisableNotepadAI           |   X   |            | Disable AI features in Notepad (Windows 11 only) |
|| DisableStickyKeys          |   X   |            | Disable the Sticky Keys keyboard shortcut (Windows 11 only) |

### Step 4: Registry Tweaks
Can be skipped with the `--skip-registry-tweaks-step` flag.

> This step modifies several registries as listed

| Registry Entry                                                                    | Name                 | Value   | Talon | Talon Lite | Description                                          |
|-----------------------------------------------------------------------------------|----------------------|---------|:-----:|:----------:|------------------------------------------------------|
| HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced                 | TaskbarAl            | DWord:0 |   X   |            | Align the taskbar to the left                        |
| HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize                | AppsUseLightTheme    | DWord:0 |   X   |            | Sets user apps to use dark mode                      |
| HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize                | SystemUsesLightTheme | DWord:0 |   X   |            | Sets system to dark mode                             |
| HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR                           | AppCaptureEnabled    | DWord:0 |   X   |            | Disable Xbox Game Barrecording system                |
| HKLM:\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR | Value                | DWord:0 |   X   |            | Disable Xbox Game Barrecording system                |
| HKCU:\Control Panel\Desktop                                                       | MenuShowDelay        |  sz:"0" |   X   |     X      | Disables animations for opening Windows search menu  |
| HKCU:\Control Panel\Desktop\WindowMetrics                                         | MinAnimate           | DWord:0 |   X   |     X      | Disables animations for opening Windows Search Menu and Explorer UIs |
| HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced                 | ExtendedUIHoverTime  | DWord:1 |   X   |     X      | Makes window previews on taskbar display immediately |
| HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced                 | HideFileExt          | DWord:0 |   X   |     X      | Shows file extensions                                |
| HKCU:\Control Panel\Desktop                                                       | DragFullWindows      |  sz:"1" |   X   |            | Makes app windows look normal while dragging them around |

### Step 5: Configure Updates
Can be skipped with the `--skip-configure-updates-step` flag.

> Runs the [update_policy_changer.ps1](https://github.com/ravendevteam/talon/blob/main/debloat_raven_scripts/update_policy_changer.ps1) script, or if you are on Pro or Enterprise, runs [update_policy_changer_pro.ps1](https://github.com/ravendevteam/talon/blob/main/debloat_raven_scripts/update_policy_changer_pro.ps1)

**update_policy_changer.ps1**
-----------------------------
Modifies the following properties of the `HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate` registry, which together makes Windows delay non-security updates for 365 days.
| Property                        | Value           | Details |
|---------------------------------|-----------------|---------|
| DeferQualityUpdates             | DWord:1         | Delays non-security updates |
| DeferQualityUpdatesPeriodInDays | DWord:4         | Delays non-security updates |
| ProductVersion                  | sz:"Windows 11" | Tells Windows to stay on the specified version |
| TargetReleaseVersion            | DWord:1         | Tells Windows to stay on the specified version |
| TargetReleaseVersionInfo        | sz:"24H2"       | Tells Windows to stay on the specified version |

**update_policy_changer_pro.ps1**
---------------------------------
Modifies the following properties of the `HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate` registry, which prevent Windows from installing non-security updates permanently.  
This script utilizes a pro+ feature called *Windows Update for Business*, which normally lets businesses limit the amount of updates received on office computers, Talon leverages it to disable non-security updates.
| Property                        | Value   | Details |
|---------------------------------|---------|---------|
| ExcludeUpdateClassifications    | Set to a string of all the UUIDs in the [below table](#classification-table) separated by semicolons | Excludes the specified update classifications from being installed |
| ExcludeWUDriversInQualityUpdate | DWord:1 | Blocks drivers from being installed by updates |
| AUOptions                       | DWord:2 | Makes Windows notify you before installing updates |

#### Classification Table
| Classification   | UUID                                     |
|------------------|------------------------------------------|
| Critical Updates | `{e6cf1350-c01b-414d-a61f-263d3d4dd9f9}` |
| Feature Packs    | `{b54e7d24-7add-49f4-88bb-9837d47477fb}` |
| Service Packs    | `{68c5b0a3-d1a6-4553-ae49-01d3a7827828}` |
| Tools            | `{b4832bd8-e735-4766-9727-7d0ffa644277}` |
| Update Rollups   | `{28bc8804-5382-4bae-93aa-13c905f28542}` |
| Updates          | `{cd5ffd1e-e257-4a05-9d88-c83a7125d4c9}` |
| Non-critical     | `{0f1afbec-90ef-4651-9e37-030fedc944c8}` |
| Drivers          | `{ebfc1fc5-71a4-4f7b-9aca-3b9a503104a0}` |
| Feature Updates  | `{9920c092-3d99-4a1b-865a-673135c5a4fc}` |


### Step 6: Apply background
Can be skipped with the `--skip-apply-background-step` flag.

> This step only runs in Talon, not Talon Lite

Sets your desktop background to [this image](https://github.com/ravendevteam/talon/blob/main/media/desktop_background.png)

### Apps Removed by Win11Debloat

<summary>
<b>Microsoft apps</b>
</summary><details>
<li>Clipchamp.Clipchamp</li>
    <blockquote>Video editor from Microsoft</blockquote>
<li>Microsoft.3DBuilder</li>
    <blockquote>Basic 3D modeling software</blockquote>
<li>Microsoft.549981C3F5F10</li>
    <blockquote>Cortana app (Voice assistant)</blockquote>
<li>Microsoft.BingFinance</li>
    <blockquote>Finance news and tracking via Bing (Discontinued)</blockquote>
<li>Microsoft.BingFoodAndDrink</li>
    <blockquote>Recipes and food news via Bing (Discontinued)</blockquote>
<li>Microsoft.BingHealthAndFitness</li>
    <blockquote>Health and fitness tracking/news via Bing (Discontinued)</blockquote>
<li>Microsoft.BingNews</li>
    <blockquote>News aggregator via Bing (Replaced by Microsoft News/Start)</blockquote>
<li>Microsoft.BingSports</li>
    <blockquote>Sports news and scores via Bing (Discontinued)</blockquote>
<li>Microsoft.BingTranslator</li>
    <blockquote>Translation service via Bing</blockquote>
<li>Microsoft.BingTravel</li>
    <blockquote>Travel planning and news via Bing (Discontinued)</blockquote>
<li>Microsoft.BingWeather</li>
    <blockquote>Weather forecast via Bing</blockquote>
<li>Microsoft.Copilot</li>
    <blockquote>AI assistant integrated into Windows</blockquote>
<li>Microsoft.Getstarted</li>
    <blockquote>Tips and introductory guide for Windows (Cannot be uninstalled in Windows 11)</blockquote>
<li>Microsoft.Messaging</li>
    <blockquote>Messaging app, often integrates with Skype (Largely deprecated)</blockquote>
<li>Microsoft.Microsoft3DViewer</li>
    <blockquote>Viewer for 3D models</blockquote>
<li>Microsoft.MicrosoftJournal</li>
    <blockquote>Digital note-taking app optimized for pen input</blockquote>
<li>Microsoft.MicrosoftOfficeHub</li>
    <blockquote>Hub to access Microsoft Office apps and documents (Precursor to Microsoft 365 app)</blockquote>
<li>Microsoft.MicrosoftPowerBIForWindows</li>
    <blockquote>Business analytics service client</blockquote>
<li>Microsoft.MicrosoftSolitaireCollection</li>
    <blockquote>Collection of solitaire card games</blockquote>
<li>Microsoft.MicrosoftStickyNotes</li>
    <blockquote>Digital sticky notes app (Deprecated & replaced by OneNote)</blockquote>
<li>Microsoft.MixedReality.Portal</li>
    <blockquote>Portal for Windows Mixed Reality headsets</blockquote>
<li>Microsoft.NetworkSpeedTest</li>
    <blockquote>Internet connection speed test utility</blockquote>
<li>Microsoft.News</li>
    <blockquote>News aggregator (Replaced Bing News, now part of Microsoft Start)</blockquote>
<li>Microsoft.Office.OneNote</li>
    <blockquote>Digital note-taking app (Universal Windows Platform version)</blockquote>
<li>Microsoft.Office.Sway</li>
    <blockquote>Presentation and storytelling app</blockquote>
<li>Microsoft.OneConnect</li>
    <blockquote>Mobile Operator management app (Replaced by Mobile Plans)</blockquote>
<li>Microsoft.Print3D</li>
    <blockquote>3D printing preparation software</blockquote>
<li>Microsoft.PowerAutomateDesktop</li>
    <blockquote>Desktop automation tool (RPA)</blockquote>
<li>Microsoft.SkypeApp</li>
    <blockquote>Skype communication app (Universal Windows Platform version)</blockquote>
<li>Microsoft.Todos</li>
    <blockquote>To-do list and task management app</blockquote>
<li>Microsoft.Windows.DevHome</li>
    <blockquote>Developer dashboard and tool configuration utility, no longer supported</blockquote>
<li>Microsoft.WindowsAlarms</li>
    <blockquote>Alarms & Clock app</blockquote>
<li>Microsoft.WindowsFeedbackHub</li>
    <blockquote>App for providing feedback to Microsoft on Windows</blockquote>
<li>Microsoft.WindowsMaps</li>
    <blockquote>Mapping and navigation app</blockquote>
<li>Microsoft.WindowsSoundRecorder</li>
    <blockquote>Basic audio recording app</blockquote>
<li>Microsoft.XboxApp</li>
    <blockquote>Old Xbox Console Companion App, no longer supported</blockquote>
<li>Microsoft.ZuneVideo</li>
    <blockquote>Movies & TV app for renting/buying/playing video content (Rebranded as "Films & TV")</blockquote>
<li>MicrosoftCorporationII.MicrosoftFamily</li>
    <blockquote>Family Safety App for managing family accounts and settings</blockquote>
<li>MicrosoftCorporationII.QuickAssist</li>
    <blockquote>Remote assistance tool</blockquote>
<li>MicrosoftTeams</li>
    <blockquote>Old MS Teams personal (MS Store version)</blockquote>
<li>MSTeams</li>
    <blockquote>New MS Teams app (Work/School or Personal)</blockquote>
</details>
<br>

<summary>
<b>Other apps</b>
</summary><details>
<li>ACGMediaPlayer</li>
    <blockquote>Media player app</blockquote>
<li>ActiproSoftwareLLC</li>
    <blockquote>Potentially UI controls or software components, often bundled by OEMs</blockquote>
<li>AdobeSystemsIncorporated.AdobePhotoshopExpress</li>
    <blockquote>Basic photo editing app from Adobe</blockquote>
<li>Amazon.com.Amazon</li>
    <blockquote>Amazon shopping app</blockquote>
<li>AmazonVideo.PrimeVideo</li>
    <blockquote>Amazon Prime Video streaming service app</blockquote>
<li>Asphalt8Airborne</li>
    <blockquote>Racing game</blockquote>
<li>AutodeskSketchBook</li>
    <blockquote>Digital drawing and sketching app</blockquote>
<li>CaesarsSlotsFreeCasino</li>
    <blockquote>Casino slot machine game</blockquote>
<li>COOKINGFEVER</li>
    <blockquote>Restaurant simulation game</blockquote>
<li>CyberLinkMediaSuiteEssentials</li>
    <blockquote>Multimedia software suite (often preinstalled by OEMs)</blockquote>
<li>DisneyMagicKingdoms</li>
    <blockquote>Disney theme park building game</blockquote>
<li>Disney</li>
    <blockquote>General Disney content app (may vary by region/OEM, often Disney+)</blockquote>
<li>DrawboardPDF</li>
    <blockquote>PDF viewing and annotation app, often focused on pen input</blockquote>
<li>Duolingo-LearnLanguagesforFree</li>
    <blockquote>Language learning app</blockquote>
<li>EclipseManager</li>
    <blockquote>Often related to specific OEM software or utilities (e.g., for managing screen settings)</blockquote>
<li>Facebook</li>
    <blockquote>Facebook social media app</blockquote>
<li>FarmVille2CountryEscape</li>
    <blockquote>Farming simulation game</blockquote>
<li>fitbit</li>
    <blockquote>Fitbit activity tracker companion app</blockquote>
<li>Flipboard</li>
    <blockquote>News and social network aggregator styled as a magazine</blockquote>
<li>HiddenCity</li>
    <blockquote>Hidden object puzzle adventure game</blockquote>
<li>HULULLC.HULUPLUS</li>
    <blockquote>Hulu streaming service app</blockquote>
<li>iHeartRadio</li>
    <blockquote>Internet radio streaming app</blockquote>
<li>Instagram</li>
    <blockquote>Instagram social media app</blockquote>
<li>king.com.BubbleWitch3Saga</li>
    <blockquote>Puzzle game from King</blockquote>
<li>king.com.CandyCrushSaga</li>
    <blockquote>Puzzle game from King</blockquote>
<li>king.com.CandyCrushSodaSaga</li>
    <blockquote>Puzzle game from King</blockquote>
<li>LinkedInforWindows</li>
    <blockquote>LinkedIn professional networking app</blockquote>
<li>MarchofEmpires</li>
    <blockquote>Strategy game</blockquote>
<li>Netflix</li>
    <blockquote>Netflix streaming service app</blockquote>
<li>NYTCrossword</li>
    <blockquote>New York Times crossword puzzle app</blockquote>
<li>OneCalendar</li>
    <blockquote>Calendar aggregation app</blockquote>
<li>PandoraMediaInc</li>
    <blockquote>Pandora music streaming app</blockquote>
<li>PhototasticCollage</li>
    <blockquote>Photo collage creation app</blockquote>
<li>PicsArt-PhotoStudio</li>
    <blockquote>Photo editing and creative app</blockquote>
<li>Plex</li>
    <blockquote>Media server and player app</blockquote>
<li>PolarrPhotoEditorAcademicEdition</li>
    <blockquote>Photo editing app (Academic Edition)</blockquote>
<li>Royal Revolt</li>
    <blockquote>Tower defense / strategy game</blockquote>
<li>Shazam</li>
    <blockquote>Music identification app</blockquote>
<li>Sidia.LiveWallpaper</li>
    <blockquote>Live wallpaper app</blockquote>
<li>SlingTV</li>
    <blockquote>Live TV streaming service app</blockquote>
<li>Spotify</li>
    <blockquote>Spotify music streaming app</blockquote>
<li>TikTok</li>
    <blockquote>TikTok short-form video app</blockquote>
<li>TuneInRadio</li>
    <blockquote>Internet radio streaming app</blockquote>
<li>Twitter</li>
    <blockquote>Twitter (now X) social media app</blockquote>
<li>Viber</li>
    <blockquote>Messaging and calling app</blockquote>
<li>WinZipUniversal</li>
    <blockquote>File compression and extraction utility (Universal Windows Platform version)</blockquote>
<li>Wunderlist</li>
    <blockquote>To-do list app (Acquired by Microsoft, functionality moved to Microsoft To Do)</blockquote>
<li>XING</li>
    <blockquote>Professional networking platform popular in German-speaking countries</blockquote>
</details>
<br>

# Talon Development

Here is some useful info for if you would like help contribute to Talon or Talon Lite:  

Talon and Talon Lite are both written in [Python 3.12.4](https://www.python.org/downloads/release/python-3124/) and use [PyQt5](https://wiki.python.org/moin/PyQt) for graphics.  

The Python compiler [Nuitka](https://nuitka.net/) is used to create the executable.  

To build Talon or Talon Lite from source, clone the respective repository and run `pip install -r requirements.txt`. Afterwards, run the `build.bat` file, and the compiled executable is found at `dist/Talon.exe` (or `dist/Talonlite.exe`).   

> NOTE: WinUtil and Win11Debloat are downloaded then bundled at compile time, meaning the exact version that is embedded in the EXE you compile may differ. If either tool has changed their capabilities since the latest Talon release, some aspects may no longer work as intended. This can result in a different file hash as well.  



# Talon FAQ

**Q: How do I install Talon?**  
A: First, disable Real Time Protection in your Windows Defender (this is automatically re-enabled after restarting your PC), then download the latest version of Talon from [here](https://ravendevteam.org/explore#talon), then  run the .exe (Note: Sometimes Defender will still interfere and kill the process. In this case it is recommended to add an exclusion to your C:\ drive. **BE SURE TO REMOVE THIS AFTER TALON IS INSTALLED!**)

**Q: Can I run Talon on an in-use Windows 11 system?**  
A: Use Talon Lite, it is a less extreme de-bloater that still cleans out clutter and AI without the risk of breaking already-installed apps.

**Q: Can I run Talon on Windows 10?**  
A: You can use Talon Lite, which is designed for Windows 10 and in-use Windows 11 systems.

**Q: Why does Talon appear as a Trojan/Virus on my virus detector?**  
A: Talon / Talon Lite are commonly flagged by anti-viruses as they make heavy modifications to your system like changing system settings, uninstalling programs, and modifying the registry. The way the EXEs are packaged also causes many false flags. We are working on reducing these flags.

**Q: A new version of Talon just came out, do I need to run it again?**  
A: No, Talon is a run and done tool and re-running it can cause harm to your system.

**Q: Does Talon remove Snipping Tool/Why are my screenshots not saving?**  
A: Yes, Talon does remove Snipping Tool. As a result, screenshots are saved to our clipboard, You can re-install Snipping Tool from the Microsoft Store if you wish. 

**Q: Why do some settings say they are 'Managed by your organization'?**  
A: This is a result of Talon changing system policies, and Windows defaults to saying this message. Your system is not actually managed by any organization.

**Q: Does Talon remove bloat from my laptops manufacturers?**  
A: No, to remove manufacturer-specific bloat, you should re-install Windows completely before running Talon.

**Q: Can I undo the changes made by Talon?**  
A: The easiest way to do this is to reinstall Windows 11. Please be aware that resetting your PC through Settings > Recovery > Reset This PC will not restore Microsoft Edge.

**Q: Talon removed OneDrive/(whatever software you wanted that was removed), is there a way to get it back?**  
A: Yes. You can just reinstall the software from the appropriate sources. Talon is carefully designed so that any program it removes can be reinstalled by the user.

**Q: Should I install/update my drivers/Windows before or after Talon?**  
A: Before. You should make sure your device and drivers are fully updated before running Talon.

**Q: What is a normal Process count after running Talon?**  
A: We can’t give you a definite answer due to every system being different from each other because of hardware, drivers and (in some cases) manufacturer software. However, the process count will be lower than before Talon was run.

**Q: Will Talon affect any Anti-cheat software (e.g. Vanguard, EasyAntiCheat)?**  
A: No. Talon does not make any modifications that will interfere with any anti-cheat software.

**Q: Does Talon Remove Xbox Game Bar?**  
A: Only Talon removes Game Bar. Talon Lite does not. If you want to reinstall Game Bar, open your browser and paste this link to reinstall it from the Microsoft store. [ms-Windows-store://pdp/?productid=9NZKPSTSNW4P](ms-Windows-store://pdp/?productid=9NZKPSTSNW4P)

**Q: Where can I find the different wallpapers from Talon?**  
A: You can find different wallpapers here: https://drive.proton.me/urls/VY5KNZBSV0#IsanvOSj5ms2.

**Q: Why can't I access https://debloat.win/?**  
A: If you can't access it, go here instead: https://ravendevteam.org/explore#talon

**Q: What does 'Unable to check Windows Defender exclusions' mean?**  
A: This error message is due to Talon only supporting genuine copies of Windows 11 Home or Pro. Third Party ISOs are unsupported.

**Q: How does Talon effect Windows Updates/Will the next Windows Update re-bloat my machine?**  
A: Depending on whether you are using Home or Professional, Talon acts slightly different. On home, Talon blocks all updates - except security ones - for 365 days. If you would like to block updates after this period, you will need to save any important files on an external device, reinstall Windows and run Talon again. On Professional, Talon blocks all updates - except security ones - permanently.

**Q: Why is Talon stuck at Step 4?**  
A: If you have signed into OneDrive, Talon will stop here indefinitely. Restart your computer with CTRL+ALT+DEL, then completely sign out of OneDrive and run Talon again.

**Q: Can I run Talon without an internet connection?**  
A: Yes, however if ran without internet, a replacement browser after removing Edge will not be installed.

**Q: How do I run Talon through PowerShell?**  
A: Launch PowerShell as Administrator and run one of these commands:  
`irm https://debloat.win/now | iex` for Talon  
`irm https://debloat.win/lite | iex` for Talon Lite  



---
### Credits

[Westbot](https://github.com/westbot657)  
[MrBooks36](https://github.com/MrBooks36)
