"""
File: index.py
Description: Central Framework Router for OneApp Backend

Author: Siddharth Amdal
App: OneApp

"""

import time
import uuid
import jwt
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from xsc_lib.xsc_lib_common.xsc_libc_logger import XSCLogger
from xsc_lib.xsc_lib_common.xsc_libc_pgrs import PostgreSQLManager
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from xsc_lib.xsc_lib_common.xsc_libc_exceptions import OneAppException
from xsc_lib.xsc_lib_common.xsc_libc_models import OneAppRequest
from xsc_lib.xsc_lib_common.xsc_libc_context import ExecutionContext, SecurityContext
from xsc_lib.xsc_lib_app.xsc_liba_container import ServiceContainer
from xsc_lib.xsc_lib_app.xsc_liba_dispatcher import ActionDispatcher
from xsc_lib.xsc_lib_app.xsc_liba_module_loader import ModuleLoader

app = FastAPI(
    title="EduCore ERP Backend",
    description="Modular education ERP backend: dispatcher-driven modular monolith (FastAPI + PostgreSQL)",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def oneapp_middleware_pipeline(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.perf_counter()

    # Initialize Context early for milestone tracking
    ctx = ExecutionContext(request_id=request_id, service_container=ServiceContainer)
    request.state.context = ctx
    ctx.add_milestone("REQ001")

    XSCLogger.api(
        f"Incoming Request: {request.method} {request.url.path}",
        event="REQ001",
        metadata={"request_id": request_id},
    )

    response_status = 500
    try:
        ctx.start_timer("authentication")
        ctx.add_milestone("AUTH001")
        security_context = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                decoded = jwt.decode(token, "OneAppSecretKey", algorithms=["HS256"])
                security_context = SecurityContext(
                    user_id=decoded.get("user_id"),
                    institution_id=decoded.get("institution_id"),
                    roles=decoded.get("roles"),
                    permissions=decoded.get("permissions"),
                    jwt_claims=decoded,
                )
                ctx.add_milestone("AUTH002", {"user_id": security_context.user_id})
                ctx.add_milestone("JWT001")
            except jwt.InvalidTokenError:
                raise OneAppException(
                    status_code=401,
                    error_code="ERR401",
                    message="Invalid or expired authentication token",
                )

        ctx.security = security_context
        ctx.stop_timer("authentication")

        response = await call_next(request)
        response_status = response.status_code

    except Exception as _e:
        request_data = getattr(request.state, "req_data", {})
        request_data["method"] = request.method
        request_data["path"] = request.url.path

        last_ms = ctx.milestones[-1]["event"] if ctx.milestones else "REQ001"
        XSCLogger.log_error(request_id, request_data, e, last_ms, ctx.security)
        raise e
    finally:
        process_time = time.perf_counter() - start_time
        duration_ms = round(process_time * 1000, 2)

        request_data = getattr(request.state, "req_data", {})
        request_data["method"] = request.method
        request_data["path"] = request.url.path

        response_payload = getattr(request.state, "response_payload", None)

        result_data = {
            "status": "SUCCESS" if response_status < 400 else "ERROR",
            "http_code": response_status,
            "duration_ms": duration_ms,
        }
        if response_payload is not None:
            result_data["response"] = response_payload

        XSCLogger.log_request(
            request_id, request_data, result_data, ctx.milestones, ctx.security
        )
        XSCLogger.perf(
            "Request Completed",
            event="RESP001",
            metadata={"request_id": request_id, "duration_ms": duration_ms},
        )

    if "response" in locals():
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(duration_ms)
        return response
    return JSONResponse(status_code=500, content={"error": "Internal Server Error"})


@app.exception_handler(OneAppException)
async def oneapp_exception_handler(request: Request, exc: OneAppException):
    ctx = getattr(request.state, "context", None)
    last_ms = ctx.milestones[-1]["event"] if ctx and ctx.milestones else "REQ001"
    request_data = getattr(request.state, "req_data", {})
    request_id = getattr(request.state, "request_id", "UNKNOWN")

    err_response = {
        "status": "error",
        "message": exc.message,
        "error_code": exc.error_code,
    }
    if exc.details:
        err_response["details"] = exc.details

    XSCLogger.log_error(
        request_id,
        request_data,
        exc,
        last_ms,
        ctx.security if ctx else None,
        response=err_response,
    )

    if ctx:
        ctx.add_milestone("RESPONSE_GENERATED", details=err_response)
        request.state.response_payload = err_response

    return JSONResponse(status_code=exc.status_code, content=err_response)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    ctx = getattr(request.state, "context", None)
    last_ms = ctx.milestones[-1]["event"] if ctx and ctx.milestones else "REQ001"
    request_data = getattr(request.state, "req_data", {})
    request_id = getattr(request.state, "request_id", "UNKNOWN")

    import traceback

    tb_str = (
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        if exc
        else ""
    )

    err_response = {
        "status": "error",
        "message": f"Internal server error: {type(exc).__name__}: {str(exc)}",
        "error_code": "ERR500",
        "stack_trace": tb_str,
    }
    XSCLogger.log_error(
        request_id,
        request_data,
        exc,
        last_ms,
        ctx.security if ctx else None,
        response=err_response,
    )

    if ctx:
        ctx.add_milestone("RESPONSE_GENERATED", details=err_response)
        request.state.response_payload = err_response

    return JSONResponse(status_code=500, content=err_response)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    ctx = getattr(request.state, "context", None)
    err_response = XSCUtility.error_response(
        message="Invalid Request Payload", error_code="ERR422"
    )
    err_response["details"] = exc.errors()

    # Attempt to capture the validation error request body
    try:
        raw_body = await request.json()

        def sanitize_payload(data):
            if isinstance(data, dict):
                sanitized = {}
                for k, v in data.items():
                    if any(
                        s in k.lower()
                        for s in ["password", "secret", "token", "key", "captcha"]
                    ):
                        sanitized[k] = "********"
                    else:
                        sanitized[k] = sanitize_payload(v)
                return sanitized
            elif isinstance(data, list):
                return [sanitize_payload(item) for item in data]
            return data

        request.state.req_data = {"request_body": sanitize_payload(raw_body)}
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(
            "Failed to parse or sanitize request body in error handler: %s", str(e)
        )

    if ctx:
        ctx.add_milestone("RESPONSE_GENERATED", details=err_response)
        request.state.response_payload = err_response

    return JSONResponse(status_code=422, content=err_response)


@app.on_event("startup")
async def startup_event():
    XSCLogger.configure()
    XSCLogger.app("Starting OneApp Framework Runtime")
    ServiceContainer.register("Logger", XSCLogger)
    pgrs = PostgreSQLManager()
    await pgrs.async_connectDB()
    ServiceContainer.register("PostgreSQLManager", pgrs)
    ServiceContainer.register("Configuration", {"env": "development"})


@app.on_event("shutdown")
async def shutdown_event():
    XSCLogger.app("Shutting down OneApp Framework Runtime")
    pgrs = ServiceContainer.resolve("PostgreSQLManager")
    if pgrs:
        await pgrs.async_disconnectDB()


class OneAppFramework:
    @staticmethod
    def _build_context(request: Request) -> ExecutionContext:
        if hasattr(request.state, "context"):
            return request.state.context

        ctx = ExecutionContext(
            request_id=getattr(request.state, "request_id", str(uuid.uuid4())),
            service_container=ServiceContainer,
        )
        ctx.security = getattr(request.state, "security", SecurityContext())
        return ctx

    @staticmethod
    @app.post("/")
    async def run(req: OneAppRequest, request: Request):
        ctx = OneAppFramework._build_context(request)

        # Sanitize request payload to prevent logging plain credentials/sensitive information
        def sanitize_payload(data):
            if isinstance(data, dict):
                sanitized = {}
                for k, v in data.items():
                    if any(
                        s in k.lower()
                        for s in ["password", "secret", "token", "key", "captcha"]
                    ):
                        sanitized[k] = "********"
                    else:
                        sanitized[k] = sanitize_payload(v)
                return sanitized
            elif isinstance(data, list):
                return [sanitize_payload(item) for item in data]
            return data

        req.mod = ModuleLoader._resolve_mod_dir(req.mod)
        req.subMod = XSCUtility.to_snake_case(req.subMod)

        request.state.req_data = {
            "mod": req.mod,
            "subMod": req.subMod,
            "action": req.action,
            "actionType": req.actionType,
            "request_body": sanitize_payload(req.dict()),
        }
        result = await ActionDispatcher.dispatch(req, ctx)
        request.state.response_payload = result
        return result
