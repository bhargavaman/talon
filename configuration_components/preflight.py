import os

import preinstall_components.pre_checks as pre_checks
from utilities.util_admin_check import is_admin, run_as_admin
from utilities.util_internet_check import has_internet


def run_configuration_preflight() -> tuple:
    if os.environ.get("TALON_DRY_RUN") == "1":
        return has_internet(), False
    if not is_admin():
        run_as_admin()
        return False, True
    pre_checks.main()
    return has_internet(), False
