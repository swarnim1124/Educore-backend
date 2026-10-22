"""
File: xsc_liba_events.py
Description: Framework Event infrastructure for OneApp.

Author: Siddharth Amdal
App: OneApp

"""

from typing import Any, Callable, Dict, List
from xsc_lib.xsc_lib_common.xsc_libc_context import ExecutionContext


class FrameworkEvents:
    """
    Event publishing infrastructure.
    Events notify the framework that something occurred.
    """

    _listeners: Dict[str, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_name: str, callback: Callable) -> None:
        """
        Subscribe a callback to a framework event.
        """
        if event_name not in cls._listeners:
            cls._listeners[event_name] = []
        cls._listeners[event_name].append(callback)

    @classmethod
    async def publish(
        cls, event_name: str, context: ExecutionContext, payload: Any = None
    ) -> None:
        """
        Publish an event, asynchronously executing all registered callbacks.
        """
        if event_name in cls._listeners:
            for callback in cls._listeners[event_name]:
                try:
                    await callback(context, payload)
                except Exception as _e:
                    if context.logger:
                        context.logger.error(
                            f"Error executing event listener for {event_name}", exc=e
                        )
