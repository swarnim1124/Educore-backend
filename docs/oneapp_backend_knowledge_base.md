# OneApp Backend — Comprehensive Knowledge Base

> **Generated from source code analysis** — EduCore, OneApp v2.0.0  
> **Codebase Root**: `XCS_backend_main/`  
> **Framework**: FastAPI (Python) + SQLAlchemy + PostgreSQL  
> **Architecture**: Modular ERP with dynamic routing via `mod → subMod → action → actionType`

---

## Table of Contents

1. [Framework Architecture](#framework-architecture)
2. [Module: m_AAA — Authentication, Authorization & Auditing](#module-m_aaa)
3. [Module: m_attendance — Attendance Management](#module-m_attendance)
4. [Module: m_curriculum — Curriculum Management](#module-m_curriculum)
5. [Module: m_exam — Examinations & Results](#module-m_exam)
6. [Module: m_fees — Fee Lifecycle Management](#module-m_fees)
7. [Module: m_profile — User Profile Management](#module-m_profile)
8. [Module: m_super_admin — Super Administration](#module-m_super_admin)
9. [Module: m_timetable — Timetable Management](#module-m_timetable)
10. [Final Summary & Operation Index](#final-summary)

---

## Framework Architecture

### Single Endpoint Routing

All operations are routed through a **single POST endpoint** at `/`. Every request uses the `OneAppRequest` model:

```json
{
  "mod": "<module_name>",
  "subMod": "<submodule_name>",
  "action": "<action_name>",
  "actionType": "<action_verb>",
  "payload": { ... }
}
```

### Request Lifecycle

1. **Middleware Pipeline** (`index.py`): Assigns `request_id` (UUID), starts timers, extracts JWT from `Authorization: Bearer <token>` header, populates `SecurityContext` (user_id, institution_id, roles, permissions).
2. **Payload Sanitization**: Sensitive fields (password, secret, token, key, captcha) are masked in logs.
3. **Module Resolution** (`ModuleLoader`): Resolves `mod` → directory, `subMod` → Python file, `action` → class method. Uses in-memory caching.
4. **Manifest Validation**: Checks `manifest.py` to confirm submodule is registered in `SUPPORTED_SUBMODULES`.
5. **Lifecycle Hooks**: `BeforeDispatch` event → `before_dispatch` hook → **Action Execution** → `after_dispatch` hook → `AfterDispatch` event.
6. **Action Dispatch** (`ActionDispatcher`): Calls the resolved action function with `(request, context)` or `(actionType, payload, context)` signatures.
7. **Response Wrapping**: If result lacks `status` key, wrapped in `XSCUtility.success_response()`.

### Standard Response Format

```json
// Success
{ "status": "success", "message": "...", "data": { ... } }

// Error  
{ "status": "error", "message": "...", "error_code": "..." }
```

### Key Shared Services

| Service | Class | Location |
|---------|-------|----------|
| Database Manager | `PostgreSQLManager` | `xsc_lib/xsc_lib_common/xsc_libc_pgrs.py` |
| Utilities | `XSCUtility` | `xsc_lib/xsc_lib_common/xsc_libc_utility.py` |
| Logger | `XSCLogger` | `xsc_lib/xsc_lib_common/xsc_libc_logger.py` |
| Capability Registry | `CapabilityRegistry` | `xsc_lib/xsc_lib_app/xsc_liba_capability.py` |
| Service Container | `ServiceContainer` | `xsc_lib/xsc_lib_app/xsc_liba_container.py` |
| Exception System | `OneAppException` hierarchy | `xsc_lib/xsc_lib_common/xsc_libc_exceptions.py` |
| CAPTCHA | `get_captcha_provider()` | `xsc_lib/xsc_lib_app/xsc_liba_captcha.py` |

### Exception Hierarchy

| Exception | Error Code | HTTP Status | Purpose |
|-----------|-----------|-------------|---------|
| `OneAppException` | custom | custom | Base application exception |
| `FrameworkException` | FWK500 | 500 | Framework internal errors |
| `ModuleNotFoundException` | FWK404 | 404 | Module/submodule not found |
| `InvalidActionException` | FWK400 | 400 | Invalid action reference |
| `AuthorizationException` | ERR403 | 403 | Permission denied |

### JWT Authentication

- **Secret**: `OneAppSecretKey` (middleware) / `config.JWT_SECRET` (token generation)
- **Algorithm**: HS256
- **Claims**: `sub` (user_id), `session_id`, `org_id`, `inst_id`, `exp`
- **Header**: `Authorization: Bearer <token>`

---

<a id="module-m_aaa"></a>
## Module: m_AAA — Authentication, Authorization & Auditing

**Version**: 2.0.0  
**Submodules**: `sm_auth`, `sm_rbac`, `sm_policy`  
**Data Layer**: `AAADataLayer` (from `m_AAA_data.py`)  
**DB Schemas**: `sch_aaa`  
**Dependencies**: None (root module)

---

### Submodule: sm_auth

---

#### Operation 1: Login (Create Session)

**1. Operation Name**: Login / Create Session

**2. Explanation**: Authenticates a user via email/password credentials. Supports CAPTCHA enforcement (policy-driven), account lockout detection (5 consecutive failures), password expiration checks, forced password change detection, and MFA challenge initiation. On success, issues a JWT token and creates a session record.

**3. Routing**:
- Module: `m_AAA`
- Submodule: `sm_auth`
- Action: `session`
- Action Type: `add`

**4. Requirements**:
- Authentication: **Not required** (login endpoint)
- Policy provider capability must be registered
- User account must exist in `sch_iam.tb_user`
- Account must not be locked (< 5 consecutive failed logins)
- Password must not be expired
- If CAPTCHA enabled by login policy: valid captcha token required
- If MFA active: second-phase challenge verification needed

**5. Request Payload**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` / `email` | string | Yes | User's login identifier |
| `password` | string | Yes | User's plaintext password |
| `captchaToken` | string | Conditional | Required if institution login policy enables CAPTCHA |
| `userAgent` | string | No | Client user agent string |
| `ipAddress` | string | No | Client IP address |
| `challengeToken` | string | Conditional | For MFA second-phase verification |
| `response` | string | Conditional | OTP/backup code for MFA verification |

**6. Response Payload**:

*Success (200)*:
```json
{ "status": "success", "message": "Login successful", "data": { "token": "<jwt>", "captchaRequired": false, "sessionId": "<uuid>" } }
```
*MFA Required (206)*:
```json
{ "status": "success", "message": "MFA Challenge Required", "data": { "challengeToken": "<token>", "mfaRequired": true } }
```
*Force Password Change (206)*:
```json
{ "status": "success", "message": "Password change required", "data": { "userId": "<id>", "forceChange": true } }
```
*Errors*: Invalid credentials, Account locked, CAPTCHA required/invalid, Password expired

**7. Database Operations**:

| Table | Operation | Purpose |
|-------|-----------|---------|
| `sch_iam.tb_user` | SELECT | Lookup user by email |
| `sch_aaa.tb_password_state` | SELECT | Check password expiration |
| `sch_aaa.tb_auth_log` | SELECT | Check account lockout (last 5 events) |
| `sch_aaa.tb_auth_log` | INSERT | Log login success/failure |
| `sch_aaa.tb_mfa_method` | SELECT | Check active MFA methods |
| `sch_aaa.tb_mfa_challenge` | INSERT | Create MFA challenge record |
| `sch_aaa.tb_session` | SELECT | Count active sessions |
| `sch_aaa.tb_session` | UPDATE | Invalidate excess sessions |
| `sch_aaa.tb_session` | INSERT | Create new session record |

**8. Sequence of Operations**:
1. Extract `username` and `password` from payload
2. Validate both fields are present
3. Query user by email → fail if not found (generic error to prevent enumeration)
4. Check password expiration state → fail if expired
5. Load auth context (org_id, institution_id)
6. Fetch login policy → determine CAPTCHA requirement
7. If CAPTCHA required: validate token via CAPTCHA provider
8. Check account lockout (5+ consecutive failures in recent auth logs)
9. Compare password hash via `XSCUtility.compare_hash()`
10. On failure: log failed attempt and return error
11. Check for forced password change (status_id == 5)
12. Check active MFA methods → if active, issue MFA challenge (206)
13. Load session policy (max concurrent sessions, duration)
14. Invalidate excess sessions if at limit
15. Generate JWT with claims (sub, session_id, org_id, inst_id, exp)
16. Create session record in database
17. Log successful authentication event
18. Return JWT token and session info

**9. Prerequisite Operations**: None (entry point)

**10. Other Details**:
- Uses `CapabilityRegistry` to resolve `policy_provider` and `mfa_provider`
- Password hashing via `XSCUtility.generate_hash()` / `XSCUtility.compare_hash()`
- MFA challenge tokens expire in 5 minutes
- Session duration defaults to 120 minutes if no policy

---

#### Operation 2: View Active Sessions

**1. Operation Name**: View Active Sessions

**2. Explanation**: Retrieves all active sessions for the authenticated user.

**3. Routing**: `m_AAA` → `sm_auth` → `session` → `view`

**4. Requirements**: Authenticated (JWT required, user_id extracted from SecurityContext)

**5. Request Payload**: None required (uses authenticated user_id)

**6. Response Payload**: Success with array of session records.

**7. Database Operations**: `sch_aaa.tb_session` SELECT (active sessions for user)

**8. Sequence**: Extract user_id from context → Query active sessions → Return list

**9. Prerequisite Operations**: Login (session/add)

---

#### Operation 3: Refresh Session

**1. Operation Name**: Refresh Session (Token Renewal)

**2. Explanation**: Extends an active session by generating a new JWT with a 2-hour extension.

**3. Routing**: `m_AAA` → `sm_auth` → `session` → `update`

**4. Requirements**: Authenticated, valid session_id in SecurityContext

**5. Request Payload**: None

**6. Response Payload**: `{ "token": "<new_jwt>" }`

**7. Database Operations**: None (generates new JWT based on context claims)

**8. Sequence**: Validate auth → Generate new JWT with +2h expiry → Return

**9. Prerequisite Operations**: Login (session/add)

---

#### Operation 4: Logout (Delete Session)

**1. Operation Name**: Logout / Delete All Sessions

**2. Explanation**: Invalidates all active sessions for the user and logs the logout event.

**3. Routing**: `m_AAA` → `sm_auth` → `session` → `delete`

**4. Requirements**: Authenticated (graceful if not — still returns success)

**5. Request Payload**: None

**6. Response Payload**: `{ "status": "success", "message": "Logout successful" }`

**7. Database Operations**: `tb_session` UPDATE (invalidate all), `tb_auth_log` INSERT (logout event, evt_type_id=2)

**8. Sequence**: Extract user_id → Invalidate all sessions → Log logout event → Return success

**9. Prerequisite Operations**: Login (session/add)

---

#### Operation 5: Set Password (Password Add)

**1. Operation Name**: Set Password

**2. Explanation**: Sets a new password for the authenticated user, validating against the institution's password policy.

**3. Routing**: `m_AAA` → `sm_auth` → `password` → `add`

**4. Requirements**: Authenticated; password policy must be accessible

**5. Request Payload**: `password` (string, required)

**6. Response Payload**: Success message

**7. Database Operations**: UPDATE user password hash, UPDATE password state (is_expired=false), INSERT auth log (evt_type_id=4)

**8. Sequence**: Validate auth → Fetch password policy → Validate password constraints → Hash and store → Mark password active → Log event

**9. Prerequisite Operations**: Login

---

#### Operation 6: Validate Password Strength

**1. Operation Name**: Evaluate Password Strength

**2. Explanation**: Evaluates a prospective password against the institution's password policy without changing anything.

**3. Routing**: `m_AAA` → `sm_auth` → `password` → `view`

**4. Requirements**: None (reads-only)

**5. Request Payload**: `password` (string) — the password to evaluate

**6. Response Payload**: `{ "isCompliant": true, "score": 100, "strength": "Strong", "rules": {...}, "failedRules": [] }`

**7. Database Operations**: None (policy fetched from capability registry)

**8. Sequence**: Fetch password policy → Evaluate each rule → Return compliance report

**9. Prerequisite Operations**: None

---

#### Operation 7: Change Password

**1. Operation Name**: Change Password

**2. Explanation**: Changes the user's password after verifying the current password and validating the new one against policy.

**3. Routing**: `m_AAA` → `sm_auth` → `password` → `update`

**4. Requirements**: Authenticated; must provide correct current password

**5. Request Payload**: `currentPassword` (required), `newPassword` (required)

**6. Response Payload**: Success message

**7. Database Operations**: SELECT password hash (verify), UPDATE password hash, INSERT auth log (evt_type_id=3)

**8. Sequence**: Verify auth → Fetch current hash → Compare → Validate new password against policy → Hash and update → Log event

**9. Prerequisite Operations**: Login

---

#### Operation 8: Expire Password

**1. Operation Name**: Force Expire Password

**2. Explanation**: Administratively expires a user's password, revoking all active sessions and forcing re-authentication with password change.

**3. Routing**: `m_AAA` → `sm_auth` → `password` → `delete`

**4. Requirements**: Authenticated (admin action)

**5. Request Payload**: None

**6. Response Payload**: Success message

**7. Database Operations**: UPDATE password state (is_expired=true), REVOKE sessions, INSERT auth log

**8. Sequence**: Set expired state → Revoke all sessions → Log event

**9. Prerequisite Operations**: Login

---

#### Operation 9: Initiate Password Reset

**1. Operation Name**: Initiate Password Reset

**2. Explanation**: Generates a secure password reset token (URL-safe, 32 bytes) with 1-hour expiry. Returns a generic message regardless of account existence to prevent email enumeration.

**3. Routing**: `m_AAA` → `sm_auth` → `passwordReset` → `add`

**4. Requirements**: None (unauthenticated endpoint)

**5. Request Payload**: `email` (required)

**6. Response Payload**: Generic success message (does not reveal account existence)

**7. Database Operations**: SELECT user by email, INSERT password reset token

**8. Sequence**: Lookup user → Generate token → Store with expiry → Return generic success

> [!NOTE]
> Email notification is deferred — `CommunicationManager` is not yet implemented.

**9. Prerequisite Operations**: None

---

#### Operation 10: Validate Reset Token

**1. Operation Name**: Validate Password Reset Token

**2. Explanation**: Checks if a password reset token is valid and not expired.

**3. Routing**: `m_AAA` → `sm_auth` → `passwordReset` → `view`

**4. Requirements**: None

**5. Request Payload**: `token` (required)

**6. Response Payload**: Success if valid; error if invalid/expired

**7. Database Operations**: SELECT password reset token record

**8. Sequence**: Fetch token → Check expiry → Return validation result

**9. Prerequisite Operations**: Initiate Password Reset (passwordReset/add)

---

#### Operation 11: Execute Password Reset

**1. Operation Name**: Execute Password Reset

**2. Explanation**: Resets the user's password using a valid reset token. Enforces password policy, invalidates the token, and revokes all active sessions atomically.

**3. Routing**: `m_AAA` → `sm_auth` → `passwordReset` → `update`

**4. Requirements**: Valid, non-expired reset token; new password must comply with policy

**5. Request Payload**: `token` (required), `newPassword` (required)

**6. Response Payload**: Success message

**7. Database Operations**: SELECT token → UPDATE password → INVALIDATE token → REVOKE sessions → INSERT auth log (atomic transaction)

**8. Sequence**: Validate token → Check expiry → Enforce password policy → Hash password → Execute atomic reset (password update + token invalidation + session revocation) → Log event

**9. Prerequisite Operations**: Initiate Password Reset

---

#### Operation 12: Cancel Password Reset

**1. Operation Name**: Cancel Password Reset

**2. Explanation**: Revokes an active password reset token, preventing its use.

**3. Routing**: `m_AAA` → `sm_auth` → `passwordReset` → `delete`

**4. Requirements**: None

**5. Request Payload**: `token` (required)

**6. Response Payload**: Success message

**7. Database Operations**: SELECT token → UPDATE revoked_at

**8. Sequence**: Validate token → Check expiry → Revoke atomically

**9. Prerequisite Operations**: Initiate Password Reset

---

#### Operation 13: View Current User

**1. Operation Name**: Get Current User Profile

**2. Explanation**: Returns the authenticated user's identity, roles, permissions, and organization data from JWT claims.

**3. Routing**: `m_AAA` → `sm_auth` → `user` → `view`

**4. Requirements**: Authenticated

**5. Request Payload**: None

**6. Response Payload**: `{ "user_id", "email", "roles", "permissions", "institution_id", "org_id" }`

**7. Database Operations**: None (reads from SecurityContext/JWT claims)

**8. Sequence**: Extract from context → Return

**9. Prerequisite Operations**: Login

---

#### Operation 14–17: MFA Management (via sm_auth → mfa action)

Routed via `m_AAA` → `sm_auth` → `mfa` → `add|view|update|delete`, delegated to `sm_mfa` class.

**Operation 14: Enroll MFA** (`mfa/add`)  
Initiates TOTP enrollment — generates secret, provisioning URI, and backup codes. Or verifies an enrollment challenge.

**Operation 15: View MFA Methods** (`mfa/view`)  
Lists active MFA methods for the user.

**Operation 16: Update MFA** (`mfa/update`)  
Sets primary method or regenerates backup codes.

**Operation 17: Delete MFA Method** (`mfa/delete`)  
Deactivates an MFA method with automatic primary fallback.

*Details: All MFA operations use `TbMfaMethod`, `TbMfaChallenge`, `TbMfaBackupCode`, `TbAuthLog` tables via SQLAlchemy ORM and atomic transactions.*

---

### Submodule: sm_rbac

---

#### Operation 18: Create Role

**3. Routing**: `m_AAA` → `sm_rbac` → `role` → `add`  
**5. Request Payload**: `roleCode` (required), `roleName` (required), `description`, `statusId`  
**7. Database Operations**: INSERT into `sch_iam.tb_role`

#### Operation 19: View Roles

**3. Routing**: `m_AAA` → `sm_rbac` → `role` → `view`  
**7. Database Operations**: SELECT all from `sch_iam.tb_role`

#### Operation 20: Update Role

**3. Routing**: `m_AAA` → `sm_rbac` → `role` → `update`  
**5. Request Payload**: `id` (required), `roleName`, `description`, `statusId`

#### Operation 21: Delete Role

**3. Routing**: `m_AAA` → `sm_rbac` → `role` → `delete`  
**5. Request Payload**: `id` (required)  
**Business Rule**: Block delete if active users assigned (BR-05.1)

#### Operation 22: Assign Roles

**3. Routing**: `m_AAA` → `sm_rbac` → `roleAssignment` → `add`  
**5. Request Payload**: `userOrgId` (required), `orgRoleIds` (array, required)  
**2. Explanation**: Supports bulk role assignment. Returns per-role success/failure results.

#### Operation 23: View Role Assignments

**3. Routing**: `m_AAA` → `sm_rbac` → `roleAssignment` → `view`  
**5. Request Payload**: `userId` (required)

#### Operation 24: Update Role Assignment (Unsupported)

**3. Routing**: `m_AAA` → `sm_rbac` → `roleAssignment` → `update`  
**2. Explanation**: Returns error — updates are unsupported by design. Users must revoke and re-assign to preserve audit trail.

#### Operation 25: Revoke Role Assignment

**3. Routing**: `m_AAA` → `sm_rbac` → `roleAssignment` → `delete`  
**5. Request Payload**: `assignmentId` (required)

#### Operations 26–29: Permission CRUD

**Routing**: `m_AAA` → `sm_rbac` → `permission` → `add|view|update|delete`

| ActionType | Payload | Description |
|-----------|---------|-------------|
| `add` | `permissionCode` (req), `description` | Register a permission |
| `view` | — | List all permissions |
| `update` | `id` (req), `permissionCode` (req), `description` | Update permission |
| `delete` | `id` (req) | Delete permission |

#### Operation 30: View Accessible Modules

**3. Routing**: `m_AAA` → `sm_rbac` → `accessibleModules` → `view`  
**2. Explanation**: Returns navigation metadata (modules and sub-modules) the authenticated user has access to, based on resolved permissions.  
**4. Requirements**: Authenticated  
**7. Database Operations**: Resolves user identity context, user permissions, then fetches accessible modules filtered by permissions.  
**6. Response**: `{ "user": {...}, "modules": [...] }` — modules sorted by displayName.

---

### Submodule: sm_policy

---

#### Operations 31–34: Password Policy CRUD

**Routing**: `m_AAA` → `sm_policy` → `passwordPolicy` → `add|view|update|delete`  
**Data Layer**: `CapabilityRegistry.get_capability("policy_provider")`

| ActionType | Key Payload | Notes |
|-----------|------------|-------|
| `add` | Policy fields + auto-generated id | Creates via `upsert_password_policy` |
| `view` | — | Returns policy for user's institution |
| `update` | `id` (required) + fields | Updates via `upsert_password_policy` |
| `delete` | — | Deletes; platform defaults apply prospectively |

#### Operations 35–38: Session Policy CRUD

**Routing**: `m_AAA` → `sm_policy` → `sessionPolicy` → `add|view|update|delete`  
Same pattern as Password Policy using `upsert_session_policy` / `get_session_policy` / `delete_session_policy`.

#### Operations 39–42: Login Policy CRUD

**Routing**: `m_AAA` → `sm_policy` → `loginPolicy` → `add|view|update|delete`  
Same pattern using `upsert_login_policy` / `get_login_policy` / `delete_login_policy`.

---

<a id="module-m_attendance"></a>
## Module: m_attendance — Attendance Management

**Version**: 1.0.0  
**Submodules**: `sm_configuration`, `sm_records`, `sm_shortage`, `sm_exception`, `sm_leave`  
**Data Layer**: `AttendanceDataLayer` (from `m_attendance_data.py`)  
**DB Schemas**: `sch_attendance`, `sch_lookup`, `sch_curriculum`, `sch_student`

---

### Submodule: sm_configuration

---

#### Operations 43–49: Attendance Configuration (Policy) Management

**Routing**: `m_attendance` → `sm_configuration` → `attendanceConfiguration` → `<actionType>`

| # | ActionType | Operation | Key Payload | Business Rules |
|---|-----------|-----------|------------|----------------|
| 43 | `add` | Create Policy | `instId`, `policyName`, `minAttPercent` (all required) | Single active policy per institution; percent must be 0-100; effectiveTo ≥ effectiveFrom |
| 44 | `view` | View Policies | `policyId` (by ID) or `instId`, `isActive`, `limit`, `offset` (list) | Pagination support |
| 45 | `update` | Update Policy | `policyId` (required) + any field | Prospective only — never retroactive; single-active conflict check when activating |
| 46 | `delete` | Reset Policy (Semantic) | `policyId` (required) | Resets to system defaults (75% threshold); retains row — NOT a SQL DELETE |
| 47 | `activate` | Activate Policy | `policyId` (required) | Auto-deactivates other active policies for same institution |
| 48 | `deactivate` | Deactivate Policy | `policyId` (required) | — |
| 49 | `get_active` | Get Active Policy | `instId` (required) | Returns current active policy for institution |

**Database Tables**: `sch_attendance.tb_att_policy` (CRUD), `sch_lookup.tb_lookup` (status resolution)

---

#### Operations 50–53: Attendance Type Management

**Routing**: `m_attendance` → `sm_configuration` → `attendanceType` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 50 | `add` | `typeCode`, `typeName` (required) | Inserts into `sch_lookup.tb_lookup` (cat_id=70) |
| 51 | `view` | — | Lists all attendance types from lookup |
| 52 | `update` | `typeId` (required), `typeName`/`typeCode`, `isActive` | Updates lookup entry |
| 53 | `delete` | `typeId` (required) | Semantic deactivation (status=False); checks for record references |

---

### Submodule: sm_records

---

#### Operations 54–57: Attendance Session Management

**Routing**: `m_attendance` → `sm_records` → `attendanceSession` → `add|view|update|delete`

| # | ActionType | Operation | Key Payload | Business Rules |
|---|-----------|-----------|------------|----------------|
| 54 | `add` | Create Session | `classSessionId`, `sessionDate` (required) | Dynamic enrollment validation if studentIds provided; sets OPEN status via lookup |
| 55 | `view` | View Sessions | `attSessionId` (by ID) or `classSessionId`, `markedByFacId` (list) | Pagination with limit/offset |
| 56 | `update` | Update Session | `attSessionId` (required) + fields | **Session Lock Invariance**: blocked if locked_at or submitted_at is set |
| 57 | `delete` | Cancel Session (Semantic) | `attSessionId` (required) | Sets status to CANCELLED; blocked if locked/submitted |

---

#### Operations 58–61: Attendance Record Marking

**Routing**: `m_attendance` → `sm_records` → `attendanceRecord` → `add|view|update|delete`

| # | ActionType | Operation | Key Payload | Business Rules |
|---|-----------|-----------|------------|----------------|
| 58 | `add` | Mark Attendance | `attSessionId`, `records[]` (each with `studId`, `attStatusCode`) | Session Lock Invariance; dynamic enrollment validation; atomic bulk insert |
| 59 | `view` | View Records | `recordId` (by ID) or `attSessionId`/`studId` (list) | Pagination |
| 60 | `update` | Correct Records | `attSessionId`, `records[]` (each with `recordId`, `attStatusCode`) | Session Lock Invariance; batch update in transaction |
| 61 | `delete` | Delete Records | `attSessionId`, `recordIds[]`, `reason` (all required) | Session Lock Invariance; audit reason mandatory |

**Database Tables**: `sch_attendance.tb_att_session`, `sch_attendance.tb_att_record`

---

#### Operations 62–65: Attendance Submission Management

**Routing**: `m_attendance` → `sm_records` → `attendanceSubmission` → `add|view|update|delete`

| # | ActionType | Operation | Key Payload | Business Rules |
|---|-----------|-----------|------------|----------------|
| 62 | `add` | Submit & Lock | `attSessionId` (required) | Sets LOCKED status; blocks further edits; triggers shortage recalculation |
| 63 | `view` | Compliance Report | Filters (classSessionId, markedByFacId) | Lists sessions with submission status |
| 64 | `update` | Reopen Session | `attSessionId`, `reason` (both required) | Sets OPEN status; nullifies locked_at; **mandatory reason** |
| 65 | `delete` | Revoke Submission (Semantic) | `attSessionId`, `reason` (both required) | Resets to OPEN state; **mandatory administrative explanation** |

---

### Submodule: sm_shortage

---

#### Operations 66–68: Attendance Shortage Evaluation

**Routing**: `m_attendance` → `sm_shortage` → `attendanceShortage` → `view|update|delete`

| # | ActionType | Operation | Key Payload | Notes |
|---|-----------|-----------|------------|-------|
| 66 | `view` | Evaluate Shortage | `instId`, `studId`/`classSessionId` | Risk stratification: SEVERE / WARNING / SAFE; read-only — does not mutate policy |
| 67 | `update` | Recalculate Shortage | Context-specific | Triggers recalculation against active policy |
| 68 | `delete` | Clear Shortage Data | Context-specific | Administrative operation |

#### Operations 69–72: Condonation Management

**Routing**: `m_attendance` → `sm_shortage` → `condonation` → `add|view|update|delete`

| # | ActionType | Operation | Key Payload | Notes |
|---|-----------|-----------|------------|-------|
| 69 | `add` | Submit Condonation Request | `studId`, `attSessionId`, `reason`, `requestedPercent` | Creates condonation petition |
| 70 | `view` | View Condonation Requests | Filters | Lists with audit trail |
| 71 | `update` | Approve/Reject Condonation | Decision + comments | Updates condonation status |
| 72 | `delete` | Cancel Condonation (Semantic) | Request ID | Semantic cancellation for audit compliance |

---

### Submodule: sm_exception

---

#### Operations 73–76: Date-Range Exception Management

**Routing**: `m_attendance` → `sm_exception` → `attendanceException` → `add|view|update|delete`

| # | ActionType | Operation | Key Payload | Notes |
|---|-----------|-----------|------------|-------|
| 73 | `add` | Submit Exception | `studId`, `startDate`, `endDate`, `reason`, `docPath` | Date-range exception (medical, sports) |
| 74 | `view` | View Exceptions | Filters | Lists exception requests |
| 75 | `update` | Modify Exception | Exception ID + fields | Modify pending exception |
| 76 | `delete` | Withdraw Exception (Semantic) | Exception ID | Retroactive revocation restores original attendance states |

#### Operations 77–79: Exception Approval

**Routing**: `m_attendance` → `sm_exception` → `exceptionApproval` → `add|view|update|delete`

| # | ActionType | Operation | Notes |
|---|-----------|-----------|-------|
| 77 | `add`/`update` | Approve/Reject | Atomic date-range overrides across matching class sessions |
| 78 | `view` | View Approvals | Reuses exception view |
| 79 | `delete` | Revoke Approval | Semantic rejection preserving audit trail |

---

### Submodule: sm_leave

---

#### Operations 80–83: Student Leave Applications

**Routing**: `m_attendance` → `sm_leave` → `studentLeave` → `add|view|update|delete`

| # | ActionType | Key Payload | Required Fields |
|---|-----------|------------|----------------|
| 80 | `add` | `studentId`, `leaveTypeId`, `fromDate`, `toDate`, `reason`, `medicalDocId` | First 5 required |
| 81 | `view` | `studentId` and/or `leaveId` | — |
| 82 | `update` | `leaveId` (required) + fields | — |
| 83 | `delete` | `leaveId` (required) | — |

---

<a id="module-m_curriculum"></a>
## Module: m_curriculum — Curriculum Management

**Version**: 1.0.0  
**Submodules**: `sm_programme`, `sm_course`, `sm_curriculum`, `sm_enrollment`  
**Data Layer**: `CurriculumDataLayer` (from `m_curriculum_data.py`)

---

### Submodule: sm_programme

#### Operations 84–87: Programme CRUD

**Routing**: `m_curriculum` → `sm_programme` → `programme` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 84 | `add` | `programmeCode`, `programmeName`, `departmentId`, `durationYears`, `durationSemesters`, `degreeTypeId` | Validates code uniqueness; creates in `sch_academic_struct.tb_programme` |
| 85 | `view` | `programmeId` or search filters + pagination | — |
| 86 | `update` | `id` (required) + fields | Validates existence |
| 87 | `delete` | `id` (required) | Checks for enrolled students before allowing |

---

### Submodule: sm_course

#### Operations 88–91: Course Definition CRUD

**Routing**: `m_curriculum` → `sm_course` → `courseDefinition` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 88 | `add` | `courseCode`, `courseName`, `credits`, `courseTypeId` + version fields | Creates root course + initial version atomically |
| 89 | `view` | `courseId` or `courseCode` search | — |
| 90 | `update` | `courseId` + fields | — |
| 91 | `delete` | `courseId` | Deactivation if referenced |

#### Operation 92: Course Requisite (Add)

**Routing**: `m_curriculum` → `sm_course` → `courseRequisite` → `add`

#### Operation 93: Course Outcome (Stub)

**Routing**: `m_curriculum` → `sm_course` → `courseOutcome`  
*Implementation is placeholder/stub.*

---

### Submodule: sm_curriculum

#### Operations 94–97: Curriculum Management CRUD

**Routing**: `m_curriculum` → `sm_curriculum` → `curriculumManagement` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 94 | `add` | `programmeId`, `academicYear`, `semester` + course list | Creates curriculum with course mappings atomically |
| 95 | `view` | `curriculumId` or search filters | — |
| 96 | `update` | `curriculumId` + fields | — |
| 97 | `delete` | `curriculumId` | Checks enrollment references |

#### Operations 98–101: Curriculum Approval

**Routing**: `m_curriculum` → `sm_curriculum` → `curriculumApproval` → `add|view|update|delete`

| # | ActionType | Notes |
|---|-----------|-------|
| 98 | `add` | Submit curriculum for approval |
| 99 | `view` | View approval status |
| 100 | `update` | Approve or reject |
| 101 | `delete` | Withdraw submission |

---

### Submodule: sm_enrollment

#### Operations 102–105: Student Enrollment CRUD

**Routing**: `m_curriculum` → `sm_enrollment` → `enrollment` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 102 | `add` | `studentId`, `programmeId`, `admissionDate`, `batchYear` | Creates enrollment with status tracking |
| 103 | `view` | `enrollmentId` or filters | — |
| 104 | `update` | `enrollmentId` + status/fields | — |
| 105 | `delete` | `enrollmentId` | Cancellation with reason |

#### Operations 106–109: Semester Registration CRUD

**Routing**: `m_curriculum` → `sm_enrollment` → `semesterRegistration` → `add|view|update|delete`

#### Operations 110–113: Elective Registration CRUD

**Routing**: `m_curriculum` → `sm_enrollment` → `electiveRegistration` → `add|view|update|delete`

---

<a id="module-m_exam"></a>
## Module: m_exam — Examinations & Results

**Version**: 1.0.0  
**Submodules**: 16 submodules (exam_center, schedule, seating, invigilation, hall_ticket, question_paper, external_exam, internal_exam, marks, evaluation, results, result_approval, revaluation, supplementary, reappear, malpractice)  
**Data Layer**: `ExamDataLayer` (from `m_exam_data.py`)  
**DB Schemas**: `sch_exam`, `sch_student`, `sch_core`, `sch_iam`, `sch_parents`, `sch_emp_fac`

> [!NOTE]
> All exam submodules use the `(action_type, payload, context)` signature pattern (legacy/self-based classes).

---

#### Operations 114–117: Exam Center CRUD

**Routing**: `m_exam` → `exam_center` → `exam_center` → `add|view|update|delete`  
Manages physical exam venue records (name, capacity, location, facilities).

#### Operations 118–122: Exam Schedule Management

**Routing**: `m_exam` → `schedule` → `exam_schedule` → `add|view|update|delete|publish`  
**Additional Action**: `exam_schedule_publication` → `view|hold|unpublish`  
Manages exam timetable entries with date, time, venue, course. Supports publish/unpublish lifecycle.

#### Operations 123–126: Seating Arrangement

**Routing**: `m_exam` → `seating` → `seating` → `add|view|update|delete`  
Generates/manages seat assignments for students in exam centers.

#### Operations 127–130: Invigilation Assignment

**Routing**: `m_exam` → `invigilation` → `invigilation` → `add|view|update|delete`  
Assigns faculty invigilators to exam sessions/rooms.

#### Operations 131–134: Hall Ticket Management

**Routing**: `m_exam` → `hall_ticket` → `hall_ticket` → `add|view|update|delete`  
Generates admit cards/hall tickets with student details, exam schedule, and photo.

#### Operations 135–138: Question Paper Management

**Routing**: `m_exam` → `question_paper` → `question_paper` → `add|view|update|delete`  
**Additional Action**: `question_paper_approval` → `add|view|update|delete`  
Manages question paper creation and approval workflow.

#### Operations 139–142: External Exam Management

**Routing**: `m_exam` → `external_exam` → `external_exam` → `add|view|update|delete`

#### Operations 143–146: Internal Exam Management

**Routing**: `m_exam` → `internal_exam` → `internal_exam` → `add|view|update|delete`

#### Operations 147–150: Marks Entry & Verification

**Routing**: `m_exam` → `marks` → `marks_entry|marks_verification` → `add|view|update|delete`

#### Operations 151–154: Evaluation Management

**Routing**: `m_exam` → `evaluation` → `evaluation_assignment|evaluation_grading` → `add|view|update|delete`

#### Operations 155–158: Results Generation

**Routing**: `m_exam` → `results` → `results` → `add|view|update|delete`

#### Operations 159–162: Result Approval

**Routing**: `m_exam` → `result_approval` → `result_approval|result_publication` → `add|view|update|delete`

#### Operations 163–172: Revaluation Suite

**Routing**: `m_exam` → `revaluation` → multiple actions:
- `revaluation_request` → `add|view|update|delete`
- `revaluation_processing` → `add|view|update|delete`
- `photocopy_request` → `add|view|update|delete`
- `appeal` → `add|view|update|delete`
- `challenge_revaluation` → `add|view|update|delete`

#### Operations 173–176: Supplementary Exams

**Routing**: `m_exam` → `supplementary` → `supplementary_exam|supplementary_registration` → `add|view|update|delete`

#### Operations 177–180: Reappear Exams

**Routing**: `m_exam` → `reappear` → `reappear` → `add|view|update|delete`

#### Operations 181–184: Malpractice Cases

**Routing**: `m_exam` → `malpractice` → `malpractice` → `add|view|update|delete`

---

<a id="module-m_fees"></a>
## Module: m_fees — Fee Lifecycle Management

**Version**: 1.0.0  
**Submodules**: `sm_fee_structure`, `sm_fee_assignment`, `sm_concession`, `sm_invoice`, `sm_payment`, `sm_refund`, `sm_penalty`  
**Data Layer**: `FeesDataLayer` (from `m_fees_data.py`)  
**DB Schemas**: `sch_fees`

---

#### Operations 185–188: Fee Structure CRUD

**Routing**: `m_fees` → `sm_fee_structure` → `feeStructure` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 185 | `add` | `name`, `academicYearId`, `programmeId`, `components[]` | Creates fee structure with component breakdown |
| 186 | `view` | `feeStructureId` or filters | Returns with component details |
| 187 | `update` | `feeStructureId` + fields | — |
| 188 | `delete` | `feeStructureId` | Checks for existing assessments |

#### Operations 189–192: Fee Assignment CRUD

**Routing**: `m_fees` → `sm_fee_assignment` → `feeAssignment` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 189 | `add` | `feeStructureId`, `studentIds[]` or `programmeId`+`batchYear` | Bulk assessment creation |
| 190 | `view` | `studentId` or filters | Returns assessments with components |
| 191 | `update` | `assessmentId` + fields | — |
| 192 | `delete` | `assessmentId` | — |

#### Operations 193–196: Fee Concession (Scholarships/Waivers) CRUD

**Routing**: `m_fees` → `sm_concession` → `feeConcession` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 193 | `add` | `studentId`, `concessionTypeId`, `amount`/`percentage`, `reason` | Creates scholarship or concession record |
| 194 | `view` | `studentId` or concession filters | — |
| 195 | `update` | `concessionId` + fields | — |
| 196 | `delete` | `concessionId` | — |

#### Operations 197–200: Invoice CRUD

**Routing**: `m_fees` → `sm_invoice` → `feeInvoice` → `add|view|update|delete`

#### Operations 201–204: Payment Processing

**Routing**: `m_fees` → `sm_payment` → `feePayment` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 201 | `add` | `studentId`, `amount`, `paymentMethodId`, `transactionRef` | Records payment with ledger entries; calculates running balance; handles overpayment detection |
| 202 | `view` | `studentId` or payment filters | — |
| 203 | `update` | Payment ID + fields | — |
| 204 | `delete` | Payment ID | Reversal with ledger adjustment |

#### Operations 205–208: Refund Management

**Routing**: `m_fees` → `sm_refund` → `feeRefund` → `add|view|update|delete`

| # | ActionType | Notes |
|---|-----------|-------|
| 205 | `add` | Initiates refund request |
| 206 | `view` | View refund status |
| 207 | `update` | Approve/process refund (finance approval if configured) |
| 208 | `delete` | Cancel refund request |

#### Operations 209–212: Penalty (Late Fees) Management

**Routing**: `m_fees` → `sm_penalty` → `feePenalty` → `add|view|update|delete`

---

<a id="module-m_profile"></a>
## Module: m_profile — User Profile Management

**Version**: 1.0.0  
**Submodules**: `sm_personal_detail`, `sm_academic_detail`, `sm_family_detail`, `sm_medical_detail`, `sm_settings`  
**Data Layer**: `ProfileDataLayer` (from `m_profile_data.py`)  
**DB Schemas**: `sch_iam`, `sch_core`, `sch_student`, `sch_emp_fac`, `sch_parents`, `sch_medical`

---

### Submodule: sm_personal_detail

#### Operations 213–216: Personal Detail CRUD

**Routing**: `m_profile` → `sm_personal_detail` → `personalDetail` → `add|view|update|delete`

| # | ActionType | Notes |
|---|-----------|-------|
| 213 | `add` | Creates user profile (first name, last name, DOB, gender, mobile, address, etc.) with mobile uniqueness check |
| 214 | `view` | Returns comprehensive profile including identity, student/employee records |
| 215 | `update` | Partial updates with field-level validation and mobile uniqueness |
| 216 | `delete` | GDPR-compliant anonymisation (replaces PII with anonymised values) |

---

### Submodule: sm_academic_detail

#### Operations 217–220: Academic Detail CRUD

**Routing**: `m_profile` → `sm_academic_detail` → `academicDetail` → `add|view|update|delete`  
Manages academic identifiers, student records, and enrollment metadata.

---

### Submodule: sm_family_detail

#### Operations 221–224: Family Detail CRUD

**Routing**: `m_profile` → `sm_family_detail` → `familyDetail` → `add|view|update|delete`  
Manages parent/guardian information (relationship, occupation, contact).

#### Operations 225–228: Emergency Contact CRUD

**Routing**: `m_profile` → `sm_family_detail` → `emergencyContact` → `add|view|update|delete`

---

### Submodule: sm_medical_detail

#### Operations 229–232: Medical Detail CRUD

**Routing**: `m_profile` → `sm_medical_detail` → `medicalDetail` → `add|view|update|delete`  
Manages medical records (blood group, allergies, medications, chronic conditions, disabilities, insurance).

---

### Submodule: sm_settings

#### Operations 233–236: User Preferences CRUD

**Routing**: `m_profile` → `sm_settings` → `userPreference` (or `settings`) → `add|view|update|delete`  
Manages user settings (theme, language, notification preferences, timezone).

---

<a id="module-m_super_admin"></a>
## Module: m_super_admin — Super Administration

**Version**: N/A (no manifest version)  
**Submodules**: `sm_mods`, `sm_sub_mods`, `sm_action`, `sm_config`, `sm_mdm_edu`  
**Routing Pattern**: Uses legacy `SuperAdmin.__call__()` router with `(action_type, payload, context)` signature

> [!WARNING]
> This module performs **filesystem operations** (create/rename/delete directories and Python files). It uses `read`, `create`, `update`, `delete` action types (not the standard `add`/`view`).

---

### Submodule: sm_mods

#### Operations 237–241: Module Lifecycle Management

**Routing**: `m_super_admin` → `sm_mods` → `mods` → `health|create|read|update|delete`

| # | ActionType | Operation | Notes |
|---|-----------|-----------|-------|
| 237 | `health` | Health Check | Returns `{ "health": "good" }` |
| 238 | `create` | Create Module | Creates `modules/m_<name>/` directory + entry-point `.py` file |
| 239 | `read` | List Modules | Lists all `m_*` directories under `modules/` |
| 240 | `update` | Rename Module | Renames directory + all contained files |
| 241 | `delete` | Delete Module | Recursively removes module directory (shutil.rmtree) |

---

### Submodule: sm_sub_mods

#### Operations 242–246: Submodule Lifecycle Management

**Routing**: `m_super_admin` → `sm_sub_mods` → `sub_mods` → `health|create|read|update|delete`

| # | ActionType | Operation | Notes |
|---|-----------|-----------|-------|
| 242 | `health` | Health Check | — |
| 243 | `create` | Create Submodule | Creates `m_<mod>_sm_<name>.py` file |
| 244 | `read` | List Submodules | Globs `m_<mod>_sm_*.py` files |
| 245 | `update` | Rename Submodule | Renames file + updates internal references |
| 246 | `delete` | Delete Submodule | Deletes file (unlink) |

---

### Submodule: sm_action

#### Operations 247–250: Action Method Introspection & Code Generation

**Routing**: `m_super_admin` → `sm_action` → `action` → `read|create|update|delete`

| # | ActionType | Operation | Notes |
|---|-----------|-----------|-------|
| 247 | `read` | List Actions | Uses Python `inspect` to list public methods on handler class |
| 248 | `create` | Create Action | Injects method into submodule file via `CodeEditor` |
| 249 | `update` | Rename Action | String-replaces `def old_name(` → `def new_name(` |
| 250 | `delete` | Delete Action | Parses AST, removes function node, re-serializes |

---

### Submodule: sm_config

#### Operations 251–253: Configuration Variable Management

**Routing**: `m_super_admin` → `sm_config` → `config` → `read|update|delete`

| # | ActionType | Operation | Key Payload | Notes |
|---|-----------|-----------|------------|-------|
| 251 | `read` | Read Config | `config_file_name` | Reads variables from `xsc_conf/oa_<name>.py` via `CodeEditor` |
| 252 | `update` | Update Config | `config_file_name`, `variable_name`, `variable_value` | Updates variable value in config file |
| 253 | `delete` | Delete Config Var | `config_file_name`, `variable_name` | Removes variable from config file |

---

### Submodule: sm_mdm_edu

#### Operations 254–259: College Master Data Management

**Routing**: `m_super_admin` → `sm_mdm_edu` → `mdm_edu` → `health|read|search|create|update|delete`

| # | ActionType | Operation | Key Payload | Notes |
|---|-----------|-----------|------------|-------|
| 254 | `health` | Health Check | — | — |
| 255 | `read` | List Colleges | `page_no`, `items_per_page` | Paginated, direct SQL via psycopg |
| 256 | `search` | Search Colleges | `search` (text, required) | ILIKE pattern matching on college_name |
| 257 | `create` | Create College | `college_name`, `short_form`, `website`, `year_founded`, `university_type`, `type_of_college`, `college_tier` | INSERT with RETURNING id |
| 258 | `update` | Update College | `id` + all fields | Full column update |
| 259 | `delete` | Delete College | `id` (required) | Physical SQL DELETE |

---

<a id="module-m_timetable"></a>
## Module: m_timetable — Timetable Management

**Version**: 1.0.0  
**Submodules**: `sm_configuration`, `sm_schedule`, `sm_allocation`, `sm_substitution`, `sm_approval`  
**Data Layer**: `TimetableDataLayer` (from `m_timetable_data.py`)  
**DB Schemas**: `sch_timetable`, `sch_academic_struct`, `sch_course_ops`, `sch_infra`, `sch_lookup`, `sch_org`

---

### Submodule: sm_configuration

#### Operations 260–263: Working Day Configuration

**Routing**: `m_timetable` → `sm_configuration` → `working_day` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 260 | `add` | `institutionId`, `dayOfWeek`, `isWorkingDay`, `effectiveFrom`, `effectiveTo` | Overlap detection across date ranges; prevents duplicate day-of-week entries |
| 261 | `view` | `institutionId` or `workingDayId` | — |
| 262 | `update` | `workingDayId` + fields | Validates no overlap |
| 263 | `delete` | `workingDayId` | Checks dependencies (time slots referencing this working day) before deactivation |

#### Operations 264–267: Time Slot Configuration

**Routing**: `m_timetable` → `sm_configuration` → `time_slot` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 264 | `add` | `institutionId`, `slotNumber`, `startTime`, `endTime`, `slotTypeId` | Time overlap detection; validates startTime < endTime |
| 265 | `view` | Filters | — |
| 266 | `update` | `timeSlotId` + fields | Overlap validation |
| 267 | `delete` | `timeSlotId` | Dependency check before deactivation |

#### Operations 268–271: Academic Calendar Configuration

**Routing**: `m_timetable` → `sm_configuration` → `academic_calendar` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 268 | `add` | `institutionId`, `calendarName`, `startDate`, `endDate`, `academicYearId` | Date range validation; uniqueness checks |
| 269 | `view` | Filters | — |
| 270 | `update` | Calendar ID + fields | — |
| 271 | `delete` | Calendar ID | Dependency checks |

---

### Submodule: sm_schedule

#### Operations 272–275: Timetable Entry CRUD

**Routing**: `m_timetable` → `sm_schedule` → `timetable` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 272 | `add` | `institutionId`, `academicCalendarId`, `entries[]` (each with dayOfWeek, timeSlotId, courseId, sectionId) | Validates each entry for conflicts (room, faculty, section clashes); batch creation |
| 273 | `view` | `timetableId` or filters (institutionId, sectionId, facultyId, date range) | Multiple view modes |
| 274 | `update` | `timetableEntryId` + fields | Conflict re-validation |
| 275 | `delete` | `timetableEntryId` | Checks if approved before allowing |

---

### Submodule: sm_allocation

#### Operations 276–279: Faculty Allocation

**Routing**: `m_timetable` → `sm_allocation` → `faculty_allocation` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 276 | `add` | `timetableEntryId`, `facultyId`, `isPrimary` | Validates faculty availability/conflicts |
| 277 | `view` | Filters (facultyId, institutionId, date range) | — |
| 278 | `update` | Allocation ID + fields | — |
| 279 | `delete` | Allocation ID | — |

#### Operations 280–283: Room Allocation

**Routing**: `m_timetable` → `sm_allocation` → `room_allocation` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 280 | `add` | `timetableEntryId`, `roomId` | Room capacity and conflict validation |
| 281 | `view` | Filters | — |
| 282 | `update` | Allocation ID + fields | Conflict re-check |
| 283 | `delete` | Allocation ID | — |

---

### Submodule: sm_substitution

#### Operations 284–287: Faculty Substitution

**Routing**: `m_timetable` → `sm_substitution` → `substitution` → `add|view|update|delete`

| # | ActionType | Key Payload | Notes |
|---|-----------|------------|-------|
| 284 | `add` | `timetableEntryId`, `originalFacultyId`, `substituteFacultyId`, `date`, `reason` | Validates substitute availability |
| 285 | `view` | Filters (date, faculty, status) | — |
| 286 | `update` | Substitution ID + fields | — |
| 287 | `delete` | Substitution ID | — |

---

### Submodule: sm_approval

#### Operations 288–291: Timetable Approval Workflow

**Routing**: `m_timetable` → `sm_approval` → `timetable_approval` → `add|view|update|delete`

| # | ActionType | Operation | Notes |
|---|-----------|-----------|-------|
| 288 | `add` | Submit for Approval | Validates timetable completeness, creates approval request |
| 289 | `view` | View Approval Status | Lists pending/approved/rejected requests |
| 290 | `update` | Approve/Reject | Records decision with comments |
| 291 | `delete` | Withdraw Submission | Cancels pending approval request |

---

<a id="final-summary"></a>
## Final Summary

### Counts

| Metric | Count |
|--------|-------|
| **Total Modules** | 8 |
| **Total Submodules** | 27 |
| **Total Operations** | ~291 |
| **Total Unique Actions** | ~75 |
| **Total Action Types** | add, view, update, delete, activate, deactivate, get_active, health, create, read, search, publish, hold, unpublish |

### Module Breakdown

| Module | Submodules | Operations |
|--------|------------|------------|
| m_AAA | 3 (sm_auth, sm_rbac, sm_policy) | 42 |
| m_attendance | 5 (sm_configuration, sm_records, sm_shortage, sm_exception, sm_leave) | 41 |
| m_curriculum | 4 (sm_programme, sm_course, sm_curriculum, sm_enrollment) | 30 |
| m_exam | 16 | ~72 |
| m_fees | 7 | 28 |
| m_profile | 5 (sm_personal_detail, sm_academic_detail, sm_family_detail, sm_medical_detail, sm_settings) | 24 |
| m_super_admin | 5 (sm_mods, sm_sub_mods, sm_action, sm_config, sm_mdm_edu) | 23 |
| m_timetable | 5 (sm_configuration, sm_schedule, sm_allocation, sm_substitution, sm_approval) | 32 |

---

### Operation Index

| # | Operation | Module | Submodule | Action | Action Type |
|---|----------|--------|-----------|--------|-------------|
| 1 | Login / Create Session | m_AAA | sm_auth | session | add |
| 2 | View Active Sessions | m_AAA | sm_auth | session | view |
| 3 | Refresh Session | m_AAA | sm_auth | session | update |
| 4 | Logout | m_AAA | sm_auth | session | delete |
| 5 | Set Password | m_AAA | sm_auth | password | add |
| 6 | Validate Password Strength | m_AAA | sm_auth | password | view |
| 7 | Change Password | m_AAA | sm_auth | password | update |
| 8 | Expire Password | m_AAA | sm_auth | password | delete |
| 9 | Initiate Password Reset | m_AAA | sm_auth | passwordReset | add |
| 10 | Validate Reset Token | m_AAA | sm_auth | passwordReset | view |
| 11 | Execute Password Reset | m_AAA | sm_auth | passwordReset | update |
| 12 | Cancel Password Reset | m_AAA | sm_auth | passwordReset | delete |
| 13 | View Current User | m_AAA | sm_auth | user | view |
| 14 | Enroll MFA | m_AAA | sm_auth | mfa | add |
| 15 | View MFA Methods | m_AAA | sm_auth | mfa | view |
| 16 | Update MFA (Primary/Backup) | m_AAA | sm_auth | mfa | update |
| 17 | Delete MFA Method | m_AAA | sm_auth | mfa | delete |
| 18 | Create Role | m_AAA | sm_rbac | role | add |
| 19 | View Roles | m_AAA | sm_rbac | role | view |
| 20 | Update Role | m_AAA | sm_rbac | role | update |
| 21 | Delete Role | m_AAA | sm_rbac | role | delete |
| 22 | Assign Roles (Bulk) | m_AAA | sm_rbac | roleAssignment | add |
| 23 | View Role Assignments | m_AAA | sm_rbac | roleAssignment | view |
| 24 | Update Role Assignment (Unsupported) | m_AAA | sm_rbac | roleAssignment | update |
| 25 | Revoke Role Assignment | m_AAA | sm_rbac | roleAssignment | delete |
| 26 | Register Permission | m_AAA | sm_rbac | permission | add |
| 27 | View Permissions | m_AAA | sm_rbac | permission | view |
| 28 | Update Permission | m_AAA | sm_rbac | permission | update |
| 29 | Delete Permission | m_AAA | sm_rbac | permission | delete |
| 30 | View Accessible Modules | m_AAA | sm_rbac | accessibleModules | view |
| 31 | Create Password Policy | m_AAA | sm_policy | passwordPolicy | add |
| 32 | View Password Policy | m_AAA | sm_policy | passwordPolicy | view |
| 33 | Update Password Policy | m_AAA | sm_policy | passwordPolicy | update |
| 34 | Delete Password Policy | m_AAA | sm_policy | passwordPolicy | delete |
| 35 | Create Session Policy | m_AAA | sm_policy | sessionPolicy | add |
| 36 | View Session Policy | m_AAA | sm_policy | sessionPolicy | view |
| 37 | Update Session Policy | m_AAA | sm_policy | sessionPolicy | update |
| 38 | Delete Session Policy | m_AAA | sm_policy | sessionPolicy | delete |
| 39 | Create Login Policy | m_AAA | sm_policy | loginPolicy | add |
| 40 | View Login Policy | m_AAA | sm_policy | loginPolicy | view |
| 41 | Update Login Policy | m_AAA | sm_policy | loginPolicy | update |
| 42 | Delete Login Policy | m_AAA | sm_policy | loginPolicy | delete |
| 43 | Create Attendance Policy | m_attendance | sm_configuration | attendanceConfiguration | add |
| 44 | View Attendance Policies | m_attendance | sm_configuration | attendanceConfiguration | view |
| 45 | Update Attendance Policy | m_attendance | sm_configuration | attendanceConfiguration | update |
| 46 | Reset Attendance Policy (Semantic Delete) | m_attendance | sm_configuration | attendanceConfiguration | delete |
| 47 | Activate Attendance Policy | m_attendance | sm_configuration | attendanceConfiguration | activate |
| 48 | Deactivate Attendance Policy | m_attendance | sm_configuration | attendanceConfiguration | deactivate |
| 49 | Get Active Attendance Policy | m_attendance | sm_configuration | attendanceConfiguration | get_active |
| 50 | Create Attendance Type | m_attendance | sm_configuration | attendanceType | add |
| 51 | View Attendance Types | m_attendance | sm_configuration | attendanceType | view |
| 52 | Update Attendance Type | m_attendance | sm_configuration | attendanceType | update |
| 53 | Delete Attendance Type (Semantic) | m_attendance | sm_configuration | attendanceType | delete |
| 54 | Create Attendance Session | m_attendance | sm_records | attendanceSession | add |
| 55 | View Attendance Sessions | m_attendance | sm_records | attendanceSession | view |
| 56 | Update Attendance Session | m_attendance | sm_records | attendanceSession | update |
| 57 | Cancel Attendance Session (Semantic) | m_attendance | sm_records | attendanceSession | delete |
| 58 | Mark Attendance (Bulk) | m_attendance | sm_records | attendanceRecord | add |
| 59 | View Attendance Records | m_attendance | sm_records | attendanceRecord | view |
| 60 | Correct Attendance Records (Bulk) | m_attendance | sm_records | attendanceRecord | update |
| 61 | Delete Attendance Records | m_attendance | sm_records | attendanceRecord | delete |
| 62 | Submit & Lock Session | m_attendance | sm_records | attendanceSubmission | add |
| 63 | View Submission Compliance | m_attendance | sm_records | attendanceSubmission | view |
| 64 | Reopen Submitted Session | m_attendance | sm_records | attendanceSubmission | update |
| 65 | Revoke Submission (Semantic) | m_attendance | sm_records | attendanceSubmission | delete |
| 66 | View Attendance Shortage | m_attendance | sm_shortage | attendanceShortage | view |
| 67 | Recalculate Shortage | m_attendance | sm_shortage | attendanceShortage | update |
| 68 | Clear Shortage Data | m_attendance | sm_shortage | attendanceShortage | delete |
| 69 | Submit Condonation Request | m_attendance | sm_shortage | condonation | add |
| 70 | View Condonation Requests | m_attendance | sm_shortage | condonation | view |
| 71 | Approve/Reject Condonation | m_attendance | sm_shortage | condonation | update |
| 72 | Cancel Condonation (Semantic) | m_attendance | sm_shortage | condonation | delete |
| 73 | Submit Attendance Exception | m_attendance | sm_exception | attendanceException | add |
| 74 | View Attendance Exceptions | m_attendance | sm_exception | attendanceException | view |
| 75 | Modify Pending Exception | m_attendance | sm_exception | attendanceException | update |
| 76 | Withdraw Exception (Semantic) | m_attendance | sm_exception | attendanceException | delete |
| 77 | Approve/Reject Exception | m_attendance | sm_exception | exceptionApproval | add/update |
| 78 | View Exception Approvals | m_attendance | sm_exception | exceptionApproval | view |
| 79 | Revoke Exception Approval | m_attendance | sm_exception | exceptionApproval | delete |
| 80 | Submit Leave Application | m_attendance | sm_leave | studentLeave | add |
| 81 | View Leave Applications | m_attendance | sm_leave | studentLeave | view |
| 82 | Update Leave Application | m_attendance | sm_leave | studentLeave | update |
| 83 | Delete Leave Application | m_attendance | sm_leave | studentLeave | delete |
| 84 | Create Programme | m_curriculum | sm_programme | programme | add |
| 85 | View Programmes | m_curriculum | sm_programme | programme | view |
| 86 | Update Programme | m_curriculum | sm_programme | programme | update |
| 87 | Delete Programme | m_curriculum | sm_programme | programme | delete |
| 88 | Create Course | m_curriculum | sm_course | courseDefinition | add |
| 89 | View Courses | m_curriculum | sm_course | courseDefinition | view |
| 90 | Update Course | m_curriculum | sm_course | courseDefinition | update |
| 91 | Delete Course | m_curriculum | sm_course | courseDefinition | delete |
| 92 | Add Course Requisite | m_curriculum | sm_course | courseRequisite | add |
| 93 | Course Outcome (Stub) | m_curriculum | sm_course | courseOutcome | — |
| 94 | Create Curriculum | m_curriculum | sm_curriculum | curriculumManagement | add |
| 95 | View Curriculum | m_curriculum | sm_curriculum | curriculumManagement | view |
| 96 | Update Curriculum | m_curriculum | sm_curriculum | curriculumManagement | update |
| 97 | Delete Curriculum | m_curriculum | sm_curriculum | curriculumManagement | delete |
| 98 | Submit Curriculum for Approval | m_curriculum | sm_curriculum | curriculumApproval | add |
| 99 | View Curriculum Approval | m_curriculum | sm_curriculum | curriculumApproval | view |
| 100 | Approve/Reject Curriculum | m_curriculum | sm_curriculum | curriculumApproval | update |
| 101 | Withdraw Curriculum Submission | m_curriculum | sm_curriculum | curriculumApproval | delete |
| 102 | Create Enrollment | m_curriculum | sm_enrollment | enrollment | add |
| 103 | View Enrollments | m_curriculum | sm_enrollment | enrollment | view |
| 104 | Update Enrollment | m_curriculum | sm_enrollment | enrollment | update |
| 105 | Delete Enrollment | m_curriculum | sm_enrollment | enrollment | delete |
| 106 | Register for Semester | m_curriculum | sm_enrollment | semesterRegistration | add |
| 107 | View Semester Registration | m_curriculum | sm_enrollment | semesterRegistration | view |
| 108 | Update Semester Registration | m_curriculum | sm_enrollment | semesterRegistration | update |
| 109 | Delete Semester Registration | m_curriculum | sm_enrollment | semesterRegistration | delete |
| 110 | Register Elective | m_curriculum | sm_enrollment | electiveRegistration | add |
| 111 | View Elective Registration | m_curriculum | sm_enrollment | electiveRegistration | view |
| 112 | Update Elective Registration | m_curriculum | sm_enrollment | electiveRegistration | update |
| 113 | Delete Elective Registration | m_curriculum | sm_enrollment | electiveRegistration | delete |
| 237 | Module Health Check | m_super_admin | sm_mods | mods | health |
| 238 | Create Module | m_super_admin | sm_mods | mods | create |
| 239 | List Modules | m_super_admin | sm_mods | mods | read |
| 240 | Rename Module | m_super_admin | sm_mods | mods | update |
| 241 | Delete Module | m_super_admin | sm_mods | mods | delete |
| 242 | SubModule Health Check | m_super_admin | sm_sub_mods | sub_mods | health |
| 243 | Create SubModule | m_super_admin | sm_sub_mods | sub_mods | create |
| 244 | List SubModules | m_super_admin | sm_sub_mods | sub_mods | read |
| 245 | Rename SubModule | m_super_admin | sm_sub_mods | sub_mods | update |
| 246 | Delete SubModule | m_super_admin | sm_sub_mods | sub_mods | delete |
| 247 | List Actions | m_super_admin | sm_action | action | read |
| 248 | Create Action | m_super_admin | sm_action | action | create |
| 249 | Rename Action | m_super_admin | sm_action | action | update |
| 250 | Delete Action | m_super_admin | sm_action | action | delete |
| 251 | Read Config Variables | m_super_admin | sm_config | config | read |
| 252 | Update Config Variable | m_super_admin | sm_config | config | update |
| 253 | Delete Config Variable | m_super_admin | sm_config | config | delete |
| 254 | MDM Edu Health Check | m_super_admin | sm_mdm_edu | mdm_edu | health |
| 255 | List Colleges (Paginated) | m_super_admin | sm_mdm_edu | mdm_edu | read |
| 256 | Search Colleges | m_super_admin | sm_mdm_edu | mdm_edu | search |
| 257 | Create College | m_super_admin | sm_mdm_edu | mdm_edu | create |
| 258 | Update College | m_super_admin | sm_mdm_edu | mdm_edu | update |
| 259 | Delete College | m_super_admin | sm_mdm_edu | mdm_edu | delete |
| 260 | Add Working Day | m_timetable | sm_configuration | working_day | add |
| 261 | View Working Days | m_timetable | sm_configuration | working_day | view |
| 262 | Update Working Day | m_timetable | sm_configuration | working_day | update |
| 263 | Delete Working Day | m_timetable | sm_configuration | working_day | delete |
| 264 | Add Time Slot | m_timetable | sm_configuration | time_slot | add |
| 265 | View Time Slots | m_timetable | sm_configuration | time_slot | view |
| 266 | Update Time Slot | m_timetable | sm_configuration | time_slot | update |
| 267 | Delete Time Slot | m_timetable | sm_configuration | time_slot | delete |
| 268 | Add Academic Calendar | m_timetable | sm_configuration | academic_calendar | add |
| 269 | View Academic Calendars | m_timetable | sm_configuration | academic_calendar | view |
| 270 | Update Academic Calendar | m_timetable | sm_configuration | academic_calendar | update |
| 271 | Delete Academic Calendar | m_timetable | sm_configuration | academic_calendar | delete |
| 272 | Add Timetable Entry | m_timetable | sm_schedule | timetable | add |
| 273 | View Timetable | m_timetable | sm_schedule | timetable | view |
| 274 | Update Timetable Entry | m_timetable | sm_schedule | timetable | update |
| 275 | Delete Timetable Entry | m_timetable | sm_schedule | timetable | delete |
| 276 | Add Faculty Allocation | m_timetable | sm_allocation | faculty_allocation | add |
| 277 | View Faculty Allocations | m_timetable | sm_allocation | faculty_allocation | view |
| 278 | Update Faculty Allocation | m_timetable | sm_allocation | faculty_allocation | update |
| 279 | Delete Faculty Allocation | m_timetable | sm_allocation | faculty_allocation | delete |
| 280 | Add Room Allocation | m_timetable | sm_allocation | room_allocation | add |
| 281 | View Room Allocations | m_timetable | sm_allocation | room_allocation | view |
| 282 | Update Room Allocation | m_timetable | sm_allocation | room_allocation | update |
| 283 | Delete Room Allocation | m_timetable | sm_allocation | room_allocation | delete |
| 284 | Add Substitution | m_timetable | sm_substitution | substitution | add |
| 285 | View Substitutions | m_timetable | sm_substitution | substitution | view |
| 286 | Update Substitution | m_timetable | sm_substitution | substitution | update |
| 287 | Delete Substitution | m_timetable | sm_substitution | substitution | delete |
| 288 | Submit Timetable for Approval | m_timetable | sm_approval | timetable_approval | add |
| 289 | View Timetable Approval | m_timetable | sm_approval | timetable_approval | view |
| 290 | Approve/Reject Timetable | m_timetable | sm_approval | timetable_approval | update |
| 291 | Withdraw Timetable Approval | m_timetable | sm_approval | timetable_approval | delete |

> [!NOTE]
> The m_exam module operations (114–184) follow the same CRUD pattern across 16 submodules. Each submodule exposes 1–5 actions with `add|view|update|delete` action types plus domain-specific types like `publish`, `hold`, and `unpublish`.

---

*End of Knowledge Base*
