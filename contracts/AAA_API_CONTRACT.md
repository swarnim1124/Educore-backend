# API Contract: m_AAA

This document outlines the standard OneApp Request/Response API surface for the `m_AAA` module.
It details the exact JSON payloads required for all actions and actionTypes based on the module's implementation.

---

## Submodule: `sm_auth`

### Action: `session`

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_auth",
    "action": "session",
    "actionType": "add",
    "payload": {
        "username": "<string> (Required: if no challengeToken)",
        "email": "<string> (Optional: alias for username)",
        "password": "<string> (Required: if no challengeToken)",
        "captchaToken": "<string> (Optional: required if policy enabled)",
        "challengeToken": "<string> (Optional: for MFA verification flow)",
        "response": "<string> (Optional: for MFA verification flow)"
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_auth",
    "action": "session",
    "actionType": "view",
    "payload": {}
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_auth",
    "action": "session",
    "actionType": "update",
    "payload": {
        "refreshToken": "<string> (Required)"
    }
}
```

#### actionType: `delete`
**Expected Payload**:
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

### Action: `password`

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_auth",
    "action": "password",
    "actionType": "add",
    "payload": {
        "password": "<string> (Required)"
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_auth",
    "action": "password",
    "actionType": "view",
    "payload": {
        "password": "<string> (Required)"
    }
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_auth",
    "action": "password",
    "actionType": "update",
    "payload": {
        "oldPassword": "<string> (Required)",
        "newPassword": "<string> (Required)"
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_auth",
    "action": "password",
    "actionType": "delete",
    "payload": {}
}
```

---

### Action: `passwordReset`

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_auth",
    "action": "passwordReset",
    "actionType": "add",
    "payload": {
        "email": "<string> (Required)"
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_auth",
    "action": "passwordReset",
    "actionType": "view",
    "payload": {
        "token": "<string> (Required)"
    }
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_auth",
    "action": "passwordReset",
    "actionType": "update",
    "payload": {
        "token": "<string> (Required)",
        "password": "<string> (Required)"
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_auth",
    "action": "passwordReset",
    "actionType": "delete",
    "payload": {
        "token": "<string> (Required)"
    }
}
```

---

## Submodule: `sm_mfa`

### Action: `mfa`

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_mfa",
    "action": "mfa",
    "actionType": "add",
    "payload": {
        "enrollmentChallengeId": "<string> (Optional: required for verification step)",
        "response": "<string> (Optional: required for verification step)"
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_mfa",
    "action": "mfa",
    "actionType": "view",
    "payload": {}
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_mfa",
    "action": "mfa",
    "actionType": "update",
    "payload": {
        "method_id": "<string> (Required)",
        "action": "<string> (Required: 'set_primary' or 'regenerate_backup_codes')"
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_mfa",
    "action": "mfa",
    "actionType": "delete",
    "payload": {
        "method_id": "<string> (Required)"
    }
}
```

---

## Submodule: `sm_rbac`

### Action: `role`

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_rbac",
    "action": "role",
    "actionType": "add",
    "payload": {
        "roleCode": "<string> (Required)",
        "roleName": "<string> (Required)",
        "description": "<string> (Optional)",
        "statusId": "<integer> (Optional: default 1)"
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_rbac",
    "action": "role",
    "actionType": "view",
    "payload": {}
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_rbac",
    "action": "role",
    "actionType": "update",
    "payload": {
        "id": "<string> (Required)",
        "roleName": "<string> (Optional)",
        "description": "<string> (Optional)",
        "statusId": "<integer> (Optional)"
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_rbac",
    "action": "role",
    "actionType": "delete",
    "payload": {
        "id": "<string> (Required)"
    }
}
```

---

### Action: `roleAssignment`

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_rbac",
    "action": "roleAssignment",
    "actionType": "add",
    "payload": {
        "userOrgId": "<string> (Required)",
        "orgRoleIds": "<array of strings> (Required)",
        "orgRoleId": "<string> (Optional: legacy single assignment)"
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_rbac",
    "action": "roleAssignment",
    "actionType": "view",
    "payload": {
        "userOrgId": "<string> (Optional)"
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_rbac",
    "action": "roleAssignment",
    "actionType": "delete",
    "payload": {
        "assignmentId": "<string> (Required)"
    }
}
```

*(Note: `update` actionType is unsupported by architectural design for role assignments. Use `delete` and `add` instead.)*

---

### Action: `permission`

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_rbac",
    "action": "permission",
    "actionType": "add",
    "payload": {
        "orgRoleId": "<string> (Required)",
        "permissionId": "<string> (Required)"
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_rbac",
    "action": "permission",
    "actionType": "view",
    "payload": {
        "orgRoleId": "<string> (Optional)"
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_rbac",
    "action": "permission",
    "actionType": "delete",
    "payload": {
        "rolePermissionId": "<string> (Required)"
    }
}
```

---

### Action: `accessibleModules`

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_rbac",
    "action": "accessibleModules",
    "actionType": "view",
    "payload": {
        "userOrgId": "<string> (Optional: defaults to authenticated user)"
    }
}
```

---

## Submodule: `sm_policy`

*(The following payload structure applies identically to actions: `passwordPolicy`, `sessionPolicy`, and `loginPolicy`)*

### Actions: `passwordPolicy`, `sessionPolicy`, `loginPolicy`

#### actionType: `add`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_policy",
    "action": "<passwordPolicy | sessionPolicy | loginPolicy>",
    "actionType": "add",
    "payload": {
        "id": "<string> (Optional)",
        "...": "<Additional policy-specific fields...>"
    }
}
```

#### actionType: `view`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_policy",
    "action": "<passwordPolicy | sessionPolicy | loginPolicy>",
    "actionType": "view",
    "payload": {
        "institution_id": "<string> (Optional: defaults to user's institution)"
    }
}
```

#### actionType: `update`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_policy",
    "action": "<passwordPolicy | sessionPolicy | loginPolicy>",
    "actionType": "update",
    "payload": {
        "id": "<string> (Required)",
        "...": "<Additional policy-specific fields...>"
    }
}
```

#### actionType: `delete`
**Expected Payload**:
```json
{
    "mod": "m_AAA",
    "subMod": "sm_policy",
    "action": "<passwordPolicy | sessionPolicy | loginPolicy>",
    "actionType": "delete",
    "payload": {
        "institution_id": "<string> (Optional)"
    }
}
```
