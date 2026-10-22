"""
File: m_super_admin_sm_action.py
Description: Submodule for Action-level CRUD and introspection in Super Admin.

Author: Akshay Basutkar, Siddharth Admal, Swarnim Deshpande, Siddharth Amdal.
App: OneApp

"""

from pathlib import Path

# Anchor to <repo>/modules regardless of the process working directory.
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


class Action:
    """
    Single submodule class handling action method introspection and code generation.
    """

    def __init__(self, modules_root: Path = None):
        self.modules_root = modules_root or MODULES_ROOT

    def _get_sub_mod_path(self, mod_name: str, sub_mod_name: str) -> Path:
        clean_mod = (mod_name or "").replace("m_", "")
        clean_sub = (sub_mod_name or "").replace("sm_", "")
        return self.modules_root / f"m_{clean_mod}" / f"m_{clean_mod}_sm_{clean_sub}.py"

    async def action(self, request_or_action_type, payload_or_context=None, context=None):
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
            case "read":
                return self.read(payload, actual_ctx)
            case "create":
                return self.create(payload, actual_ctx)
            case "update":
                return self.update(payload, actual_ctx)
            case "delete":
                return self.delete(payload, actual_ctx)
            case _:
                return XSCUtility.error_response(
                    message=f"Unsupported actionType '{action_type}' for action"
                )

    # --- Public Action Handlers ---

    def read(self, request_or_payload, context=None):
        import sys
        from importlib import import_module
        from inspect import getmembers, isclass
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        payload, ctx = _extract_payload_ctx(request_or_payload, context)

        mod = payload.get("mod_name")
        sub_mod = payload.get("sub_mod_name")

        if not mod or not sub_mod:
            return XSCUtility.error_response(
                message="mod_name and sub_mod_name are required"
            )

        file_path = self._get_sub_mod_path(mod, sub_mod)
        if not file_path.exists():
            return XSCUtility.error_response(message="subMod does not exist")

        clean_mod = mod.replace("m_", "")
        clean_sub = sub_mod.replace("sm_", "")
        module_name = f"modules.m_{clean_mod}.m_{clean_mod}_sm_{clean_sub}"

        try:
            sys.modules.pop(module_name, None)
            module = import_module(module_name)
            classes = [
                cls
                for name, cls in getmembers(module, isclass)
                if cls.__module__ == module.__name__
            ]
            if classes:
                cls = classes[0]
                actions = [
                    name
                    for name, member in getmembers(cls, predicate=callable)
                    if not name.startswith("_")
                ]
                return XSCUtility.success_response(
                    message="Operation successful", action_list=actions
                )
        except Exception:
            pass

        # AST Fallback parsing if module cannot be imported directly
        import ast
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            actions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for body_node in node.body:
                        if isinstance(body_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if not body_node.name.startswith("_"):
                                actions.append(body_node.name)
            return XSCUtility.success_response(
                message="Operation successful", action_list=actions
            )
        except Exception as e:
            return XSCUtility.error_response(message=f"Could not inspect subMod: {e}")

    def create(self, request_or_payload, context=None):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from xsc_lib.xsc_lib_common.xsc_libc_code_editor import CodeEditor
        payload, ctx = _extract_payload_ctx(request_or_payload, context)

        mod_name = payload.get("mod_name")
        sub_mod_name = payload.get("sub_mod_name")
        action_name = payload.get("action_name")
        parameters = payload.get("parameters") or ["request", "context"]
        body = payload.get("body") or "return XSCUtility.success_response(message='Action executed')"
        docstring = payload.get("docstring") or f"Action handler for {action_name}"

        file_path = self._get_sub_mod_path(mod_name, sub_mod_name)

        if not file_path.exists():
            return XSCUtility.error_response(message="subMod does not exist")

        try:
            editor = CodeEditor(file_path)
            editor.create_method(
                method_name=action_name,
                parameters=parameters,
                docstring=docstring,
                body=body,
            )
            editor.save()
            return XSCUtility.success_response(message="Action created successfully")
        except ValueError as e:
            return XSCUtility.error_response(message=str(e))

    def update(self, request_or_payload, context=None):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from xsc_lib.xsc_lib_common.xsc_libc_code_editor import CodeEditor
        payload, ctx = _extract_payload_ctx(request_or_payload, context)

        mod_name = payload.get("mod_name")
        sub_mod_name = payload.get("sub_mod_name")
        action_name = payload.get("action_name")
        new_name = payload.get("new_name")

        file_path = self._get_sub_mod_path(mod_name, sub_mod_name)

        if not file_path.exists():
            return XSCUtility.error_response(message="subMod does not exist")

        try:
            editor = CodeEditor(file_path)
            editor.rename_method(old_name=action_name, new_name=new_name)
            editor.save()
            return XSCUtility.success_response(message="Action renamed successfully")
        except ValueError as e:
            return XSCUtility.error_response(message=str(e))

    def delete(self, request_or_payload, context=None):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
        from xsc_lib.xsc_lib_common.xsc_libc_code_editor import CodeEditor
        payload, ctx = _extract_payload_ctx(request_or_payload, context)

        mod_name = payload.get("mod_name")
        sub_mod_name = payload.get("sub_mod_name")
        action_to_delete = payload.get("action_name")

        file_path = self._get_sub_mod_path(mod_name, sub_mod_name)

        if not file_path.exists():
            return XSCUtility.error_response(message="subMod does not exist")

        try:
            editor = CodeEditor(file_path)
            editor.delete_method(method_name=action_to_delete)
            editor.save()
            return XSCUtility.success_response(message="Action deleted successfully")
        except ValueError as e:
            return XSCUtility.error_response(message=str(e))


# Class name aliases for ActionDispatcher resolution
sm_action = Action
