"""
File: xsc_libc_exceptions.py
Description: Centralized framework exceptions for OneApp.

Author: Siddharth Amdal
App: OneApp

"""

from typing import Any, Dict, Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from xsc_lib.xsc_lib_common.xsc_libc_logger import XSCLogger


class OneAppException(Exception):
    """
    Base exception for all OneApp specific errors.
    """

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class FrameworkException(OneAppException):
    """
    Exception thrown by framework internals.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code="FWK500", message=message, status_code=500, details=details
        )


class ModuleNotFoundException(FrameworkException):
    def __init__(self, target: str):
        super().__init__(
            message=f"Module or Submodule not found: {target}",
            details={"target": target},
        )
        self.error_code = "FWK404"
        self.status_code = 404


class InvalidActionException(FrameworkException):
    def __init__(self, target: str):
        super().__init__(
            message=f"Invalid action or actionType: {target}",
            details={"target": target},
        )
        self.error_code = "FWK400"
        self.status_code = 400


class AuthorizationException(OneAppException):
    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            error_code="ERR403", message=message, status_code=403, details=details
        )


# Global Exception Handlers for FastAPI
async def oneapp_exception_handler(request: Request, exc: OneAppException):
    XSCLogger.error(
        f"OneAppException [{exc.error_code}]: {exc.message}",
        metadata={"path": request.url.path, "details": exc.details},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=XSCUtility.error_response(
            message=exc.message, error_code=exc.error_code
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception):
    XSCLogger.error(
        f"Unhandled Exception: {str(exc)}", metadata={"path": request.url.path}, exc=exc
    )
    return JSONResponse(
        status_code=500,
        content=XSCUtility.error_response(
            message="An internal server error occurred.", error_code="ERR500"
        ),
    )
