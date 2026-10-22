# AGENT-FIRST SPECIFICATION: OneApp Overall Backend Framework Architecture

> **IMPORTANT NOTICE FOR AI CODING AGENTS**:
> This document is an **agent-first, authoritative architectural reference** designed specifically for AI coding assistants working in this repository.
> When generating, refactoring, or inspecting code in the **OneApp** repository, you **MUST** strictly adhere to the patterns, invariants, naming rules, import protocols, and signatures documented here.

---

# 1. Executive Summary & Core Invariants

The **OneApp** backend is an enterprise-grade modular ERP platform built with **Python 3** and **FastAPI**. 

### 🛑 Strict Agent Invariants (Non-Negotiable Rules)

1. **Single Entry Point**: All HTTP requests MUST pass through the single POST gateway at `POST /` on `index.py`. NEVER create standalone FastAPI endpoints or ad-hoc router decorators (`@app.get(...)`, `@app.post(...)`) inside business modules.
2. **Module Directory Naming**: Module directories MUST be located in `modules/` and named using `snake_case` with an `m_` prefix (e.g., `modules/m_profile/`, `modules/m_student/`).
3. **Submodule File Naming**: Submodule files MUST be placed inside their parent module folder and named `m_<mod_name>_sm_<sub_mod_name>.py` using `snake_case` (e.g., `m_profile_sm_personal_detail.py`).
4. **Single Class Per Submodule File**: Each submodule file MUST contain **exactly one class** named in `PascalCase` matching the submodule name (e.g., `subMod: "personal_detail"` $\rightarrow$ `class PersonalDetail:`).
5. **Action Function Signature**: Action functions inside a submodule class MUST match the `action` request parameter and accept exactly `(self, action_type, payload, context)`:
   ```python
   async def personal_detail(self, action_type, payload, context):
   ```
6. **Action Type Routing**: Action function execution branching MUST be performed via a `match action_type.lower():` block inside the action method.
7. **Granular & Function-Scoped Imports**: NO top-level heavy imports or broad imports (`from ... import XSCUtility` or `import xsc_lib`). ALL imports MUST be granular (`from xsc_lib.xsc_lib_common.xsc_libc_utility import error_response`) and placed **inside the specific function/method** where they are executed.
8. **No Manual Module Unloading**: NEVER write code that attempts to unload Python modules (`del sys.modules[...]`). Rely on lazy imports and worker process boundaries.

---

# 2. Complete Technology & Dependency Stack

| Technology Layer | Specification / Library | Purpose & Usage in Code |
| :--- | :--- | :--- |
| **ASGI Engine** | `FastAPI`, `uvicorn`, `Starlette` | Serves HTTP pipeline, CORSMiddleware, and exception handling in `index.py`. |
| **Language Runtime** | `Python 3.11+` | Core execution engine. Uses `asyncio`, `importlib`, and native `match-case`. |
| **Database Pool** | `PostgreSQL`, `psycopg3`, `SQLAlchemy` | Multi-schema persistence (`sch_iam`, `sch_core`, `sch_student`, `sch_medical`). |
| **Security & Auth** | `PyJWT` (`jwt`) | Decodes Bearer tokens into `SecurityContext` (claims, roles, permissions). |
| **Cache & Queue** | `Redis` | Session storage, rate limiting, and message queue for background workers. |
| **Worker Engine** | `Celery` / `FastAPI Background Tasks` | Isolated memory-heavy computation (reporting, ML model execution). |

---

# 3. High-Level Architecture & End-to-End Request Trajectory

