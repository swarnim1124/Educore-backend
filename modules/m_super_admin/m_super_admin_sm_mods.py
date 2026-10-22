"""
File: m_super_admin_sm_mods.py
Description: Submodule for Module-level CRUD operations in Super Admin.

Author: Akshay Basutkar, Siddharth Admal, Swarnim Deshpande
App: OneApp

"""

from pathlib import Path

# Anchor to <repo>/modules regardless of the process working directory.
MODULES_ROOT = Path(__file__).resolve().parents[1]

PROTECTED_CORE_MODULES = {
    "m_profile",
    "m_attendance",
    "m_AAA",
    "m_super_admin",
    "m_fees",
    "m_timetable",
    "m_curriculum",
    "m_exam",
}


def _extract_payload_ctx(request_or_payload, context):
    if hasattr(request_or_payload, "payload"):
        payload = getattr(request_or_payload, "payload", {}) or {}
        actual_ctx = context
    elif isinstance(request_or_payload, dict):
        payload = request_or_payload
        actual_ctx = context
    else:
        payload = {}
        actual_ctx = request_or_payload or context
    return payload, actual_ctx


class Mods:
    """
    Single submodule class handling all top-level module operations.
    """

    def __init__(self, modules_root: Path = None):
        self.modules_root = modules_root or MODULES_ROOT

    async def mods(self, request_or_action_type, payload_or_context=None, context=None):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        if hasattr(request_or_action_type, "actionType"):
            action_type = getattr(request_or_action_type, "actionType", "")
            payload = getattr(request_or_action_type, "payload", {}) or {}
            actual_ctx = payload_or_context
        elif isinstance(payload_or_context, dict):
            action_type = request_or_action_type
            payload = payload_or_context
            actual_ctx = context
        elif isinstance(payload_or_context, str):
            action_type = request_or_action_type
            payload = {"mod_name": payload_or_context, "new_name": payload_or_context}
            actual_ctx = context
        else:
            action_type = request_or_action_type
            payload = {}
            actual_ctx = payload_or_context or context

        action_type = (action_type or "").lower()

        match action_type:
            case "health":
                return self.health(payload, actual_ctx)
            case "create":
                return self.create(payload, actual_ctx)
            case "read":
                return self.read(payload, actual_ctx)
            case "update":
                return self.update(payload, actual_ctx)
            case "delete":
                return self.delete(payload, actual_ctx)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for mods"
                )

    # --- Public Action Handlers ---

    def health(self, request_or_payload=None, context=None):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        payload, ctx = _extract_payload_ctx(request_or_payload, context)
        return XSCUtility.success_response(message="", health="good")

    def create(self, request_or_payload, context=None):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from xsc_lib.xsc_lib_common.xsc_libc_string_operations import is_valid_name
        payload, ctx = _extract_payload_ctx(request_or_payload, context)

        mod = payload.get("mod_name") or ""
        clean_mod = mod.replace("m_", "")
        if not is_valid_name(clean_mod):
            return XSCUtility.error_response(message="Invalid module name")

        module_dir = self.modules_root / f"m_{clean_mod}"
        if module_dir.exists():
            return XSCUtility.error_response(message="Module already exists.")

        module_dir.mkdir(parents=True, exist_ok=True)

        pascal_mod = "".join(word.capitalize() for word in clean_mod.split("_") if word)

        # 1. Manifest
        manifest_code = f'''"""
File: manifest.py
Description: Module Manifest for m_{clean_mod}.
"""

MODULE_NAME = "m_{clean_mod}"
MODULE_VERSION = "1.0.0"
AUTHOR = "SuperAdmin Generator"
DESCRIPTION = "{clean_mod.capitalize()} Business Domain Module."

DEPENDENCIES = ["m_AAA"]

SUPPORTED_SUBMODULES = ["sm_default"]

DATABASE_SCHEMAS = ["sch_{clean_mod}"]

PERMISSIONS = ["{clean_mod}.default.manage"]

FEATURE_FLAGS = {{}}
'''
        (module_dir / "manifest.py").write_text(manifest_code, encoding="utf-8")

        # 2. Data Layer
        data_code = f'''"""
File: m_{clean_mod}_data.py
Description: Data Access Layer for m_{clean_mod}.
"""

import logging

logger = logging.getLogger(__name__)


class {pascal_mod}DataLayer:
    def __init__(self, db_manager):
        self.db = db_manager
'''
        (module_dir / f"m_{clean_mod}_data.py").write_text(data_code, encoding="utf-8")

        # 3. Default Submodule
        submod_code = f'''"""
File: m_{clean_mod}_sm_default.py
Description: Default submodule handler for m_{clean_mod}.
"""

import logging
from typing import Dict, Any
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

logger = logging.getLogger(__name__)


class sm_default:
    @staticmethod
    async def default_action(request: Any, context: Any) -> Dict[str, Any]:
        action_type = (request.actionType or "").lower()
        match action_type:
            case "view" | "read":
                return await sm_default.view(request, context)
            case _:
                return XSCUtility.error_response(message="Invalid actionType")

    @staticmethod
    async def view(request: Any, context: Any) -> Dict[str, Any]:
        return XSCUtility.success_response(message="Default view executed successfully")
'''
        (module_dir / f"m_{clean_mod}_sm_default.py").write_text(submod_code, encoding="utf-8")

        # 4. Entry Point Router
        entry_code = f'''"""
File: m_{clean_mod}.py
Description: Module entry point for m_{clean_mod}.
"""

class {pascal_mod}:
    async def {clean_mod}(self, request, context):
        from xsc_lib.xsc_lib_app.xsc_liba_dispatcher import ActionDispatcher
        return await ActionDispatcher.dispatch(request, context)
'''
        (module_dir / f"m_{clean_mod}.py").write_text(entry_code, encoding="utf-8")

        return XSCUtility.success_response(message=f"Module 'm_{clean_mod}' created successfully", code=200)

    def read(self, request_or_payload=None, context=None):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        payload, ctx = _extract_payload_ctx(request_or_payload, context)

        mods = [
            d.name
            for d in self.modules_root.iterdir()
            if d.is_dir() and d.name.startswith("m_")
        ]
        return XSCUtility.success_response(message="", code=200, mods=mods)

    def update(self, request_or_payload, context=None):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from xsc_lib.xsc_lib_common.xsc_libc_string_operations import is_valid_name
        payload, ctx = _extract_payload_ctx(request_or_payload, context)

        mod = (payload.get("mod_name") or "").replace("m_", "")
        new_mod = (payload.get("new_name") or "").replace("m_", "")

        if f"m_{mod}" in PROTECTED_CORE_MODULES:
            return XSCUtility.error_response(message=f"Cannot rename protected core system module 'm_{mod}'")

        if not (is_valid_name(mod) and is_valid_name(new_mod)):
            return XSCUtility.error_response(message="Invalid name(s)")

        module_dir = self.modules_root / f"m_{mod}"
        new_dir = self.modules_root / f"m_{new_mod}"

        if not module_dir.exists():
            return XSCUtility.error_response(message="Module does not exist")

        if new_dir.exists():
            return XSCUtility.error_response(message="Target module already exists")

        module_dir.rename(new_dir)

        for file in new_dir.iterdir():
            if not file.is_file():
                continue
            renamed = file.name.replace(f"m_{mod}", f"m_{new_mod}")
            target = new_dir / renamed
            if file != target:
                file.rename(target)
            if target.suffix == ".py":
                text = target.read_text(encoding="utf-8")
                text = text.replace(f"m_{mod}", f"m_{new_mod}")
                target.write_text(text, encoding="utf-8")

        return XSCUtility.success_response(message="Module renamed successfully")

    def delete(self, request_or_payload, context=None):
        import shutil
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from xsc_lib.xsc_lib_common.xsc_libc_string_operations import is_valid_name
        payload, ctx = _extract_payload_ctx(request_or_payload, context)

        raw_mod = XSCUtility.trim(payload.get("mod_name") or "")
        clean_mod = raw_mod.replace("m_", "")

        if f"m_{clean_mod}" in PROTECTED_CORE_MODULES:
            return XSCUtility.error_response(
                message=f"Access Denied: 'm_{clean_mod}' is a protected core system module and cannot be deleted."
            )

        if not is_valid_name(clean_mod):
            return XSCUtility.error_response(message="Invalid module name")

        module_dir = self.modules_root / f"m_{clean_mod}"

        if not module_dir.exists():
            return XSCUtility.error_response(
                message=f"Module 'm_{clean_mod}' does not exist."
            )

        # Move to .trash directory for safety backup before deleting
        trash_dir = self.modules_root.parent / ".trash" / f"m_{clean_mod}"
        if trash_dir.exists():
            shutil.rmtree(trash_dir)
        trash_dir.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(module_dir), str(trash_dir))
        return XSCUtility.success_response(
            message=f"Module 'm_{clean_mod}' safely deleted (moved to backup trash).", code=200
        )


# Class name aliases for ActionDispatcher resolution
sm_mods = Mods
