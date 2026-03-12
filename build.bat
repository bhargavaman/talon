@echo off
set FileVersion=1.0.0.7
set ProductVersion=3.0.0.0
set "ROOT=%~dp0"
set "SCRIPT_BUNDLE_DIR=%ROOT%external_scripts"

if exist "%SCRIPT_BUNDLE_DIR%" rd /s /q "%SCRIPT_BUNDLE_DIR%"
mkdir "%SCRIPT_BUNDLE_DIR%"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
	"[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; " ^
	"$u1 = 'https://christitus.com/win'; " ^
	"$u2 = 'https://api.github.com/repos/Raphire/Win11Debloat/zipball/2026.03.09'; " ^
	"$o1 = Join-Path '%SCRIPT_BUNDLE_DIR%' 'winutil.ps1'; " ^
	"$zip2 = Join-Path '%SCRIPT_BUNDLE_DIR%' 'win11debloat.zip'; " ^
	"Invoke-WebRequest -Uri $u1 -OutFile $o1 -UseBasicParsing; " ^
	"Invoke-WebRequest -Uri $u2 -OutFile $zip2 -UseBasicParsing; " ^
	"try { Expand-Archive -LiteralPath $zip2 -DestinationPath '%SCRIPT_BUNDLE_DIR%' -Force } catch { Write-Error $_; exit 1 }; " ^
	"Remove-Item -LiteralPath $zip2 -Force; " ^
	"$c = Get-Content -LiteralPath $o1 -Raw -Encoding UTF8; " ^
	"$patched = [regex]::Replace($c,'(?ms)^\s*Write-Host ""Installing features\.\.\.""\s*.*?Write-Host ""Done\.""','Write-Host ""Features installation skipped""' + [Environment]::NewLine); " ^
	"Set-Content -LiteralPath $o1 -Value $patched -Encoding UTF8;"

python -m nuitka --standalone --enable-plugins=pyqt5 --include-qt-plugins=qml --remove-output --windows-disable-console --windows-uac-admin --output-dir=dist --output-filename=Talon.exe --follow-imports --windows-icon-from-ico=media\ICON.ico --include-data-dir=media=media --include-data-dir=ui=ui --include-data-dir=debloat_raven_scripts=debloat_raven_scripts --include-data-dir=external_scripts=external_scripts --include-package=screens --product-name="Talon" --company-name="Raven Technologies Group" --file-description="Simple utility to debloat Windows in 2 clicks." --file-version=%FileVersion% --product-version=%ProductVersion% --copyright="Copyright (c) 2026 Raven Technologies Group LLC" talon.py
pause