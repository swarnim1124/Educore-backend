"""
File: xsc_libc_logger.py
Description: OneApp Centralized Logging Framework

Author: Siddharth Amdal
App: OneApp

"""

import logging
import json
import traceback
import os
from datetime import datetime
from typing import Any, Dict, Optional

# Standard Logger Names
LOG_APP = "app"
LOG_API = "api"
LOG_AUDIT = "audit"
LOG_SECURITY = "security"
LOG_DB = "db"
LOG_JOB = "job"
LOG_PERF = "per"
LOG_ERROR = "error"


class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs in structured JSON format with optional indentation."""

    def __init__(self, indent: Optional[int] = 2):
        super().__init__()
        self.indent = indent

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "category": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "event") and record.event:
            log_obj["event"] = record.event

        if hasattr(record, "metadata") and record.metadata is not None:
            if isinstance(record.metadata, dict):
                for k, v in record.metadata.items():
                    if k not in log_obj:
                        log_obj[k] = v
            else:
                log_obj["metadata"] = record.metadata

        if record.exc_info and record.exc_info[0] is not None:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, indent=self.indent, default=str)


class XSCLogger:
    """
    Centralized OneApp Logger wrapper.
    Internally uses standard Python logging framework while exposing
    a consistent, standardized API for all OneApp modules.
    """

    _initialized = False

    @classmethod
    def configure(
        cls,
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        indent: Optional[int] = 2,
    ):
        """
        Configures the root logger. Called once at application startup.
        """
        if cls._initialized:
            return

        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Clear existing handlers
        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JSONFormatter(indent=indent))
        root_logger.addHandler(console_handler)

        # File Handler (Optional)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(JSONFormatter(indent=indent))
            root_logger.addHandler(file_handler)

        # Set up request and error specific loggers
        try:
            os.makedirs("logs", exist_ok=True)
        except Exception:
            pass

        req_logger = logging.getLogger("oneapp.request")
        req_logger.setLevel(logging.INFO)
        req_logger.propagate = False
        try:
            req_handler = logging.FileHandler("logs/oneapp_requests.log")
        except (PermissionError, OSError):
            req_handler = logging.StreamHandler()
        req_handler.setFormatter(JSONFormatter(indent=indent))
        req_logger.addHandler(req_handler)

        err_logger = logging.getLogger("oneapp.error")
        err_logger.setLevel(logging.ERROR)
        err_logger.propagate = False
        try:
            err_handler = logging.FileHandler("logs/oneapp_errors.log")
        except (PermissionError, OSError):
            err_handler = logging.StreamHandler()
        err_handler.setFormatter(JSONFormatter(indent=indent))
        err_logger.addHandler(err_handler)

        cls._initialized = True

    @classmethod
    def _get_logger(cls, category: str) -> logging.Logger:
        return logging.getLogger(category)

    @classmethod
    def _log(
        cls,
        category: str,
        level: int,
        message: str,
        event: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ):
        if not cls._initialized:
            cls.configure()

        logger = cls._get_logger(category)
        extra = {"metadata": metadata} if metadata else {}
        if event:
            extra["event"] = event
        logger.log(level, message, extra=extra, exc_info=exc_info)

    # --- Specific Category Loggers ---

    @classmethod
    def app(
        cls,
        message: str,
        event: Optional[str] = None,
        level: int = logging.INFO,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """General application logic logs"""
        cls._log(LOG_APP, level, message, event, metadata)

    @classmethod
    def api(
        cls,
        message: str,
        event: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """API request/response lifecycle logs"""
        cls._log(LOG_API, logging.INFO, message, event, metadata)

    @classmethod
    def audit(
        cls,
        message: str,
        event: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Business action audit trails"""
        cls._log(LOG_AUDIT, logging.INFO, message, event, metadata)

    @classmethod
    def security(
        cls,
        message: str,
        event: Optional[str] = None,
        level: int = logging.WARNING,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Authentication, authorization, and security event logs"""
        cls._log(LOG_SECURITY, level, message, event, metadata)

    @classmethod
    def db(
        cls,
        message: str,
        event: Optional[str] = None,
        level: int = logging.DEBUG,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Database queries, connections, and transaction logs"""
        cls._log(LOG_DB, level, message, event, metadata)

    @classmethod
    def job(
        cls,
        message: str,
        event: Optional[str] = None,
        level: int = logging.INFO,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Background job / scheduler logs"""
        cls._log(LOG_JOB, level, message, event, metadata)

    @classmethod
    def perf(
        cls,
        message: str,
        event: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Performance and timing metrics"""
        cls._log(LOG_PERF, logging.INFO, message, event, metadata)

    @classmethod
    def error(
        cls,
        message: str,
        event: Optional[str] = None,
        exc: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Application errors and unhandled exceptions"""
        # Always log to ERROR level, include stack trace if exception is passed
        cls._log(LOG_ERROR, logging.ERROR, message, event, metadata, exc_info=bool(exc))

    @classmethod
    def log_request(
        cls,
        request_id: str,
        request_data: Dict[str, Any],
        result_data: Dict[str, Any],
        milestones: list,
        security=None,
    ):
        if not cls._initialized:
            cls.configure()

        user_id = (
            security.user_id
            if security and getattr(security, "user_id", None)
            else "Anonymous"
        )
        institution_id = (
            security.institution_id
            if security and getattr(security, "institution_id", None)
            else None
        )

        method = request_data.get("method", "UNKNOWN")
        path = request_data.get("path", "UNKNOWN")
        mod = request_data.get("mod", "UNKNOWN")
        sub_mod = request_data.get("subMod", "UNKNOWN")
        action = request_data.get("action", "UNKNOWN")
        action_type = request_data.get("actionType", "UNKNOWN")

        timeline = []
        for ms in milestones:
            timeline.append(
                {
                    "time_iso": ms.get("time_iso", ""),
                    "event": ms.get("event", "UNKNOWN_EVENT"),
                    "details": ms.get("details", {}),
                }
            )

        payload = {
            "request_id": request_id,
            "user": {"user_id": user_id, "institution_id": institution_id},
            "request": {
                "method": method,
                "path": path,
                "mod": mod,
                "subMod": sub_mod,
                "action": action,
                "actionType": action_type,
            },
            "execution_timeline": timeline,
            "result": {
                "status": result_data.get("status", "UNKNOWN"),
                "http_code": result_data.get("http_code", "UNKNOWN"),
                "duration_ms": result_data.get("duration_ms", 0),
            },
        }

        if "request_body" in request_data:
            payload["request"]["request_body"] = request_data["request_body"]

        if "response" in result_data:
            payload["result"]["response"] = result_data["response"]

        msg = f"Request completed: {method} {path} [{mod}/{sub_mod}/{action}] - HTTP {result_data.get('http_code', 'UNKNOWN')}"
        cls._log("oneapp.request", logging.INFO, msg, metadata=payload)

    @classmethod
    def log_error(
        cls,
        request_id: str,
        request_data: Dict[str, Any],
        exc: Exception,
        last_milestone: str,
        security=None,
        response: Optional[Dict[str, Any]] = None,
    ):
        if not cls._initialized:
            cls.configure()

        user_id = (
            security.user_id
            if security and getattr(security, "user_id", None)
            else "Anonymous"
        )
        institution_id = (
            security.institution_id
            if security and getattr(security, "institution_id", None)
            else None
        )

        op = f"{request_data.get('mod', 'UNKNOWN')} / {request_data.get('subMod', 'UNKNOWN')} / {request_data.get('action', 'UNKNOWN')}"
        tb_str = (
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            if exc
            else ""
        )

        payload = {
            "request_id": request_id,
            "user": {"user_id": user_id, "institution_id": institution_id},
            "operation": {
                "mod": request_data.get("mod", "UNKNOWN"),
                "subMod": request_data.get("subMod", "UNKNOWN"),
                "action": request_data.get("action", "UNKNOWN"),
            },
            "error": {
                "type": type(exc).__name__ if exc else "Exception",
                "message": str(exc) if exc else "Unknown error",
                "last_milestone": last_milestone,
                "http_code": 500,
                "stack_trace": tb_str,
            },
        }

        if "request_body" in request_data:
            payload["operation"]["request_body"] = request_data["request_body"]

        if response is not None:
            payload["response"] = response

        msg = f"Request error: {op} - {type(exc).__name__ if exc else 'Exception'}: {str(exc) if exc else ''}"
        exc_info = (type(exc), exc, exc.__traceback__) if exc else False
        cls._log(
            "oneapp.error", logging.ERROR, msg, metadata=payload, exc_info=exc_info
        )
