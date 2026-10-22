"""
File: m_super_admin_sm_action_type.py
Description: Submodule for ActionType CRUD operations in Super Admin.

Author: EduCore
App: OneApp

"""

import ast
import re
from pathlib import Path
from typing import Any, Dict

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from xsc_lib.xsc_lib_common.xsc_libc_code_editor import CodeEditor
from xsc_lib.xsc_lib_common.xsc_libc_string_operations import is_valid_name

MODULES_ROOT = Path(__file__).resolve().parents[1]


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


class ActionType:
    """
    Single submodule class handling actionType CRUD code modifications inside submodule files.
    """

    def __init__(self, modules_root: Path = None):
        self.modules_root = modules_root or MODULES_ROOT

    def _get_sub_mod_path(self, mod_name: str, sub_mod_name: str) -> Path:
        clean_mod = (mod_name or "").replace("m_", "")
        clean_sub = (sub_mod_name or "").replace("sm_", "")
        return self.modules_root / f"m_{clean_mod}" / f"m_{clean_mod}_sm_{clean_sub}.py"

    async def action_type(self, request_or_action_type: Any, payload_or_context: Any = None, context: Any = None) -> Dict[str, Any]:
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
            case "read":
                return self.read(payload, actual_ctx)
            case "create" | "add":
                return self.create(payload, actual_ctx)
            case "update":
                return self.update(payload, actual_ctx)
            case "delete" | "remove":
                return self.delete(payload, actual_ctx)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for action_type"
                )

    # --- Public Action Handlers ---

    def read(self, request_or_payload: Any = None, context: Any = None) -> Dict[str, Any]:
        payload, ctx = _extract_payload_ctx(request_or_payload, context)
        mod_name = payload.get("mod_name")
        sub_mod_name = payload.get("sub_mod_name")

        if not mod_name or not sub_mod_name:
            return XSCUtility.error_response(
                message="mod_name and sub_mod_name are required"
            )

        file_path = self._get_sub_mod_path(mod_name, sub_mod_name)
        if not file_path.exists():
            return XSCUtility.error_response(message="subMod file does not exist")

        source = file_path.read_text(encoding="utf-8")

        # 1. Parse AST to find match case branches in actionType dispatchers
        action_types = set()
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Match):
                    for case in node.cases:
                        pattern = case.pattern
                        if isinstance(pattern, ast.MatchValue):
                            if isinstance(pattern.value, ast.Constant) and isinstance(pattern.value.value, str):
                                action_types.add(pattern.value.value)
                        elif isinstance(pattern, ast.MatchOr):
                            for alt in pattern.patterns:
                                if isinstance(alt, ast.MatchValue) and isinstance(alt.value, ast.Constant) and isinstance(alt.value.value, str):
                                    action_types.add(alt.value.value)
        except Exception:
            pass

        # 2. Regex fallback if AST match extraction yields nothing
        if not action_types:
            matches = re.findall(r'case\s+["\']([^"\']+)["\']', source)
            action_types.update([m for m in matches if m != "_"])

        return XSCUtility.success_response(
            message="ActionTypes retrieved successfully",
            action_types=sorted(list(action_types)),
        )

    def create(self, request_or_payload: Any = None, context: Any = None) -> Dict[str, Any]:
        payload, ctx = _extract_payload_ctx(request_or_payload, context)
        mod_name = payload.get("mod_name")
        sub_mod_name = payload.get("sub_mod_name")
        action_type_name = payload.get("action_type_name") or payload.get("action_type")

        if not mod_name or not sub_mod_name or not action_type_name:
            return XSCUtility.error_response(
                message="mod_name, sub_mod_name, and action_type_name are required"
            )

        clean_type = action_type_name.lower().strip()
        handler_name = clean_type.replace("-", "_").replace(" ", "_")
        if not is_valid_name(handler_name):
            return XSCUtility.error_response(message="Invalid actionType name")

        file_path = self._get_sub_mod_path(mod_name, sub_mod_name)
        if not file_path.exists():
            return XSCUtility.error_response(message="subMod file does not exist")

        source = file_path.read_text(encoding="utf-8")

        # Check if actionType already exists in source
        if f'case "{clean_type}"' in source or f"case '{clean_type}'" in source:
            return XSCUtility.error_response(
                message=f"ActionType '{clean_type}' already exists in subMod"
            )

        # 1. Append handler method using CodeEditor
        try:
            editor = CodeEditor(file_path)
            pascal_type = "".join(word.capitalize() for word in clean_type.split("_") if word)
            body_code = f"return XSCUtility.success_response(message='{pascal_type} actionType executed successfully')"
            editor.create_method(
                method_name=handler_name,
                parameters=["request", "context"],
                docstring=f"Handler for actionType '{clean_type}'",
                body=body_code,
            )
            editor.save()
        except ValueError as e:
            if "already exists" not in str(e):
                return XSCUtility.error_response(message=str(e))

        # 2. Inject case branch into match block
        source = file_path.read_text(encoding="utf-8")
        if f'case "{clean_type}"' not in source and f"case '{clean_type}'" not in source:
            lines = source.splitlines()
            new_lines = []
            case_inserted = False
            for line in lines:
                if not case_inserted and re.match(r"^\s*case\s+(_|[\"\'])", line):
                    indent_len = len(line) - len(line.lstrip())
                    ind = " " * indent_len
                    body_ind = " " * (indent_len + 4)
                    clean_sub = sub_mod_name.replace("m_", "").replace("sm_", "")
                    new_lines.append(f'{ind}case "{clean_type}":')
                    new_lines.append(f'{body_ind}return await sm_{clean_sub}.{handler_name}(request, context)')
                    case_inserted = True
                new_lines.append(line)

            if case_inserted:
                file_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

        return XSCUtility.success_response(
            message=f"ActionType '{clean_type}' created successfully"
        )

    def update(self, request_or_payload: Any = None, context: Any = None) -> Dict[str, Any]:
        payload, ctx = _extract_payload_ctx(request_or_payload, context)
        mod_name = payload.get("mod_name")
        sub_mod_name = payload.get("sub_mod_name")
        old_type = (payload.get("action_type_name") or payload.get("old_name") or "").lower().strip()
        new_type = (payload.get("new_name") or payload.get("new_action_type_name") or "").lower().strip()

        if not mod_name or not sub_mod_name or not old_type or not new_type:
            return XSCUtility.error_response(
                message="mod_name, sub_mod_name, old_name/action_type_name, and new_name are required"
            )

        file_path = self._get_sub_mod_path(mod_name, sub_mod_name)
        if not file_path.exists():
            return XSCUtility.error_response(message="subMod does not exist")

        old_handler = old_type.replace("-", "_").replace(" ", "_")
        new_handler = new_type.replace("-", "_").replace(" ", "_")

        # 1. Rename handler method
        try:
            editor = CodeEditor(file_path)
            editor.rename_method(old_name=old_handler, new_name=new_handler)
            editor.save()
        except ValueError:
            pass

        # 2. Rename in source
        source = file_path.read_text(encoding="utf-8")
        source = source.replace(f'case "{old_type}"', f'case "{new_type}"')
        source = source.replace(f"case '{old_type}'", f"case '{new_type}'")
        source = source.replace(f".{old_handler}(", f".{new_handler}(")
        file_path.write_text(source, encoding="utf-8")

        return XSCUtility.success_response(
            message=f"ActionType renamed from '{old_type}' to '{new_type}' successfully"
        )

    def delete(self, request_or_payload: Any = None, context: Any = None) -> Dict[str, Any]:
        payload, ctx = _extract_payload_ctx(request_or_payload, context)
        mod_name = payload.get("mod_name")
        sub_mod_name = payload.get("sub_mod_name")
        type_to_delete = (payload.get("action_type_name") or payload.get("action_type") or "").lower().strip()

        if not mod_name or not sub_mod_name or not type_to_delete:
            return XSCUtility.error_response(
                message="mod_name, sub_mod_name, and action_type_name are required"
            )

        file_path = self._get_sub_mod_path(mod_name, sub_mod_name)
        if not file_path.exists():
            return XSCUtility.error_response(message="subMod does not exist")

        handler_name = type_to_delete.replace("-", "_").replace(" ", "_")

        # 1. Delete handler method if exists
        try:
            editor = CodeEditor(file_path)
            editor.delete_method(method_name=handler_name)
            editor.save()
        except ValueError:
            pass

        # 2. Remove case block cleanly from match statement
        source = file_path.read_text(encoding="utf-8")
        lines = source.splitlines()
        new_lines = []
        skip_next = False

        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
            if re.search(rf'case\s+["\']{re.escape(type_to_delete)}["\']:', line):
                if i + 1 < len(lines) and ("return " in lines[i + 1] or "pass" in lines[i + 1]):
                    skip_next = True
                continue
            new_lines.append(line)

        file_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

        return XSCUtility.success_response(
            message=f"ActionType '{type_to_delete}' deleted successfully"
        )


# Class name aliases for ActionDispatcher resolution
sm_action_type = ActionType
