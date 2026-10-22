# m_AAA API Contract

**Version:** 2.0  
**Last verified:** 2026-07-29  
**Module:** `m_AAA`  
**Base URL:** `https://dev.globaloneapp.com` (local default: `http://127.0.0.1:8000`)

This document describes the Authentication, Authorization, and Access Control module (`m_AAA`) API surface, covering user login/session management, Multi-Factor Authentication (MFA), Role-Based Access Control (RBAC), and security policies.

---

## 1. Transport & Common Request Format

All operations use the central framework gateway (`POST /`) with standard request wrapper:

```json
{
  "mod": "m_AAA",
  "subMod": "sm_auth",
  "action": "session",
  "actionType": "add",
  "payload": {}
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `mod` | string | Yes | Must be `m_AAA`. |
| `subMod` | string | Yes | Must be one of: `sm_auth`, `sm_rbac`, `sm_policy`. |
| `action` | string | Yes | Submodule action string (`session`, `mfa`, `rbac`, `policy`). |
| `actionType` | string | Yes | One of `add`, `view`, `update`, `delete`. |
| `payload` | object | Yes | Operation-specific request payload. |

---

## 2. Submodule Index

| Submodule (`subMod`) | Action (`action`) | Supported Action Types | Description |
|---|---|---|---|
| `sm_auth` | `session` | `add`, `view`, `update`, `delete` | Login, session validation, token refresh, logout |
| `sm_auth` | `mfa` | `add`, `view`, `update`, `delete` | MFA registration, status, verification, disable |
| `sm_rbac` | `rbac` | `add`, `view`, `update`, `delete` | Roles and permission management |
| `sm_policy` | `policy` | `add`, `view`, `update`, `delete` | Password & security policy configuration |

---

## 3. Submodule: Authentication & Sessions (`sm_auth`)

Use `subMod: "sm_auth"` and `action: "session"`.

### 3.1 `add` — User Login / Create Session

#### Request Payload
```json
{
  "mod": "m_AAA",
  "subMod": "sm_auth",
  "action": "session",
  "actionType": "add",
  "payload": {
    "username": "admin@example.com",
    "password": "SecurePassword123!",
    "captchaToken": "CAPTCHA-TOKEN-XYZ"
  }
}
```

#### Payload Fields
| Field | Type | Required | Description |
|---|---|---:|---|
| `username` | string | Yes | Registered email or username. |
| `password` | string | Yes | Plaintext user password. |
| `captchaToken` | string | Conditional | Required if `XSC_CAPTCHA_ENABLED` is `true`. |

#### Success Response
```json
{
  "status": "success",
  "message": "Authentication successful",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "tokenType": "Bearer",
    "expiresIn": 86400,
    "user": {
      "userId": 1,
      "email": "admin@example.com",
      "roles": ["SUPER_ADMIN"],
      "institutionId": 1
    }
  }
}
```

---

### 3.2 `view` — Inspect Active Session

#### Request Payload
```json
{
  "mod": "m_AAA",
  "subMod": "sm_auth",
  "action": "session",
  "actionType": "view",
  "payload": {}
}
```

*Requires `Authorization: Bearer <jwt>` HTTP header.*

---

### 3.3 `update` — Refresh Token / Change Password

#### Request Payload
```json
{
  "mod": "m_AAA",
  "subMod": "sm_auth",
  "action": "session",
  "actionType": "update",
  "payload": {
    "refreshToken": "REFRESH-TOKEN-ABC123XYZ"
  }
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `refreshToken` | string | No* | Valid refresh token (or supply `oldPassword` & `newPassword`). |
| `oldPassword` | string | No* | Existing password for password update. |
| `newPassword` | string | No* | New password for password update. |

---

### 3.4 `delete` — Logout / Terminate Session

#### Request Payload
```json
{
  "mod": "m_AAA",
  "subMod": "sm_auth",
  "action": "session",
  "actionType": "delete",
  "payload": {}
}
```

---

## 4. Submodule: Multi-Factor Authentication (`sm_auth` / `mfa`)

### 4.1 `update` — Verify MFA Code

```json
{
  "mod": "m_AAA",
  "subMod": "sm_auth",
  "action": "mfa",
  "actionType": "update",
  "payload": {
    "mfaCode": "654321"
  }
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `mfaCode` | string | Yes | 6-digit TOTP / SMS verification code. |

---

## 5. Submodule: Role-Based Access Control (`sm_rbac`)

Use `subMod: "sm_rbac"` and `action: "rbac"`.

### 5.1 `add` — Create Role

```json
{
  "mod": "m_AAA",
  "subMod": "sm_rbac",
  "action": "rbac",
  "actionType": "add",
  "payload": {
    "roleName": "FINANCE_MANAGER",
    "description": "Manages student fee assignments and collection",
    "permissions": ["fees.read", "fees.write", "reports.generate"]
  }
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `roleName` | string | Yes | Unique role code identifier. |
| `description` | string | No | Role description. |
| `permissions` | array[string] | No | Granted permission strings. |

---

## 6. Submodule: Security Policy (`sm_policy`)

Use `subMod: "sm_policy"` and `action: "policy"`.

### 6.1 `view` — Get Security Policies

```json
{
  "mod": "m_AAA",
  "subMod": "sm_policy",
  "action": "policy",
  "actionType": "view",
  "payload": {}
}
```
