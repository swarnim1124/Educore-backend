"""
File: xsc_libc_context.py
Description: Framework Context objects for Execution and Security.

Author: Siddharth Amdal
App: OneApp

"""

from typing import Any, Dict, List, Optional
import time
from datetime import datetime


class SecurityContext:
    """
    Holds authenticated user information and validated JWT claims.
    """

    def __init__(
        self,
        user_id: str = None,
        institution_id: str = None,
        tenant_id: str = None,
        roles: List[str] = None,
        permissions: List[str] = None,
        jwt_claims: Dict[str, Any] = None,
    ):
        self.user_id = user_id
        self.institution_id = institution_id
        self.tenant_id = tenant_id
        self.roles = roles or []
        self.permissions = permissions or []
        self.jwt_claims = jwt_claims or {}


class ExecutionContext:
    """
    The canonical runtime context object shared across the framework.
    """

    def __init__(self, request_id: str, service_container: Any = None):
        self.request_id = request_id
        self.request_start_time = time.perf_counter()

        # Injected Services
        self._container = service_container

        # Security
        self.security: Optional[SecurityContext] = None

        # Extensibility
        self.locale: str = "en-US"
        self.timezone: str = "UTC"
        self.metadata: Dict[str, Any] = {}

        # Logging & Timing
        self.milestones: List[Dict[str, Any]] = []
        self._timers: Dict[str, float] = {}

    def add_milestone(self, event: str, details: Dict[str, Any] = None):
        """Records a structured execution milestone."""
        self.milestones.append(
            {
                "timestamp": time.perf_counter(),
                "time_iso": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                "event": event,
                "details": details or {},
            }
        )

    def start_timer(self, name: str):
        """Starts a timer for a specific execution block."""
        self._timers[name] = time.perf_counter()

    def stop_timer(self, name: str):
        """Stops a timer and records it as a milestone."""
        if name in self._timers:
            duration_ms = round((time.perf_counter() - self._timers[name]) * 1000, 2)
            self.add_milestone(
                event=f"TIMER_{name.upper()}", details={"duration_ms": duration_ms}
            )
            del self._timers[name]

    @property
    def logger(self):
        return self._container.resolve("Logger") if self._container else None

    @property
    def postgres(self):
        return self._container.resolve("PostgreSQLManager") if self._container else None

    @property
    def configuration(self):
        return self._container.resolve("Configuration") if self._container else None

    @property
    def cache(self):
        return self._container.resolve("Cache") if self._container else None
