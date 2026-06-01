import os
import tempfile
from utilities.util_windows_check import check_windows_11_home_or_pro
from utilities.util_error_popup import show_error_popup
from utilities.util_logger import logger
from configuration_components.localization import t

def _check_temp_writable() -> bool:
    temp_root = os.environ.get("TEMP", tempfile.gettempdir())
    talon_dir = os.path.join(temp_root, "talon")
    try:
        os.makedirs(talon_dir, exist_ok=True)
        fd, test_path = tempfile.mkstemp(prefix="talon_write_", dir=talon_dir)
        try:
            with os.fdopen(fd, "w") as f:
                f.write("test")
        finally:
            try:
                os.remove(test_path)
            except FileNotFoundError:
                pass
        return True
    except Exception as e:
        logger.error(f"Temp dir check failed: {e}")
        show_error_popup(
            t("errors.temp_unwritable", {"talon_dir": talon_dir}),
            allow_continue=True,
        )
        return False

def main() -> None:
    check_windows_11_home_or_pro()
    if not _check_temp_writable():
        raise SystemExit(1)

if __name__ == "__main__":
    main()
