"""
File: m_profile.py
Description: Dynamic Module Entry Router for m_profile.

Author: EduCore
App: OneApp

"""

import importlib
import asyncio


class Profile:
    """
    Dynamic entry point router for the Profile module.
    Delegates incoming requests to their respective submodule files and classes.
    """

    def __call__(self, req_json_obj, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

        sub_mod = XSCUtility.to_snake_case(req_json_obj.get("subMod"))
        action = req_json_obj.get("action")
        action_type = req_json_obj.get("actionType")

        if not sub_mod or not action or not action_type:
            return XSCUtility.error_response(
                message="Missing 'subMod', 'action', or 'actionType'"
            )

        print(f"[m_profile.py] Routing to submodule: {sub_mod}, action: {action}")

        try:
            # 1. Resolve submodule file (e.g. .m_profile_sm_personal_detail)
            sub_mod_snake = XSCUtility.to_snake_case(sub_mod)
            sm_sub_mod_snake = (
                sub_mod_snake
                if sub_mod_snake.startswith("sm_")
                else f"sm_{sub_mod_snake}"
            )

            sub_module_path = f".m_profile_{sm_sub_mod_snake}"

            try:
                module = importlib.import_module(sub_module_path, package=__package__)
            except ImportError:
                # Fallback check
                try:
                    alt_path = f".m_profile_{sub_mod}"
                    module = importlib.import_module(alt_path, package=__package__)
                except ImportError:
                    raise

            # 2. Resolve class (try sm_snake, exact action name, PascalCase of sub_mod, or PascalCase of action)
            class_name = sm_sub_mod_snake
            module_class = getattr(module, sm_sub_mod_snake, None)

            if not module_class:
                class_name = action
                module_class = getattr(module, action, None)

            if not module_class:
                class_name = XSCUtility.to_pascal_case(sub_mod_snake.replace("sm_", ""))
                module_class = getattr(module, class_name, None)

            if not module_class:
                class_name = XSCUtility.to_pascal_case(action)
                module_class = getattr(module, class_name, None)

            if not module_class:
                return XSCUtility.error_response(
                    message=f"Class for action '{action}' not found in {sub_module_path}"
                )

            instance = module_class()

            # 3. Resolve execution method (try execute() first, then method matching action name)
            action_func = getattr(instance, "execute", None)
            if not action_func:
                action_func = getattr(instance, action, None)

            if not action_func:
                target_cls_name = getattr(module_class, "__name__", class_name)
                return XSCUtility.error_response(
                    message=f"Action method for '{action}' not found on class '{target_cls_name}'"
                )

            # 4. Execute action
            from xsc_lib.xsc_lib_common.xsc_libc_models import OneAppRequest

            if isinstance(req_json_obj, dict):
                req_obj = OneAppRequest(
                    app=req_json_obj.get("app", "OneApp"),
                    mod=req_json_obj.get("mod", "m_profile"),
                    subMod=sub_mod,
                    action=action,
                    actionType=action_type,
                    payload=req_json_obj.get("payload", {}),
                )
            else:
                req_obj = req_json_obj

            if asyncio.iscoroutinefunction(action_func):
                def _run_async(coro):
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = None

                    if loop and loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                            return pool.submit(asyncio.run, coro).result()
                    else:
                        return asyncio.run(coro)

                try:
                    return _run_async(action_func(req_obj, context))
                except TypeError:
                    payload = (
                        req_json_obj.get("payload", {})
                        if isinstance(req_json_obj, dict)
                        else getattr(req_json_obj, "payload", {})
                    )
                    return _run_async(action_func(action_type, payload, context))
            else:
                try:
                    return action_func(req_obj, context)
                except TypeError:
                    payload = (
                        req_json_obj.get("payload", {})
                        if isinstance(req_json_obj, dict)
                        else getattr(req_json_obj, "payload", {})
                    )
                    return action_func(action_type, payload, context)

        except ImportError as e:
            return XSCUtility.error_response(
                message=f"Submodule file not found for subMod '{sub_mod}'. Details: {str(e)}"
            )
        except Exception as e:
            return XSCUtility.error_response(
                message=f"Execution error in m_profile: {str(e)}"
            )
