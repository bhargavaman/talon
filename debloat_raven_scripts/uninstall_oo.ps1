# Uninstall OO
# filename: uninstall_oo.ps1
#
# This script is designed to uninstall One Drive and Outlook from Windows 11 systems.
# The user can still reinstall these programs from Microsoft's website at any time.

# Run with highest privileges
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    try {
        Start-Process PowerShell -Verb RunAs "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -WindowStyle Hidden
        exit
    }
    catch {
        exit
    }
}

try {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    $ErrorActionPreference = 'SilentlyContinue'
    $administratorsSid = "*S-1-5-32-544"

    function Remove-ShortcutByTarget {
        param(
            [string[]]$SearchRoots,
            [string[]]$TargetPatterns
        )

        $wshShell = $null
        try {
            $wshShell = New-Object -ComObject WScript.Shell
        }
        catch {
            return
        }

        foreach ($root in $SearchRoots) {
            if (-not (Test-Path $root)) {
                continue
            }

            Get-ChildItem -Path $root -Filter *.lnk -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
                try {
                    $shortcut = $wshShell.CreateShortcut($_.FullName)
                    $targetData = @(
                        $shortcut.TargetPath,
                        $shortcut.Arguments,
                        $shortcut.IconLocation,
                        $_.BaseName
                    ) -join ' '

                    foreach ($pattern in $TargetPatterns) {
                        if ($targetData -like $pattern) {
                            Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
                            break
                        }
                    }
                }
                catch {}
            }
        }
    }

    # Close Outlook processes
    Get-Process | Where-Object { $_.ProcessName -like "*outlook*" } | Stop-Process -Force
    Start-Sleep -Seconds 2

    # Remove Outlook apps
    Get-AppxPackage *Microsoft.Office.Outlook* | Remove-AppxPackage
    Get-AppxProvisionedPackage -Online | Where-Object {$_.PackageName -like "*Microsoft.Office.Outlook*"} | Remove-AppxProvisionedPackage -Online
    Get-AppxPackage *Microsoft.OutlookForWindows* | Remove-AppxPackage
    Get-AppxProvisionedPackage -Online | Where-Object {$_.PackageName -like "*Microsoft.OutlookForWindows*"} | Remove-AppxProvisionedPackage -Online

    # Remove Outlook folders
    $windowsAppsPath = "C:\Program Files\WindowsApps"
    $outlookFolders = Get-ChildItem -Path $windowsAppsPath -Directory | Where-Object { $_.Name -like "Microsoft.OutlookForWindows*" }
    foreach ($folder in $outlookFolders) {
        $folderPath = Join-Path $windowsAppsPath $folder.Name
        takeown /f $folderPath /r /d Y | Out-Null
        icacls $folderPath /grant "${administratorsSid}:F" /t /c | Out-Null
        Remove-Item -Path $folderPath -Recurse -Force
    }

    # Remove shortcuts
    $shortcutRoots = @(
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs",
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs",
        "$env:PUBLIC\Desktop",
        [Environment]::GetFolderPath('Desktop')
    )

    Remove-ShortcutByTarget -SearchRoots $shortcutRoots -TargetPatterns @(
        "*OUTLOOK.EXE*",
        "*Microsoft.Office.Outlook*",
        "*Microsoft.OutlookForWindows*",
        "*Outlook*"
    )

    # Taskbar cleanup
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ShowTaskViewButton" -Value 0 -Type DWord -Force

    $registryPaths = @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Taskband",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\TaskbarMRU",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\TaskBar",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
    )
    foreach ($path in $registryPaths) {
        if (Test-Path $path) {
            @("Favorites", "FavoritesResolve", "FavoritesChanges", "FavoritesRemovedChanges", "TaskbarWinXP", "PinnedItems") | 
            ForEach-Object { Remove-ItemProperty -Path $path -Name $_ -ErrorAction SilentlyContinue }
        }
    }

    Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Shell\LayoutModification.xml" -Force
    Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\iconcache*" -Force
    Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\thumbcache*" -Force

    # OneDrive removal
    Get-Process | Where-Object { $_.ProcessName -like "*onedrive*" } | Stop-Process -Force
    if (Test-Path "$env:SystemRoot\SysWOW64\OneDriveSetup.exe") {
        & "$env:SystemRoot\SysWOW64\OneDriveSetup.exe" /uninstall
    } elseif (Test-Path "$env:SystemRoot\System32\OneDriveSetup.exe") {
        & "$env:SystemRoot\System32\OneDriveSetup.exe" /uninstall
    }

    Remove-ShortcutByTarget -SearchRoots $shortcutRoots -TargetPatterns @(
        "*OneDrive.exe*",
        "*OneDrive*"
    )

    @(
        "$env:USERPROFILE\OneDrive",
        "$env:LOCALAPPDATA\Microsoft\OneDrive",
        "$env:ProgramData\Microsoft\OneDrive",
        "$env:SystemDrive\OneDriveTemp"
    ) | ForEach-Object { Remove-Item $_ -Force -Recurse }

    @(
        "HKCR:\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}",
        "HKCR:\Wow6432Node\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{018D5C66-4533-4307-9B53-224DE2ED1FE6}"
    ) | ForEach-Object { Remove-Item -Path $_ -Recurse -Force }

    # Restart Explorer
    Get-Process explorer | Stop-Process -Force
    Start-Sleep -Seconds 2
    Start-Process explorer
}
catch {}
exit 
