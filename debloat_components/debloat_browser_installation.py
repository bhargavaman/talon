import os
import sys
import subprocess
from utilities.util_logger import logger
from utilities.util_error_popup import show_error_popup
from utilities.util_powershell_handler import run_powershell_command



def ensure_chocolatey():
	try:
		subprocess.run(
			["choco", "-v"],
			check=True,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL
		)
		logger.info("Chocolatey already installed.")
	except (subprocess.CalledProcessError, FileNotFoundError):
		logger.info("Chocolatey not found. Installing now...")
		install_cmd = (
			"Set-ExecutionPolicy Bypass -Scope Process -Force; "
			"[System.Net.ServicePointManager]::SecurityProtocol = "
			"[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
			"iex ((New-Object System.Net.WebClient).DownloadString("
			"'https://community.chocolatey.org/install.ps1'))"
		)
		logger.info(f"Running install command: {install_cmd}")
		try:
			run_powershell_command(install_cmd)
			logger.info("Chocolatey install script executed.")
			choco_exe = _get_choco_exe()
			subprocess.run(
				[choco_exe, "-v"],
				check=True,
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL
			)
			logger.info("Chocolatey installed and verified.")
		except Exception as e:
			logger.error(f"Failed to install or verify Chocolatey: {e}")
			show_error_popup(
				f"Failed to install or verify Chocolatey:\n{e}",
				allow_continue=False
			)
			sys.exit(1)



def _get_choco_exe() -> str:
	env_path = os.environ.get("ChocolateyInstall")
	if env_path:
		choco = os.path.join(env_path, "bin", "choco.exe")
		if os.path.exists(choco):
			return choco
	default_path = os.path.join(
		os.environ.get("ProgramData", r"C:\\ProgramData"),
		"chocolatey",
		"bin",
		"choco.exe",
	)
	return default_path if os.path.exists(default_path) else "choco"



def _install_choco_package(pkg_id: str, display_name: str):
	choco_exe = _get_choco_exe()
	logger.info(f"Installing via Chocolatey: {display_name} ({pkg_id})")
	try:
		result = subprocess.run(
			[choco_exe, "install", pkg_id, "-y"],
			check=False
		)
		if result.returncode in (0, 3010):
			if result.returncode == 3010:
				logger.info(f"Successfully installed {display_name}, reboot required.")
			else:
				logger.info(f"Successfully installed {display_name}.")
			return
		logger.error(f"Chocolatey exited with code {result.returncode} for {pkg_id}")
		show_error_popup(
			"A problem occurred with Chocolatey during installation. "
			f"'{display_name}' could not be installed successfully.\n"
			f"Chocolatey exit code: {result.returncode}",
			allow_continue=True
		)
	except Exception as e:
		logger.error(f"Unexpected error installing {pkg_id}: {e}")
		show_error_popup(
			"A problem occurred with Chocolatey during installation. "
			f"'{display_name}' could not be installed successfully.\n"
			f"Error: {e}",
			allow_continue=True
		)



def install_vcredist():
	_install_choco_package("vcredist140", "Microsoft Visual C++ 2015â€“2022 Redistributable")



def install_browser(pkg_id: str):
	_install_choco_package(pkg_id, f"browser '{pkg_id}'")



def main(selected_browser_package=None):
	try:
		pkg_id = str(selected_browser_package or "").strip()
		if not pkg_id:
			raise ValueError("No browser package was provided by the runner metadata.")
		logger.info(f"Browser selected: {pkg_id}")
	except Exception as e:
		logger.error(f"Error reading browser choice metadata: {e}")
		show_error_popup(f"Internal error reading browser choice metadata:\n{e}", allow_continue=False)
		sys.exit(1)
	ensure_chocolatey()
	install_vcredist()
	install_browser(pkg_id)



if __name__ == "__main__":
	main()
