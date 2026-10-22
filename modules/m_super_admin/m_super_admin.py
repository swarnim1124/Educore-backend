"""
File: m_super_admin.py
Description: Dynamic Module Entry Router for m_super_admin.

Author: Akshay Basutkar, Siddharth Admal, Swarnim Deshpande.
App: OneApp

"""

import importlib
import asyncio


def to_pascal_case(s: str) -> str:
    """Converts a snake_case string to PascalCase."""
    return "".join(word.capitalize() for word in s.split("_") if word)


class SuperAdmin:
    """
    Entry point for m_super_admin module.
    Delegates action dispatching to OneApp Framework ActionDispatcher.
    """

    async def super_admin(self, request, context):
        from xsc_lib.xsc_lib_app.xsc_liba_dispatcher import ActionDispatcher

        return await ActionDispatcher.dispatch(request, context)

    def __call__(self, req_json_obj, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        sub_mod = XSCUtility.to_snake_case(
            req_json_obj.get("subMod")
            if isinstance(req_json_obj, dict)
            else getattr(req_json_obj, "subMod", "")
        )
        action = (
            req_json_obj.get("action")
            if isinstance(req_json_obj, dict)
            else getattr(req_json_obj, "action", "")
        )
        action_type = (
            req_json_obj.get("actionType")
            if isinstance(req_json_obj, dict)
            else getattr(req_json_obj, "actionType", "")
        )
        payload = (
            req_json_obj.get("payload", {})
            if isinstance(req_json_obj, dict)
            else getattr(req_json_obj, "payload", {})
        )

        if not sub_mod or not action or not action_type:
            return XSCUtility.error_response(
                message="Missing 'subMod', 'action', or 'actionType'"
            )

        sm_sub_mod = sub_mod if sub_mod.startswith("sm_") else f"sm_{sub_mod}"

        try:
            sub_module_path = f".m_super_admin_{sm_sub_mod}"
            try:
                module = importlib.import_module(sub_module_path, package=__package__)
            except ImportError:
                alt_path = f".m_super_admin_sm_{sub_mod.replace('sm_', '')}"
                module = importlib.import_module(alt_path, package=__package__)

            clean_sub_mod = sub_mod.replace("sm_", "")
            class_name = to_pascal_case(clean_sub_mod)
            module_class = getattr(module, class_name, None)

            if not module_class:
                module_class = getattr(module, action, None) or getattr(
                    module, to_pascal_case(action), None
                )

            if not module_class:
                return XSCUtility.error_response(
                    message=f"Class for subMod '{sub_mod}' not found in {sub_module_path}"
                )

            instance = module_class()
            action_func = (
                getattr(instance, action, None)
                or getattr(instance, clean_sub_mod, None)
                or getattr(instance, "execute", None)
            )

            if not action_func:
                return XSCUtility.error_response(
                    message=f"Action method '{action}' not found on class '{class_name}'"
                )

            if asyncio.iscoroutinefunction(action_func):
                return asyncio.run(action_func(action_type, payload, context))
            return action_func(action_type, payload, context)

        except ImportError as e:
            return XSCUtility.error_response(
                message=f"Submodule file not found for subMod '{sub_mod}'. Details: {str(e)}"
            )
        except Exception as e:
            return XSCUtility.error_response(
                message=f"Execution error in m_super_admin: {str(e)}"
            )
