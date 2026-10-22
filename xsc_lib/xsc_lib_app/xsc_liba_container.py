"""
File: xsc_liba_container.py
Description: Dependency Injection Container for OneApp Framework infrastructure.

Author: Siddharth Amdal
App: OneApp

"""

from typing import Any, Dict


class ServiceContainer:
    """
    Central registry for framework-level infrastructure dependencies.
    """

    _services: Dict[str, Any] = {}

    @classmethod
    def register(cls, name: str, service: Any) -> None:
        """
        Register an infrastructure service.
        """
        cls._services[name] = service

    @classmethod
    def resolve(cls, name: str) -> Any:
        """
        Resolve an infrastructure service by name.
        """
        return cls._services.get(name)

    @classmethod
    def has(cls, name: str) -> bool:
        """
        Check if a service is registered.
        """
        return name in cls._services

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Remove a service from the registry.
        """
        if name in cls._services:
            del cls._services[name]
