# Backend Architecture Specification

## Purpose

This document defines the architecture of the backend framework. It explains how the framework is organized, how requests are routed, and the responsibilities of each architectural layer.

This document is the authoritative reference for the backend architecture and must be followed when extending or modifying the framework.

---

# 1. Architectural Overview

The backend follows a **modular, convention-driven architecture** with a **single dynamic routing entry point**.

Unlike traditional REST applications where each endpoint is manually registered, this framework dynamically discovers modules, classes, and actions based on predefined conventions.

The architecture is designed to:

* Reduce boilerplate.
* Eliminate manual route registration.
* Keep the router generic.
* Encourage feature isolation.
* Improve maintainability.
* Scale without increasing routing complexity.

---

# 2. High-Level Architecture

```text
                    Frontend
                        │
                        ▼
               Single API Endpoint
                        │
                        ▼
                  Dynamic Router
                   (index.py)
                        │
                        ▼
                 Module Discovery
                        │
                        ▼
               SubModule Discovery
                        │
                        ▼
                 Dynamic Import
                        │
                        ▼
                 Class Discovery
                        │
                        ▼
              Public Action Discovery
                        │
                        ▼
               Action Execution
                        │
                        ▼
           ActionType Dispatch (match-case)
                        │
                        ▼
                Business Logic
                        │
                        ▼
                   API Response
```

Only the router knows how to locate and execute code.

Business modules remain completely independent of the routing mechanism.

---

# 3. Architectural Hierarchy

The framework is organized into four logical layers.

```text
Module
    ↓
SubModule
    ↓
Action
    ↓
ActionType
```

Each layer has a single responsibility.

---

# 4. Module

A module represents a **business domain**.

Examples include:

* Faculty
* Student
* Finance
* Examination
* Library

Modules are the highest level of organization and should never contain business logic directly.

Their purpose is to group related features.

---

# 5. SubModule

A submodule represents a **single business feature** within a module.

Examples:

* Attendance
* Student Profile
* Fee Management
* Timetable

Each submodule maps to exactly one Python file and contains exactly one primary public class.

A submodule should encapsulate everything related to a single feature.

---

# 6. Class

Every submodule contains one primary public class.

The class is responsible for:

* Organizing feature functionality.
* Exposing routable actions.
* Encapsulating feature-specific logic.
* Managing private helper methods.

The router dynamically discovers and instantiates this class.

No manual registration is required.

---

# 7. Action

An action is a **public method** exposed by the class.

An action represents a **business capability**, not an individual CRUD operation.

Examples:

* Student Profile Management
* Attendance Processing
* Fee Collection
* Report Generation

An action acts as the entry point for a particular capability.

---

# 8. ActionType

An ActionType represents a **specific operation** performed by an action.

Rather than creating multiple public methods for related operations, the framework groups them into a single action.

Example:

```text
student_profile_main()

├── create
├── update
├── delete
├── search
└── get_details
```

The action performs internal routing using Python's `match-case`.

This keeps the public API of each class small while grouping related operations together.

---

# 9. Routing Lifecycle

Every request follows the same routing lifecycle.

```text
Request
    │
    ▼
Read Module
    │
    ▼
Read SubModule
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
Locate Public Action
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

Every request follows this exact sequence.

---

# 10. Router Responsibilities

The router (`index.py`) is responsible only for routing.

Its responsibilities include:

* Receiving requests.
* Identifying the module.
* Identifying the submodule.
* Dynamically importing the correct Python module.
* Discovering the primary class.
* Instantiating the class.
* Discovering the requested public action.
* Invoking the action.

The router must remain completely generic.

It should never contain business logic or feature-specific decisions.

---

# 11. Action Responsibilities

An action is responsible for:

* Receiving the request.
* Determining the requested ActionType.
* Dispatching internally using `match-case`.
* Executing the appropriate business logic.
* Returning the final result.

The action owns all ActionType routing.

The router never needs to understand ActionTypes.

---

# 12. Separation of Responsibilities

```text
Frontend
    │
    ▼
Chooses:
• Module
• SubModule
• Action
• ActionType

────────────────────────────────

Router
    │
    ▼
Responsible for:
• Dynamic discovery
• Dynamic imports
• Action invocation

────────────────────────────────

Action
    │
    ▼
Responsible for:
• ActionType dispatch
• Business orchestration

────────────────────────────────

Private Helpers
    │
    ▼
Responsible for:
• Validation
• Calculations
• Internal processing
```

Each layer has a clearly defined responsibility.

Responsibilities should never overlap.

---

# 13. Why ActionTypes Exist

Without ActionTypes, every business operation would require a separate public method.

Example:

```text
create_student()

update_student()

delete_student()

search_student()

get_student_details()
```

As features grow, classes become cluttered with numerous small public methods.

Instead, the framework groups related operations.

```text
student_profile_main()

├── create
├── update
├── delete
├── search
└── get_details
```

Benefits include:

* Smaller public interfaces.
* Better organization.
* Easier discovery.
* Clear grouping of related functionality.
* Reduced routing complexity.

---

# 14. Scalability

The architecture is designed to scale by adding functionality without modifying the routing layer.

Adding a new business capability typically requires:

* Creating a new submodule, or
* Adding a new action, or
* Adding a new ActionType.

The central router remains unchanged.

This allows the framework to grow without increasing architectural complexity.

---

# 15. Architectural Principles

The framework follows these architectural principles:

* Single routing entry point.
* Dynamic discovery instead of manual registration.
* Convention over configuration.
* Business logic isolated from routing.
* One feature per submodule.
* One primary class per submodule.
* Public actions expose business capabilities.
* ActionTypes group related operations.
* Private helper methods encapsulate implementation details.
* Modular design promotes scalability and maintainability.

---

# Summary

The backend architecture is intentionally simple and highly extensible.

The router is responsible only for locating and invoking the correct action.

Each submodule owns its feature.

Each action owns its business capability.

Each ActionType represents an operation within that capability.

This separation of concerns allows the backend to grow organically while keeping the routing layer stable, generic, and independent of business logic.
