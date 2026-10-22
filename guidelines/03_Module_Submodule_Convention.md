# Module & Submodule Architecture Specification

## Purpose

This document defines the strict architectural standards, directory layouts, naming conventions, dynamic routing mechanisms, and import policies for all backend modules in the **OneApp** framework.

This document serves as an authoritative guideline for creating, refactoring, and maintaining modules and submodules across the backend repository.

---

# 1. Structural Overview & Mapping

The framework follows a convention-driven modular hierarchy:

$$\text{Module (Folder)} \longrightarrow \text{Submodule (Python File)} \longrightarrow \text{Submodule Class (Single Class)} \longrightarrow \text{Action (Method)} \longrightarrow \text{Action Type (Branch)}$$

### Entity Mapping Table

| Entity | Location / Convention | Naming Rule | Example |
| :--- | :--- | :--- | :--- |
| **Module Directory** | `modules/m_<mod_name>/` | `snake_case` with `m_` prefix | `modules/m_profile/` |
| **Module Entry Router** | `modules/m_<mod_name>/m_<mod_name>.py` | `m_<mod_name>.py` | [m_profile.py](modules/m_profile/m_profile.py) |
| **Submodule File** | `modules/m_<mod_name>/m_<mod_name>_sm_<sub_mod>.py` | `m_<mod_name>_sm_<sub_mod>.py` (`snake_case`) | `m_profile_sm_personal_detail.py` |
| **Submodule Class** | Inside submodule file | **One PascalCase class per file** | `class PersonalDetail:` |
| **Action Function** | Method inside submodule class | Matches `action` request field | `def personal_detail(self, action_type, payload, context):` |
| **Action Type** | `match action_type:` block inside function | `lowercase` string | `"add"`, `"view"`, `"update"`, `"delete"` |

---

# 2. Request JSON Payload Contract

API requests dispatched to any module must adhere strictly to the following JSON structure:

```json
{
  "mod": "profile",
  "subMod": "personal_detail",
  "action": "personal_detail",
  "actionType": "view",
  "payload": {
    "userId": "usr_12345"
  }
}
```

### Key Descriptions
- **`mod`**: Clean module name (e.g., `"profile"`, `"student"`, `"super_admin"`).
- **`subMod`**: Clean `snake_case` submodule identifier without `sm_` prefix (e.g., `"personal_detail"`, `"family_detail"`).
- **`action`**: Action function name inside the submodule class (e.g., `"personal_detail"`).
- **`actionType`**: Specific operation handled by the `match-case` block inside the action method (e.g., `"add"`, `"view"`, `"update"`, `"delete"`).
- **`payload`**: Input dictionary containing execution arguments.

---

# 3. Dynamic Module Router Specification (`m_<mod_name>.py`)

Each module contains a primary entry point file `m_<mod_name>.py` containing a `PascalCase` module class (e.g. `class Profile` or `class SuperAdmin`).

This class implements `__call__` to resolve submodules, classes, and action functions dynamically without hardcoded switches:

```python
import importlib
import asyncio

class Profile:
    """
    Dynamic Entry Point Router for m_profile module.
    """

    def __call__(self, req_json_obj, context):
        # Function-scoped import for utility response handler
        from xsc_lib.xsc_lib_common.xsc_libc_utility import error_response

        sub_mod = req_json_obj.get("subMod")
        action = req_json_obj.get("action")
        action_type = req_json_obj.get("actionType")

        if not sub_mod or not action or not action_type:
            return error_response(message="Missing 'subMod', 'action', or 'actionType'")

        try:
            # 1. Resolve submodule file (e.g., .m_profile_sm_personal_detail)
            sub_module_path = f".m_profile_sm_{sub_mod}"
            module = importlib.import_module(sub_module_path, package=__package__)

            # 2. Resolve PascalCase Class Name (e.g., "personal_detail" -> "PersonalDetail")
            from xsc_lib.xsc_lib_common.xsc_libc_utility import to_pascal_case
            class_name = to_pascal_case(sub_mod)
            module_class = getattr(module, class_name, None)

            if not module_class:
                return error_response(message=f"Class '{class_name}' not found in {sub_module_path}")

            instance = module_class()

            # 3. Resolve Action Method matching request action
            action_func = getattr(instance, action, None)
            if not action_func:
                return error_response(message=f"Action method '{action}' not found in class '{class_name}'")

            # 4. Execute (support async and sync)
            if asyncio.iscoroutinefunction(action_func):
                return asyncio.run(action_func(action_type, req_json_obj.get("payload", {}), context))
            return action_func(action_type, req_json_obj.get("payload", {}), context)

        except ImportError as e:
            return error_response(message=f"Submodule file not found for subMod '{sub_mod}'. Details: {str(e)}")
```

---

# 4. Submodule Implementation Specification

Each submodule file must contain **a single PascalCase class** representing the submodule. All action functions for that submodule reside inside this class.

```python
# File: modules/m_profile/m_profile_sm_personal_detail.py

class PersonalDetail:
    """
    Submodule handler class for personal detail management.
    """

    async def personal_detail(self, action_type, payload, context):
        """
        Main action method for personal_detail.
        """
        # Granular function-scoped imports
        from xsc_lib.xsc_lib_common.xsc_libc_utility import error_response
        from .m_profile_data import ProfileDataLayer

        dal = ProfileDataLayer(context.postgres)
        action_type = action_type.lower()

        # Action Type branching via match-case
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
        ...

    async def _view(self, payload, dal, context):
        ...

    async def _update(self, payload, dal, context):
        ...

    async def _delete(self, payload, dal, context):
        ...
```

---

# 5. Strict Import Guidelines

To maximize execution efficiency, eliminate circular dependency risks, and keep initial process startup fast, all Python code in modules and submodules **must follow strict import guidelines**:

### Rule 5.1: No Top-Level Heavy Imports
- **DO NOT** place heavy library imports, database connection modules, or cross-module utilities at the top of Python files.
- Top-level imports force Python to evaluate and load dependencies into memory at process boot time, degrading performance.

### Rule 5.2: Deferred / Function-Scoped Imports
- **DO** place imports **inside the specific function or method** where they are consumed.
- This ensures code and dependencies are evaluated lazily on demand when that specific action is executed.

### Rule 5.3: Granular Import Signatures
- **DO NOT** import entire modules or large utility classes (e.g. `import xsc_lib` or `from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility`).
- **DO** import specifically the required function or symbol directly.

```python
# CORRECT (Granular & Deferred inside function)
def my_action_handler(self, payload):
    from xsc_lib.xsc_lib_common.xsc_libc_string_operations import is_valid_name
    from xsc_lib.xsc_lib_common.xsc_libc_utility import error_response, success_response

    if not is_valid_name(payload.get("name")):
        return error_response(message="Invalid name")
    return success_response(message="Valid")

# INCORRECT (Top-level or broad class import)
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility  # Avoid broad class import
import xsc_lib                                                # Avoid broad library import
```

---

# 6. Summary Checklist for Developers

When creating or refactoring a submodule:
- [ ] Submodule file named `m_<mod>_sm_<sub_mod>.py` in `snake_case`.
- [ ] Submodule file contains **only one class**, named in `PascalCase` matching `sub_mod`.
- [ ] Action function inside the class matches the `action` request name.
- [ ] Operation branches handled via `match action_type:` inside the action function.
- [ ] All imports are **granular** (importing specific functions) and **deferred** inside the methods that require them.
