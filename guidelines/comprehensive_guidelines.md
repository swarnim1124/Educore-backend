# Backend Development Standards & Framework Specification

## Purpose

This document is the authoritative specification for developing and maintaining the backend framework. It defines the architecture, conventions, standards, and procedures that **must** be followed when generating, modifying, or refactoring backend code.

The purpose of this document is to ensure that all backend code:

* Follows a consistent architecture.
* Adheres to the framework's conventions.
* Remains maintainable and scalable.
* Integrates seamlessly with the existing codebase.
* Requires minimal manual review for architectural consistency.

Unless explicitly instructed otherwise by the development team, every piece of backend code must comply with this specification.

---

# 1. Core Philosophy

The backend framework is built on the following principles.

## 1.1 Convention Over Configuration

The framework relies on conventions rather than manual registration.

Files, classes, methods, and modules are discovered dynamically based on predefined naming conventions.

Never introduce manual registration mechanisms unless explicitly required by the framework.

---

## 1.2 Modular Architecture

The backend is divided into business domains.

Each domain contains independent features that can evolve without affecting unrelated modules.

The architecture should encourage isolation, maintainability, and scalability.

---

## 1.3 Dynamic Routing

All requests enter through a single routing layer.

The router dynamically locates the appropriate module, submodule, class, and action without hardcoded route definitions.

---

## 1.4 Separation of Concerns

Each layer has a clearly defined responsibility.

The router performs routing.

Actions perform business orchestration.

Private methods perform implementation details.

Helpers perform reusable functionality.

Responsibilities should never overlap.

---

## 1.5 Reusability

Existing functionality should always be reused whenever appropriate.

Avoid duplicate implementations.

Prefer extending existing code over introducing parallel implementations.

---

## 1.6 Consistency

Consistency is preferred over individual coding preferences.

If multiple valid implementations exist, choose the one that best aligns with this framework.

---

## 1.7 Simplicity

Keep implementations straightforward.

Avoid unnecessary abstractions.

Avoid premature optimization.

Avoid unnecessary design patterns.

---

# 2. Framework Invariants

The following rules are non-negotiable.

These rules must never be violated.

* The backend has a single routing entry point.
* Routing logic must remain generic.
* Business logic must never exist inside the router.
* Modules represent business domains.
* Submodules represent individual features.
* Every submodule contains exactly one primary public class.
* Class discovery is performed dynamically.
* Public methods are routable.
* Private methods are internal implementation details.
* Actions may contain multiple actionTypes.
* Action routing is handled using Python `match-case`.
* Business logic belongs inside actions and private helper methods.
* All naming conventions defined in this document are mandatory.
* Existing code should be reused whenever possible.
* Duplicate business logic should never be introduced.

---

# 3. Backend Architecture

The routing hierarchy is:

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

## Module

Represents a business domain.

Examples:

* faculty
* student
* finance
* examination

---

## SubModule

Represents a single feature within a module.

Examples:

* attendance
* student_profile
* fee_management

Each submodule maps to one Python file.

---

## Class

Every submodule contains one primary class.

The class encapsulates the feature.

---

## Action

An action is a public method exposed by the class.

An action represents a business capability rather than an individual CRUD operation.

---

## ActionType

An actionType represents a specific operation within an action.

Actions dispatch internally using `match-case`.

---

# 4. Dynamic Routing

The routing process follows the sequence below.

```text
Request
    ↓
Module
    ↓
SubModule
    ↓
Dynamic Import
    ↓
Class Discovery
    ↓
Class Instantiation
    ↓
Action Discovery
    ↓
Action Execution
    ↓
match(actionType)
    ↓
Business Logic
    ↓
Response
```

## Router Responsibilities

The router is responsible for:

* Identifying the module.
* Identifying the submodule.
* Dynamically importing the submodule.
* Discovering the primary class.
* Instantiating the class.
* Discovering the requested public action.
* Executing the action.

The router must not contain business logic.

The router must not know the available actionTypes.

---

## Action Responsibilities

Each action is responsible for:

* Receiving the request.
* Interpreting the actionType.
* Dispatching internally using `match-case`.
* Executing business logic.
* Returning the result.

---

## ActionType Routing

Multiple operations belonging to the same business capability should be grouped into one action.

Example:

```python
def student_profile_main(self, payload, action_type):

    match action_type:

        case "create":
            ...

        case "update":
            ...

        case "delete":
            ...

        case "search":
            ...

        case _:
            raise ValueError("Unsupported action type")
```

---

# 5. Naming Conventions

The framework depends on strict naming conventions.

---

## Modules

* lowercase
* prefixed with `m_` (e.g., `m_<module_name>`)
* directory name

Examples

```
m_faculty
m_student
m_finance
m_super_admin
m_profile
m_AAA
```
---
if the name of the module has 2 words then it must be written with `_` between it after `m_` prefix.

## SubModules

* lowercase
* snake_case
* prefixed with `m_<module_name>_sm_<submodule_name>.py`
* one file per feature

Examples

```
m_attendance_sm_leave.py

m_profile_sm_personal_detail.py

m_fees_sm_payment.py
```

---

## Classes

Classes use PascalCase (or matching feature name).

Examples