```text
  [ Client (ReactJS / Swift iOS / Kotlin Android) ]
                          │
                          │ HTTP POST / (JSON Payload)
                          ▼
  ┌───────────────────────────────────────────────────────────────┐
  │                 index.py (FastAPI Gateway)                    │
  │  1. oneapp_middleware_pipeline: Assign request_id (UUID)      │
  │  2. SecurityContext: Decode Bearer JWT header                 │
  │  3. OneAppFramework.run(): Wrap into OneAppRequest & ExecutionContext │
  └───────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
  ┌───────────────────────────────────────────────────────────────┐
  │         xsc_lib_app / ActionDispatcher.dispatch()             │
  │  1. Event: BeforeDispatch                                     │
  │  2. Hook:  before_dispatch                                    │
  │  3. ModuleLoader: Resolve module & class reference            │
  └───────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
  ┌───────────────────────────────────────────────────────────────┐
  │           Module Entry Router (modules/m_<mod>/m_<mod>.py)    │
  │  1. Profile.__call__(req_json_obj, context)                   │
  │  2. Dynamic import: .m_profile_sm_personal_detail             │
  │  3. Resolve Class: PersonalDetail (PascalCase)                │
  │  4. Resolve Action: personal_detail()                         │
  └───────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
  ┌───────────────────────────────────────────────────────────────┐
  │  Submodule Handler (m_profile_sm_personal_detail.py)         │
  │  1. PersonalDetail.personal_detail(action_type, payload, ctx) │
  │  2. Granular local import of ProfileDataLayer                 │
  │  3. match action_type:                                        │
  │     case "view":   return await self._view(...)               │
  │     case "add":    return await self._add(...)                │
  │     case "update": return await self._update(...)             │
  │     case "delete": return await self._delete(...)             │
  └───────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
  ┌───────────────────────────────────────────────────────────────┐
  │       Data Access Layer (ProfileDataLayer / PostgreSQL)       │
  │  Executes async SQL query via context.postgres                │
  └───────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
  ┌───────────────────────────────────────────────────────────────┐
  │                   Response Assembly                           │
  │  1. Format via success_response() / error_response()          │
  │  2. Hook:  after_dispatch                                     │
  │  3. Event: AfterDispatch                                      │
  │  4. Attach headers: X-Request-ID, X-Process-Time-Ms           │
  └───────────────────────────────────────────────────────────────┘
```

---

# 4. Standardized Data Contracts & Schemas

### 4.1 Request Contract (`OneAppRequest`)

Defined in [xsc_libc_models.py](xsc_lib/xsc_lib_common/xsc_libc_models.py):

```json
{
  "app": "OneApp",
  "mod": "profile",
  "subMod": "personal_detail",
  "action": "personal_detail",
  "actionType": "view",
  "payload": {
    "userId": "usr_998877"
  }
}
```

| JSON Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `app` | String | Optional | Calling client application name (e.g. `"OneApp"`). |
| `mod` | String | **Yes** | Target business domain module (`"profile"`, `"student"`, `"super_admin"`). |
| `subMod` | String | **Yes** | Target submodule name in `snake_case` without `sm_` prefix (`"personal_detail"`). |
| `action` | String | **Yes** | Action method name inside the submodule class (`"personal_detail"`). |
| `actionType` | String | **Yes** | Specific CRUD operation type (`"add"`, `"view"`, `"update"`, `"delete"`). |
| `payload` | Object | **Yes** | Dictionary containing domain-specific input parameters. |

---

### 4.2 Response Contract (`OneAppResponse`)

Returned by all actions via `XSCUtility` functions:

```json
{
  "statusCode": 1,
  "statusMsg": "Operation successful",
  "payload": {
    "userId": "usr_998877",
    "email": "alex@example.com",
    "firstName": "Alex"
  }
}
```

---

### 4.3 Numeric Framework Status Codes

| Status Code | Constant Identifier | HTTP Equivalent | Trigger Scenario |
| :---: | :--- | :---: | :--- |
| `1` | `STAT_CODE_SUCCESS` | `200 OK` | Request processed completely and successfully. |
| `0` | `STAT_CODE_WARN` | `200 OK` | Partial success, soft warnings, or empty data sets. |
| `-1` | `STAT_CODE_ERR_BIZ` | `400 Bad Request` | Business rule validation failed (e.g., duplicate record). |
| `-2` | `STAT_CODE_ERR_VALIDATION` | `422 Unprocessable` | Missing mandatory payload parameters or invalid types. |
| `-3` | `STAT_CODE_ERR_AUTH` | `401 Unauthorized` | Invalid JWT token or missing authorization header. |
| `-4` | `STAT_CODE_ERR_AUTHORIZATION` | `403 Forbidden` | User lacks required role/permission for action. |
| `-5` | `STAT_CODE_ERR_SYSTEM` | `500 Internal Err` | Uncaught runtime error, DB crash, or syntax exception. |

---

# 5. Core Framework Layers & Class Reference

### 5.1 Gateway & Pipeline Layer (`index.py` & `main.py`)

