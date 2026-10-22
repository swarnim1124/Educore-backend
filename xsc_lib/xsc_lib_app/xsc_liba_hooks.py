"""
File: xsc_liba_hooks.py
Description: Framework Lifecycle Hooks for OneApp.

Author: Siddharth Amdal
App: OneApp

"""

from typing import Any, Callable, Dict, List
from xsc_lib.xsc_lib_common.xsc_libc_context import ExecutionContext
from xsc_lib.xsc_lib_common.xsc_libc_models import OneAppRequest


class FrameworkHooks:
    """
    Lifecycle extension points that modify framework execution.
    Dispatcher invokes these hooks only if implemented.
    """

    _hooks: Dict[str, List[Callable]] = {}

    @classmethod
    def register(cls, hook_name: str, callback: Callable) -> None:
        """
        Register a callback for a specific lifecycle hook.
        Available hooks: before_dispatch, after_dispatch, before_commit, after_commit, before_response, after_response.
        """
        if hook_name not in cls._hooks:
            cls._hooks[hook_name] = []
        cls._hooks[hook_name].append(callback)

    @classmethod
    async def execute_hook(
        cls,
        hook_name: str,
        request: OneAppRequest,
        context: ExecutionContext,
        payload: Any = None,
    ) -> Any:
        """
        Execute all registered callbacks for a hook sequentially.
        If a hook returns a mutated payload, it is passed to the next hook.
        """
        current_payload = payload
        if hook_name in cls._hooks:
            for callback in cls._hooks[hook_name]:
                try:
                    # Hooks might mutate the payload or context
                    result = await callback(request, context, current_payload)
                    if result is not None:
                        current_payload = result
                except Exception as _e:
                    if context.logger:
                        context.logger.error(
                            f"Error executing hook '{hook_name}'", exc=e
                        )
                    # We might want to halt execution depending on the hook, but for now we log and proceed
                    raise
        return current_payload
