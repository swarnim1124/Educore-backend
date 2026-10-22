"""
File: xsc_libc_string_operations.py
Description: Handler for xsc_libc_string_operations operations in OneApp.

Author: Siddharth, Siddharth Amdal.
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility


import re


def is_valid_name(name: str) -> bool:
    """
    Executes the is_valid_name operation.
    """
    if not name or XSCUtility.trim(name) == "":
        return False

    # "." and ".." are not valid names
    if name in (".", ".."):
        return False

    # Invalid Windows characters
    if re.search(r'[<>:"/\\|?*]', name):
        return False

    # Cannot end with space or period
    if name.endswith(" ") or name.endswith("."):
        return False

    # Reserved Windows names
    reserved = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }

    if XSCUtility.to_upper(name) in reserved:
        return False

    return True
