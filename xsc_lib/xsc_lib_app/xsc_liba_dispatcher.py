"""
File: xsc_liba_dispatcher.py
Description: Central Action Dispatcher orchestration engine for OneApp Framework.

Author: Siddharth Amdal
App: OneApp

"""

from typing import Any
from xsc_lib.xsc_lib_common.xsc_libc_context import ExecutionContext
from xsc_lib.xsc_lib_common.xsc_libc_models import OneAppRequest
from xsc_lib.xsc_lib_common.xsc_libc_exceptions import (
    FrameworkException,
    InvalidActionException,
    OneAppException,
)
from xsc_lib.xsc_lib_app.xsc_liba_events import FrameworkEvents
from xsc_lib.xsc_lib_app.xsc_liba_hooks import FrameworkHooks


class ActionDispatcher:
    """
    Orchestration engine of the framework.
    Responsibilities: Module resolution, context injection, hook execution, event publishing, exception translation, response formatting.
    """

    @classmethod
    async def dispatch(cls, request: OneAppRequest, context: ExecutionContext) -> Any:
        try:
            from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
            from xsc_lib.xsc_lib_app.xsc_liba_module_loader import ModuleLoader

            request.mod = ModuleLoader._resolve_mod_dir(request.mod)
            request.subMod = XSCUtility.to_snake_case(request.subMod)

            if context.logger:
                context.logger.api(
                    event="DISP001",
                    message=f"Dispatching Request: {request.mod}.{request.subMod}.{request.action}.{request.actionType}",
                    metadata={
                        "module": request.mod,
                        "submodule": request.subMod,
                        "action": request.action,
                    },
                )

            # Framework Event
            await FrameworkEvents.publish("BeforeDispatch", context, request)

            # Resolve Action Function
            context.start_timer("module_resolution")
            action_func = ModuleLoader.load_action(
                request.mod, request.subMod, request.action
            )
            context.stop_timer("module_resolution")

            context.add_milestone(
                event="MODULE_RESOLVED",
                details={
                    "module": request.mod,
                    "submodule": request.subMod,
                    "action": request.action,
                },
            )

            if not callable(action_func):
                raise InvalidActionException(
                    target=f"Action '{request.action}' is not callable"
                )

            # Lifecycle Hook: before_dispatch
            mutated_request = await FrameworkHooks.execute_hook(
                "before_dispatch", request, context, request
            )

            # Execute Business Logic
            context.start_timer("action_execution")
            import inspect, asyncio

            if inspect.iscoroutinefunction(action_func) or asyncio.iscoroutinefunction(
                action_func
            ):
                try:
                    result = await action_func(mutated_request, context)
                except TypeError as e:
                    if "positional argument" in str(e) or "required" in str(e):
                        result = await action_func(
                            mutated_request.actionType, mutated_request.payload, context
                        )
                    else:
                        raise
            else:
                try:
                    res_or_coro = action_func(mutated_request, context)
                    if inspect.isawaitable(res_or_coro):
                        result = await res_or_coro
                    else:
                        result = res_or_coro
                except TypeError as e:
                    if "positional argument" in str(e) or "required" in str(e):
                        res_or_coro = action_func(
                            mutated_request.actionType, mutated_request.payload, context
                        )
                        if inspect.isawaitable(res_or_coro):
                            result = await res_or_coro
                        else:
                            result = res_or_coro
                    else:
                        raise
            context.stop_timer("action_execution")

            context.add_milestone(
                event="ACTION_EXECUTED", details={"action": request.action}
            )

            # Format Response if it isn't already formatted by XSCUtility
            # (Assuming business logic returns dict wrapped in XSCUtility.success_response)
            if not isinstance(result, dict) or "status" not in result:
                result = XSCUtility.success_response(
                    message="Operation successful", data=result
                )

            # Lifecycle Hook: after_dispatch
            result = await FrameworkHooks.execute_hook(
                "after_dispatch", mutated_request, context, result
            )

            # Framework Event
            await FrameworkEvents.publish("AfterDispatch", context, result)

            context.add_milestone(event="RESPONSE_GENERATED", details=result)

            return result

        except OneAppException as e:
            # Re-raise standard framework/module exceptions (handled by middleware)
            raise
        except Exception as e:
            if context.logger:
                context.logger.error(
                    f"Execution failed for {request.mod}.{request.subMod}.{request.action}",
                    exc=e,
                )
            # Translate raw exceptions into FrameworkException
            raise FrameworkException(
                "Internal framework execution error.", details={"error": str(e)}
            )