```
Attendance

StudentProfile

FeeManagement
```

Every submodule contains one primary public class.

---

## Public Methods (Actions & ActionType Handlers)

All public methods use snake_case or camelCase matching feature capabilities.

ActionType handlers inside submodule classes (e.g., `add`, `view`, `update`, `delete`, `leave_add`, `leave_view`) are exposed as **public methods**.

Examples

```
attendance_main()

student_profile_main()

add()

view()

update()

delete()
```

---

## Private Methods

Private methods begin with an underscore `_` and are strictly internal helper methods (such as internal data validation routines).

Examples

```
_validate_internal_state()

_format_raw_buffer()
```

Private methods are never routable.

---

## ActionTypes

ActionTypes use lowercase snake_case or camelCase. ActionType handler methods on classes are public methods.

Examples

```
add

view

update

delete

create

search

bulk_update

approve

reject

archive

restore
```

---

## Variables

Variables use snake_case.

Examples

```
student_id

academic_year

attendance_percentage
```

---

## Constants

Constants use UPPER_SNAKE_CASE.

Examples

```
MAX_RETRY_COUNT

DEFAULT_TIMEOUT

SUPPORTED_ACTION_TYPES
```

---

# 6. Development Workflow

All backend development should follow the same workflow.

```text
Understand Requirement
        ↓
Identify Module
        ↓
Identify SubModule
        ↓
Identify Action
        ↓
Identify ActionType
        ↓
Locate Existing Code
        ↓
Implement Changes
        ↓
Verify Framework Compliance
```

Never skip framework compliance verification.

---

# 7. Coding Standards

## Readability

Write code that is easy to understand.

Avoid clever implementations.

Prioritize clarity.

---

## Single Responsibility

Methods should perform one logical responsibility.

Split complex implementation into private helper methods.

---

## Public vs Private Methods

Public methods expose business capabilities.

Private methods support implementation.

Private methods must never become part of the routing layer.

---

## Method Organization

Recommended ordering inside classes:

1. Public actions
2. Private helper methods
3. Utility methods

---

## Imports

Keep imports organized.

Remove unused imports.

Avoid duplicate imports.

---

## Comments

Comments should explain **why**, not **what**.

Do not comment obvious code.

---

## Magic Values

Avoid hardcoded values.

Use named constants where appropriate.

---

## Code Duplication

Never duplicate business logic.

Extract reusable logic into helper methods when appropriate.

---

## Consistency

Follow the existing implementation style of the module.

Do not introduce different coding patterns within the same feature.

---

# 8. Action Design Guidelines

Actions represent business capabilities.

They should not represent individual CRUD operations.

Preferred:

```
student_profile_main()
```

Not preferred:

```
create_student()

update_student()

delete_student()
```

These operations belong inside the action.

Actions should remain cohesive.

If unrelated business capabilities emerge, create a new action rather than continuously expanding an existing one.

Private helper methods should be used to improve readability.

---

# 9. Code Reuse Guidelines

Before implementing new functionality:

* Search for an existing implementation.
* Search for reusable helper methods.
* Search for reusable utilities.
* Extend existing implementations whenever appropriate.

Do not introduce duplicate functionality.

Do not create nearly identical methods.

Prefer modifying existing implementations over creating parallel ones.

---

# 10. Common Mistakes to Avoid

Do not:

* Add business logic to the router.
* Create multiple primary classes in one submodule.
* Bypass dynamic routing.
* Hardcode module imports.
* Introduce duplicate business logic.
* Ignore naming conventions.
* Create CRUD methods instead of actionTypes.
* Expose private helper methods as public actions.
* Introduce unnecessary abstraction.
* Create inconsistent coding styles within the same module.

---

# 11. AI Development Checklist

Before considering any implementation complete, verify the following:

* Correct module selected.
* Correct submodule selected.
* Correct action selected.
* Correct actionType selected.
* Naming conventions followed.
* Router remains unchanged.
* Business logic placed in the correct layer.
* Public and private methods correctly separated.
* Existing code reused where appropriate.
* No duplicate implementation introduced.
* Framework invariants satisfied.
* Code remains readable and maintainable.

Every implementation should satisfy this checklist before being considered complete.

---

# 12. Practical Examples

## Example 1

Feature:

Student Profile

```
Module
    student

SubModule
    student_profile

Class
    StudentProfile

Action
    student_profile_main()

ActionTypes
    create
    update
    delete
    search
```

---

## Example 2

Attendance Reporting

```
Module
    faculty

SubModule
    attendance

Class
    Attendance

Action
    attendance_report()

ActionTypes
    daily
    monthly
    yearly
```

---

## Example 3

Private Helper

```
attendance_main()

↓

_attendance_validate()

↓

_attendance_prepare_data()

↓

_attendance_save()

↓

Return Response
```

Private helper methods remain internal and are never exposed through the routing system.

---

# Final Principle

This framework is intentionally convention-driven.

The architecture, naming conventions, routing strategy, and coding standards defined in this document are designed to keep the backend consistent, scalable, and maintainable.

When implementing or modifying backend functionality, prioritize consistency with the framework over personal coding preferences. Every change should integrate naturally into the existing architecture without requiring changes to the routing layer or deviations from the established conventions.
