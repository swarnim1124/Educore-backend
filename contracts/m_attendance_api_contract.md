# m_attendance API Contract

This document outlines the standard OneApp Request/Response API surface for the `m_attendance` module.
It explicitly lists out all action types and their expected payloads so frontend applications can integrate cleanly.

---

## Submodule: `sm_configuration`

All operations use standard gateway envelope (`POST /`):

#### actionType: `<add|view|update|delete|activate|deactivate|get_active>`
**Description**: Supports institutional attendance policy lifecycle including semantic deletion/reseting to defaults.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceConfiguration",
    "actionType": "<add|view|update|delete|activate|deactivate|get_active>",
    "payload": {
        "instId": 1,
        "policyName": "Standard Attendance Policy 2026",
        "minAttPercent": 75.0,
        "allowLateMarking": true,
        "lateMarkingWindowMinutes": 15,
        "autoLockAfterHours": 24,
        "requireApproval": true,
        "requireMedProof": false,
        "isActive": true
    }
}
```

#### actionType: `activate`
**Description**: Executes the action.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceConfiguration",
    "actionType": "activate",
    "payload": {
        "policyId": 1001
    }
}
```

#### actionType: `add`
**Description**: Executes the action.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceConfiguration",
    "actionType": "add",
    "payload": {
        "instId": 1,
        "policyName": "Fall 2026 Policy",
        "minAttPercent": 75.0,
        "allowLateMarking": true,
        "isActive": true
    }
}
```

#### actionType: `deactivate`
**Description**: Executes the action.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceConfiguration",
    "actionType": "deactivate",
    "payload": {
        "policyId": 1001
    }
}
```

#### actionType: `delete`
**Description**: Executes a Semantic Delete / Reset on an institutional attendance policy record. Retains the physical row in tb_att_policy while resetting parameter columns to system defaults (e.g., 75% min attendance threshold) and updating audit timestamps. This is a semantic operation and not a SQL physical DELETE operation.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceConfiguration",
    "actionType": "delete",
    "payload": {
        "policyId": 1001
    }
}
```

#### actionType: `get_active`
**Description**: Executes the action.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceConfiguration",
    "actionType": "get_active",
    "payload": {
        "instId": 1
    }
}
```

#### actionType: `update`
**Description**: Takes immediate effect for future calculations; never retroactively recalculates history.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceConfiguration",
    "actionType": "update",
    "payload": {
        "policyId": 1001,
        "minAttPercent": 80.0
    }
}
```

#### actionType: `view`
**Description**: Executes the action.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceConfiguration",
    "actionType": "view",
    "payload": {
        "policyId": 1001
    }
}
```

---

## Submodule: `sm_configuration`

### Action: `attendanceType`

#### actionType: `<add|view|update|delete>`
**Description**: Enforces semantic deactivation rather than SQL deletion when records reference the type.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceType",
    "actionType": "<add|view|update|delete>",
    "payload": {
        "typeCode": "PRESENT",
        "typeName": "Present in Class",
        "countsAsPresent": true
    }
}
```

#### actionType: `add`
**Description**: Executes the action.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceType",
    "actionType": "add",
    "payload": {
        "typeCode": "PRESENT",
        "typeName": "Present in Class",
        "countsAsPresent": true
    }
}
```

#### actionType: `delete`
**Description**: Executes a Semantic Deactivation on an attendance marking type rather than a SQL physical DELETE operation. Verifies if attendance records reference this type ID; deactivates instead to preserve immutable audit trail.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceType",
    "actionType": "delete",
    "payload": {
        "typeId": 10
    }
}
```

#### actionType: `update`
**Description**: Executes the action.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceType",
    "actionType": "update",
    "payload": {
        "typeId": 10,
        "countsAsPresent": false
    }
}
```

#### actionType: `view`
**Description**: Executes the action.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_configuration",
    "action": "attendanceType",
    "actionType": "view",
    "payload": {}
}
```

---

## Submodule: `sm_exception`

### Action: `attendanceException`

#### actionType: `<add|view|update|delete>`
**Description**: Supports retroactive exception revocation inside explicit async transactions when withdrawing an approved exception.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_exception",
    "action": "attendanceException",
    "actionType": "<add|view|update|delete>",
    "payload": {
        "studId": 101,
        "startDate": "2026-08-01",
        "endDate": "2026-08-05",
        "reason": "National University Sports Tournament Representation",
        "docPath": "/uploads/med_proof_101.pdf"
    }
}
```

---

## Submodule: `sm_exception`

### Action: `exceptionApproval`

#### actionType: `<add|view|update|delete>`
**Description**: When approved, triggers atomic date-range exception overrides across all matching class sessions. When rejected or revoked, executes a semantic rejection to preserve audit compliance.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_exception",
    "action": "exceptionApproval",
    "actionType": "<add|view|update|delete>",
    "payload": {
        "exceptionId": 300,
        "decision": "APPROVE",
        "comments": "Verified official sports participation letter."
    }
}
```

---

## Submodule: `sm_records`

### Action: `attendanceRecord`

#### actionType: `<add|view|update|delete>`
**Description**: Enforces atomic bulk marking within explicit async transactions and session lock invariance.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_records",
    "action": "attendanceRecord",
    "actionType": "<add|view|update|delete>",
    "payload": {
        "attSessionId": 500,
        "records": [
            {"studId": 101, "attStatusCode": "PRESENT", "remarks": "On time"},
            {"studId": 102, "attStatusCode": "ABSENT", "remarks": "Unexcused"}
        ]
    }
}
```

---

## Submodule: `sm_records`

### Action: `attendanceSession`

#### actionType: `<add|view|update|delete>`
**Description**: Supports dynamic enrollment validation upon session creation and semantic session cancellation.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_records",
    "action": "attendanceSession",
    "actionType": "<add|view|update|delete>",
    "payload": {
        "classSessionId": 100,
        "markedByFacId": 5,
        "sessionDate": "2026-08-10",
        "sessionType": "REGULAR",
        "studentIds": [101, 102, 103]
    }
}
```

---

## Submodule: `sm_records`

### Action: `attendanceSubmission`

#### actionType: `<add|view|update|delete>`
**Description**: Enforces mandatory reason logging for reopen and revoke operations.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_records",
    "action": "attendanceSubmission",
    "actionType": "<add|view|update|delete>",
    "payload": {
        "attSessionId": 500,
        "reason": "Administrative correction required for student 102"
    }
}
```

---

## Submodule: `sm_shortage`

### Action: `attendanceShortage`

#### actionType: `<view|update|delete>`
**Description**: Categorizes students into risk levels without mutating policy configurations.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_shortage",
    "action": "attendanceShortage",
    "actionType": "<view|update|delete>",
    "payload": {
        "instId": 1,
        "studId": 101,
        "classSessionId": 200
    }
}
```

---

## Submodule: `sm_shortage`

### Action: `condonation`

#### actionType: `<add|view|update|delete>`
**Description**: Enforces audit compliance and semantic cancellation/rejection rather than physical SQL deletion.

**Expected Payload**:
```json
{
    "mod": "m_attendance",
    "subMod": "sm_shortage",
    "action": "condonation",
    "actionType": "<add|view|update|delete>",
    "payload": {
        "studId": 101,
        "attSessionId": 500,
        "reason": "Medical emergency during final exam review",
        "requestedPercent": 5.0
    }
}
```

---

