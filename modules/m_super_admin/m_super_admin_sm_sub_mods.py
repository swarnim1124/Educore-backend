"""
File: m_super_admin_sm_sub_mods.py
Description: Submodule for SubModule-level CRUD operations in Super Admin.

Author: Akshay Basutkar, Siddharth Admal, Swarnim Deshpande
App: OneApp

"""

from pathlib import Path

# Anchor to <repo>/modules regardless of the process working directory.
MODULES_ROOT = Path(__file__).resolve().parents[1]


def _sync_manifest_submodules(manifest_path: Path, action: str, submod_key: str, new_submod_key: str = None):
    if not manifest_path.exists():
        return
    try:
        content = manifest_path.read_text(encoding="utf-8")
        import re

        match = re.search(r"SUPPORTED_SUBMODULES\s*=\s*\[(.*?)\]", content, re.DOTALL)
        if not match:
            return

        items = [i.strip().strip('"\'') for i in match.group(1).split(",") if i.strip()]

        if action == "add":
            if submod_key not in items:
                items.append(submod_key)
        elif action == "rename":
            items = [new_submod_key if i == submod_key else i for i in items]
        elif action == "remove":
            items = [i for i in items if i != submod_key]

        formatted_items = ",\n    ".join(f'"{i}"' for i in items)
        new_list_code = f"SUPPORTED_SUBMODULES = [\n    {formatted_items}\n]"
        new_content = re.sub(r"SUPPORTED_SUBMODULES\s*=\s*\[.*?\]", new_list_code, content, flags=re.DOTALL)
        manifest_path.write_text(new_content, encoding="utf-8")
    except Exception:
        pass


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


class SubMods:
    """
    Single submodule class handling submodule file lifecycle.
    """

    def __init__(self, modules_root: Path = None):
        self.modules_root = modules_root or MODULES_ROOT

    async def sub_mods(self, request_or_action_type, payload_or_context=None, context=None):
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
                    message=f"Unsupported actionType '{action_type}' for sub_mods"
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

        raw_mod = payload.get("mod_name") or ""
        clean_mod = raw_mod.replace("m_", "")

        raw_sub = payload.get("new_sub_mod_name") or payload.get("sub_mod_name") or ""
        clean_sub = raw_sub.replace("sm_", "")

        if not is_valid_name(clean_mod):
            return XSCUtility.error_response(message="Not a valid module name")

        if not is_valid_name(clean_sub):
            return XSCUtility.error_response(message="Not a valid subMod name")

        module_path = self.modules_root / f"m_{clean_mod}"
        sub_mod_path = module_path / f"m_{clean_mod}_sm_{clean_sub}.py"

        if not module_path.exists():
            return XSCUtility.error_response(message="Module does not exist")

        if sub_mod_path.exists():
            return XSCUtility.error_response(
                message="subMod already exists, choose another name"
            )

        pascal_sub = "".join(word.capitalize() for word in clean_sub.split("_") if word)
        
        submod_template = f'''"""
File: m_{clean_mod}_sm_{clean_sub}.py
Description: Submodule handler for sm_{clean_sub} in m_{clean_mod}.
"""

import logging
from typing import Dict, Any
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

logger = logging.getLogger(__name__)


class sm_{clean_sub}:
    @staticmethod
    async def {clean_sub}(request: Any, context: Any) -> Dict[str, Any]:
        action_type = (request.actionType or "").lower()
        match action_type:
            case "view" | "read":
                return await sm_{clean_sub}.view(request, context)
            case _:
                return XSCUtility.error_response(message=f"Unsupported actionType '{{action_type}}'")

    @staticmethod
    async def view(request: Any, context: Any) -> Dict[str, Any]:
        return XSCUtility.success_response(message="{pascal_sub} view executed successfully")
'''
        sub_mod_path.write_text(submod_template, encoding="utf-8")

        # Sync manifest.py
        _sync_manifest_submodules(module_path / "manifest.py", "add", f"sm_{clean_sub}")

        return XSCUtility.success_response(message=f"subMod 'sm_{clean_sub}' created successfully", code=200)

    def read(self, request_or_payload=None, context=None):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        payload, ctx = _extract_payload_ctx(request_or_payload, context)

        raw_mod = payload.get("mod_name") or ""
        clean_mod = raw_mod.replace("m_", "")
        mod_path = self.modules_root / f"m_{clean_mod}"

        if not mod_path.exists():
            return XSCUtility.error_response(message="Module doesn't exist")

        sub_mods_list = []
        prefix = f"m_{clean_mod}_"
        for file in mod_path.glob(f"m_{clean_mod}_sm_*.py"):
            sub_mod_name = file.stem.removeprefix(prefix).removeprefix("sm_")
            sub_mods_list.append(sub_mod_name)

        return XSCUtility.success_response(
            message="Returning the names of submods", list=sub_mods_list
        )

    def update(self, request_or_payload, context=None):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from xsc_lib.xsc_lib_common.xsc_libc_string_operations import is_valid_name
        payload, ctx = _extract_payload_ctx(request_or_payload, context)

        raw_mod = payload.get("mod_name") or ""
        clean_mod = raw_mod.replace("m_", "")

        old_sub = (payload.get("sub_mod_name") or "").replace("sm_", "")
        new_sub = (payload.get("new_name") or "").replace("sm_", "")

        if not (is_valid_name(clean_mod) and is_valid_name(old_sub) and is_valid_name(new_sub)):
            return XSCUtility.error_response(message="Invalid name(s)")

        module_path = self.modules_root / f"m_{clean_mod}"
        old_path = module_path / f"m_{clean_mod}_sm_{old_sub}.py"
        new_path = module_path / f"m_{clean_mod}_sm_{new_sub}.py"

        if not old_path.exists():
            return XSCUtility.error_response(
                message="subMod to be renamed doesn't exist"
            )

        if new_path.exists():
            return XSCUtility.error_response(message="Target subMod already exists")

        content = old_path.read_text(encoding="utf-8")
        content = content.replace(f"sm_{old_sub}", f"sm_{new_sub}")
        content = content.replace(f"def {old_sub}(", f"def {new_sub}(")

        old_path.rename(new_path)
        new_path.write_text(content, encoding="utf-8")

        # Sync manifest.py
        _sync_manifest_submodules(module_path / "manifest.py", "rename", f"sm_{old_sub}", f"sm_{new_sub}")

        return XSCUtility.success_response(message="subMod renamed successfully")

    def delete(self, request_or_payload, context=None):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        payload, ctx = _extract_payload_ctx(request_or_payload, context)

        raw_mod = payload.get("mod_name") or ""
        clean_mod = raw_mod.replace("m_", "")

        raw_sub = payload.get("sub_mod_name") or ""
        clean_sub = raw_sub.replace("sm_", "")

        mod_path = self.modules_root / f"m_{clean_mod}"

        if not mod_path.exists():
            return XSCUtility.error_response(message="Module does not exist")

        sub_mod_path = mod_path / f"m_{clean_mod}_sm_{clean_sub}.py"

        if not sub_mod_path.exists():
            return XSCUtility.error_response(message="Mentioned subMod doesn't exist")

        sub_mod_path.unlink()

        # Sync manifest.py
        _sync_manifest_submodules(mod_path / "manifest.py", "remove", f"sm_{clean_sub}")

        return XSCUtility.success_response(message="subMod deleted successfully")


# Class name aliases for ActionDispatcher resolution
sm_sub_mods = SubMods