- **[main.py](main.py)**: ASGI entry point (`uvicorn main:app`). Re-exports `app` from `index.py`.
- **[index.py](index.py)**:
  - `oneapp_middleware_pipeline`: Intercepts every HTTP request, assigns a UUID `request_id`, decodes Bearer JWT, constructs `SecurityContext`, and tracks duration.
  - `OneAppFramework.run`: Bound to `@app.post("/")`. Assembles `ExecutionContext` and forwards to `ActionDispatcher.dispatch`.

---

### 5.2 Orchestration & Dispatch Layer (`xsc_lib_app`)

- **[xsc_liba_dispatcher.py](xsc_lib/xsc_lib_app/xsc_liba_dispatcher.py)** (`ActionDispatcher`):
  - Manages execution hooks (`before_dispatch`, `after_dispatch`) and framework events (`BeforeDispatch`, `AfterDispatch`).
  - Calls `ModuleLoader.load_action_class()` to locate the entry router.
- **[xsc_liba_module_loader.py](xsc_lib/xsc_lib_app/xsc_liba_module_loader.py)** (`ModuleLoader`):
  - Maintains in-memory reflection caches (`_cache["modules"]`, `_cache["submodules"]`, `_cache["actions"]`).
  - Performs dynamic imports using `importlib.import_module()`.
- **[xsc_liba_container.py](xsc_lib/xsc_lib_app/xsc_liba_container.py)** (`ServiceContainer`):
  - Thread-safe registry for singletons (`Logger`, `PostgreSQLManager`, `Configuration`).

---

### 5.3 Common Infrastructure Layer (`xsc_lib_common`)

- **[xsc_libc_context.py](xsc_lib/xsc_lib_common/xsc_libc_context.py)**:
  - `SecurityContext`: Contains `user_id`, `institution_id`, `roles`, `permissions`, `jwt_claims`.
  - `ExecutionContext`: Wraps `request_id`, `security`, `service_container`, and helper property `postgres`.
- **[xsc_libc_pgrs.py](xsc_lib/xsc_lib_common/xsc_libc_pgrs.py)** (`PostgreSQLManager`):
  - Asynchronous connection pool manager. Provides `async_genericSQL(stmt, params)`.
- **[xsc_libc_utility.py](xsc_lib/xsc_lib_common/xsc_libc_utility.py)** (`XSCUtility`):
  - Provides standard response formatters: `success_response(message, data, ...)` and `error_response(message, error_code, ...)`.

---

# 6. Canonical Implementation Templates for Agents

When creating or refactoring modules and submodules, agents **MUST** strictly copy and follow these exact code templates:

### Template 1: Module Entry Router (`modules/m_<mod_name>/m_<mod_name>.py`)

```python
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
        # Granular function-scoped import
        from xsc_lib.xsc_lib_common.xsc_libc_utility import error_response

        sub_mod = req_json_obj.get("subMod")
        action = req_json_obj.get("action")
        action_type = req_json_obj.get("actionType")

        if not sub_mod or not action or not action_type:
            return error_response(message="Missing 'subMod', 'action', or 'actionType'")

        try:
            # 1. Resolve submodule file (e.g. .m_profile_sm_personal_detail)
            sub_module_path = f".m_profile_sm_{sub_mod}"
            module = importlib.import_module(sub_module_path, package=__package__)

            # 2. Resolve PascalCase Class Name (e.g. "personal_detail" -> "PersonalDetail")
            from xsc_lib.xsc_lib_common.xsc_libc_utility import to_pascal_case
            class_name = to_pascal_case(sub_mod)
            module_class = getattr(module, class_name, None)

            if not module_class:
                return error_response(message=f"Class '{class_name}' not found in {sub_module_path}")

            instance = module_class()

            # 3. Resolve action method matching request action name
            action_func = getattr(instance, action, None)
            if not action_func:
                return error_response(message=f"Action method '{action}' not found in class '{class_name}'")

            # 4. Execute function (supports async and sync)
            if asyncio.iscoroutinefunction(action_func):
                return asyncio.run(action_func(action_type, req_json_obj.get("payload", {}), context))
            return action_func(action_type, req_json_obj.get("payload", {}), context)

        except ImportError as e:
            return error_response(message=f"Submodule file not found for subMod '{sub_mod}'. Details: {str(e)}")
```

---

