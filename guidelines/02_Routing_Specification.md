# Backend Routing Specification

# Purpose

This document defines the routing mechanism of the backend framework.

It explains how incoming requests are dynamically routed to the appropriate business logic, the responsibilities of each layer in the routing process, and the conventions that must be followed to ensure the routing system functions correctly.

The routing framework is completely dynamic and relies on convention rather than manual route registration.

---

# 1. Routing Philosophy

The backend exposes a **single API entry point**.

Every request enters through the same endpoint regardless of the business domain or feature being accessed.

Instead of defining individual routes for every API, the framework dynamically determines where a request should be executed based on the routing information contained within the request.

This approach provides:

* Minimal routing code.
* Consistent request handling.
* Dynamic feature discovery.
* Simplified framework maintenance.
* Unlimited scalability without modifying the router.

---

# 2. Routing Hierarchy

Every request follows the same routing hierarchy.

```text id="k34r7b"
Module
    ↓
SubModule
    ↓
Action
    ↓
ActionType
```

Each level progressively narrows the request until the required business logic is reached.

---

# 3. Routing Flow

Every request passes through the following stages.

```text id="ny7d0t"
Incoming Request
        │
        ▼
Read Module
        │
        ▼
Read SubModule
        │
        ▼
Build Import Path
        │
        ▼
Import Python Module
        │
        ▼
Discover Primary Class
        │
        ▼
Instantiate Class
        │
        ▼
Discover Public Action
        │
        ▼
Execute Action
        │
        ▼
Dispatch ActionType
        │
        ▼
Execute Business Logic
        │
        ▼
Return Response
```

The routing flow is identical for every request.

---

# 4. Router Responsibilities

The router is responsible only for dispatching requests.

Its responsibilities include:

* Receiving the request.
* Reading the routing information.
* Constructing the Python import path.
* Dynamically importing the requested submodule.
* Discovering the primary class.
* Instantiating the class.
* Discovering the requested public action.
* Invoking the action.

The router must never:

* Execute business logic.
* Understand ActionTypes.
* Perform feature-specific processing.
* Contain feature-specific conditions.
* Require modifications when new features are added.

The router should remain completely generic.

---

# 5. Dynamic Module Resolution

The router resolves the requested module dynamically.

Example routing information:

```text id="yb8m3j"
Module
faculty

SubModule
attendance
```

The router constructs the Python import path using the framework's directory conventions.

Example:

```text id="lwq61d"
modules.faculty.attendance
```

The router then imports the module dynamically.

No manual imports should ever be added to the router.

---

# 6. Dynamic Class Discovery

After importing the Python module, the router discovers the primary public class.

The class is not referenced by name inside the router.

Instead, it is identified dynamically using Python's inspection capabilities.

Every submodule must therefore contain exactly one primary public class.

This convention allows the routing framework to remain completely generic.

---

# 7. Class Instantiation

Once the primary class has been discovered, the router creates an instance of that class.

All subsequent routing occurs through that object.

The router does not need to know anything about the feature implementation.

---

# 8. Action Discovery

The router discovers the requested action by inspecting the available public methods of the instantiated class.

Only public methods are routable.

Private helper methods are ignored.

If the requested action does not exist, the router should terminate processing and return an appropriate error.

---

# 9. Action Execution

After locating the requested action, the router executes it.

At this point, the router has completed its responsibility.

Everything beyond this point is owned by the action itself.

---

# 10. ActionType Dispatch

Each action is responsible for internally dispatching ActionTypes.

The router never participates in ActionType routing.

An action should dispatch ActionTypes using Python's `match-case`.

Conceptually, the routing looks like this:

```text id="8xtv6r"
student_profile_main()
        │
        ▼
match(actionType)
        │
        ├── create
        ├── update
        ├── delete
        ├── search
        └── get_details
```

This allows related business operations to remain grouped within a single business capability.

---

# 11. Routing Responsibility Boundaries

The routing system is intentionally divided into independent responsibilities.

```text id="d2w7vx"
Frontend
        │
        ▼
Chooses:
• Module
• SubModule
• Action
• ActionType

────────────────────────────

Router
        │
        ▼
Responsible for:
• Dynamic discovery
• Dynamic imports
• Class discovery
• Action discovery
• Action execution

────────────────────────────

Action
        │
        ▼
Responsible for:
• ActionType dispatch
• Business orchestration
• Calling helper methods

────────────────────────────

Private Helpers
        │
        ▼
Responsible for:
• Internal implementation
```

Each layer performs only its own responsibility.

---

# 12. Dynamic Discovery Principles

The routing framework depends entirely on dynamic discovery.

The router should never maintain:

* Route tables.
* Action registries.
* Module registries.
* Class registries.
* Manual mappings.
* Hardcoded imports.

Everything should be discovered dynamically from the project structure.

---

# 13. Extending the Routing Framework

The routing framework is designed so that new functionality does not require modifications to the router.

Adding a new feature should typically involve one of the following:

* Creating a new submodule.
* Adding a new public action.
* Adding a new ActionType.

The router should continue functioning without modification.

If adding a feature requires changes to the routing layer, the implementation should be reconsidered.

---

# 14. Routing Principles

The routing framework follows these principles:

* One entry point for all backend requests.
* Dynamic module discovery.
* Dynamic class discovery.
* Dynamic action discovery.
* Convention-driven routing.
* No manual route registration.
* No hardcoded imports.
* No feature-specific routing logic.
* ActionTypes are dispatched only within actions.
* Business logic begins only after action execution.

---

# 15. Routing Lifecycle Summary

The complete routing lifecycle can be summarized as follows.

```text id="2c3zq9"
Request
    │
    ▼
Router
    │
    ▼
Dynamic Module Discovery
    │
    ▼
Dynamic Class Discovery
    │
    ▼
Dynamic Action Discovery
    │
    ▼
Action Execution
    │
    ▼
ActionType Dispatch
    │
    ▼
Business Logic
    │
    ▼
Response
```

The routing layer exists solely to locate and invoke the correct business capability. It should remain generic, convention-driven, and independent of business logic. Every new feature should integrate into this lifecycle without requiring changes to the router itself.