### Template 2: Submodule File (`modules/m_<mod_name>/m_<mod_name>_sm_<sub_mod>.py`)

```python
"""
File: m_profile_sm_personal_detail.py
Description: Submodule handling Personal Detail operations for m_profile.

Author: EduCore
App: OneApp
"""


class PersonalDetail:
    """
    Submodule handler class for personal details.
    Contains action methods routing through match-case blocks.
    """

    async def personal_detail(self, action_type, payload, context):
        """
        Action method for personal_detail requests.
        """
        # Granular function-scoped imports
        from xsc_lib.xsc_lib_common.xsc_libc_utility import error_response
        from .m_profile_data import ProfileDataLayer

        dal = ProfileDataLayer(context.postgres)
        action_type = (action_type or "").lower()

        match action_type:
            case "add":
                return await self._add(payload, dal, context)
            case "view":
                return await self._view(payload, dal, context)
            case "update":
                return await self._update(payload, dal, context)
            case "delete":
                return await self._delete(payload, dal, context)
            case _:
                return error_response(message=f"Unsupported actionType '{action_type}' for personal_detail")

    # --- Internal Helper Methods ---
    async def _add(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import error_response, success_response

        user_id = payload.get("userId")
        if not user_id:
            return error_response(message="userId is required", error_code="ERR422")

        result = await dal.insert_personal_detail(user_id, payload)
        return success_response(message="Personal detail created successfully", data=result)

    async def _view(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import error_response, success_response

        user_id = payload.get("userId") or context.security.user_id
        if not user_id:
            return error_response(message="userId is required", error_code="ERR422")

        record = await dal.get_personal_detail(user_id)
        if not record:
            return error_response(message="Personal detail not found", error_code="ERR404")

        return success_response(message="Personal detail retrieved", data=record)

    async def _update(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import error_response, success_response

        user_id = payload.get("userId")
        if not user_id:
            return error_response(message="userId is required", error_code="ERR422")

        updated = await dal.update_personal_detail(user_id, payload)
        return success_response(message="Personal detail updated successfully", data=updated)

    async def _delete(self, payload, dal, context):
        from xsc_lib.xsc_lib_common.xsc_libc_utility import error_response, success_response

        user_id = payload.get("userId")
        if not user_id:
            return error_response(message="userId is required", error_code="ERR422")

        await dal.delete_personal_detail(user_id)
        return success_response(message="Personal detail deleted successfully")
```

---

# 7. Strict Import Protocol for Agents

To optimize startup performance and eliminate circular dependencies, AI agents **MUST** follow these rules when adding imports:

### 🚫 Forbidden Import Patterns
```python
# PROHIBITED: Top-level heavy import
import pandas as pd  # DO NOT place heavy imports at the top of python files

# PROHIBITED: Importing broad utility classes or whole packages
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility  # DO NOT import broad utility class
import xsc_lib                                                # DO NOT import entire namespace
```

### ✅ Allowed & Required Import Patterns
```python
# REQUIRED: Deferred, function-scoped, granular imports
def my_method(self, payload):
    from xsc_lib.xsc_lib_common.xsc_libc_string_operations import is_valid_name
    from xsc_lib.xsc_lib_common.xsc_libc_utility import error_response, success_response

    if not is_valid_name(payload.get("username")):
        return error_response(message="Invalid username")
    return success_response(message="Valid username")
```

---

# 8. Agent Checklist & Verification Protocol

Before completing any coding task involving the framework or business modules, AI agents **MUST** run through this verification checklist:

- [ ] **Router Check**: Is the request passing through `POST /` on `index.py`?
- [ ] **Module Path Check**: Is the module located in `modules/m_<mod>/`?
- [ ] **Submodule Path Check**: Is the submodule file named `m_<mod>_sm_<sub_mod>.py` in `snake_case`?
- [ ] **Class Naming Check**: Is there **exactly one class** in the submodule file, named in `PascalCase` matching `subMod`?
- [ ] **Action Signature Check**: Does the action method signature match `def <action>(self, action_type, payload, context):`?
- [ ] **Match-Case Routing Check**: Is operation branching handled via `match action_type:` inside the action method?
- [ ] **Import Audit Check**: Are **ALL** imports granular and located **inside the specific function/method** where they are used?
- [ ] **Response Schema Check**: Are responses formatted using `success_response()` or `error_response()`?
