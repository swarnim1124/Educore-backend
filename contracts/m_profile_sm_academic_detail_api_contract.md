# m_profile — Academic Detail Submodule API Contract (`sm_academic_detail`)

**Version:** 1.0.0  
**Last Updated:** 2026-08-04  
**Module:** `m_profile`  
**Submodule:** `sm_academic_detail`  
**Action:** `academicDetail`  
**Endpoint:** `POST /`

This document specifies the complete API contract for the `sm_academic_detail` submodule in `m_profile`.

---

## 1. Transport & Gateway Envelope

All requests use the standard OneApp Gateway envelope.

```json
{
  "app": "OneApp",
  "mod": "m_profile",
  "subMod": "sm_academic_detail",
  "action": "academicDetail",
  "actionType": "<add|view|update|delete>",
  "payload": {}
}
```

### Request Headers
```http
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

---

## 2. Operations Overview

| Action | ActionType | Purpose | Payload Requirements |
|---|---|---|---|
| `academicDetail` | `add` | Create user academic identifiers (ID Card, Biometric) | `userId` (required), optional `idCardNumber`, `biometricId` |
| `academicDetail` | `view` | View user academic identifiers and student/employee numbers | `userId` OR `enrollmentNumber` OR `employeeCode` |
| `academicDetail` | `update` | Re-issue ID Card or Biometric identifiers | `userId` (required), optional `idCardNumber`, `biometricId` |
| `academicDetail` | `delete` | Deactivate an active academic identifier | `userId` (required), `identifierType` (required), optional `reason` |

---

## 3. Action Type Specifications

### 3.1 `add` — Add Academic Identifiers

Creates academic identifier records for an existing user profile.

#### Request Example
```json
{
  "mod": "m_profile",
  "subMod": "sm_academic_detail",
  "action": "academicDetail",
  "actionType": "add",
  "payload": {
    "userId": 42,
    "idCardNumber": "CARD-2026-0042",
    "biometricId": "BIO-2026-0042"
  }
}
```

#### Success Response
```json
{
  "status": "success",
  "message": "Academic identifiers created successfully",
  "data": {
    "userId": 42,
    "identifiers": [
      {
        "type": "idCardNumber",
        "id": 101
      },
      {
        "type": "biometricId",
        "id": 102
      }
    ]
  }
}
```

#### Error Responses
- **Missing userId**: `{"status": "error", "message": "userId is required"}`
- **Profile not found**: `{"status": "error", "message": "personalDetail must exist before creating academicDetail"}`

---

### 3.2 `view` — View Academic Details & Identifiers

Retrieves academic identifiers and enrollment/employee numbers. Exactly one lookup selector must be provided: `userId`, `enrollmentNumber`, or `employeeCode`.

#### Request Example (by userId)
```json
{
  "mod": "m_profile",
  "subMod": "sm_academic_detail",
  "action": "academicDetail",
  "actionType": "view",
  "payload": {
    "userId": 42
  }
}
```

#### Success Response (by userId)
```json
{
  "status": "success",
  "message": "Academic detail retrieved",
  "data": {
    "identifiers": [
      {
        "id": 101,
        "user_id": 42,
        "identifier_type_id": 1,
        "identifier_type_name": "ID Card",
        "identifier_value": "CARD-2026-0042",
        "status_id": 1,
        "status_name": "Active"
      }
    ],
    "enrollmentNumber": "STU-2026-0042",
    "branch": "Computer Science and Engineering",
    "batch": "2022-2026",
    "semester": 5,
    "section": "Section A",
    "cgpa": 8.32,
    "employeeCode": null
  }
}
```

#### Request Example (by enrollmentNumber)
```json
{
  "mod": "m_profile",
  "subMod": "sm_academic_detail",
  "action": "academicDetail",
  "actionType": "view",
  "payload": {
    "enrollmentNumber": "STU-2026-0042"
  }
}
```

#### Request Example (by employeeCode)
```json
{
  "mod": "m_profile",
  "subMod": "sm_academic_detail",
  "action": "academicDetail",
  "actionType": "view",
  "payload": {
    "employeeCode": "EMP-2026-0002"
  }
}
```

#### Error Response
- **No search parameter provided**: `{"status": "error", "message": "Provide userId, enrollmentNumber, or employeeCode"}`

---

### 3.3 `update` — Update / Re-issue Identifiers

Re-issues `idCardNumber` or `biometricId` by deactivating existing active identifiers of that type and creating a new record.

> [!NOTE]
> `enrollmentNumber` and `employeeCode` are immutable system numbers and cannot be updated.

#### Request Example
```json
{
  "mod": "m_profile",
  "subMod": "sm_academic_detail",
  "action": "academicDetail",
  "actionType": "update",
  "payload": {
    "userId": 42,
    "idCardNumber": "CARD-2026-0099"
  }
}
```

#### Success Response
```json
{
  "status": "success",
  "message": "Academic identifiers updated",
  "data": {
    "reIssued": [
      "idCardNumber"
    ]
  }
}
```

#### Error Responses
- **Attempting to update immutable fields**: `{"status": "error", "message": "enrollmentNumber and employeeCode are immutable and cannot be updated"}`
- **No fields provided**: `{"status": "error", "message": "No updatable fields provided (idCardNumber, biometricId)"}`

---

### 3.4 `delete` — Deactivate Identifier

Deactivates an active identifier by type for a user.

#### Request Example
```json
{
  "mod": "m_profile",
  "subMod": "sm_academic_detail",
  "action": "academicDetail",
  "actionType": "delete",
  "payload": {
    "userId": 42,
    "identifierType": "biometricId",
    "reason": "Card lost / biometric re-scanned"
  }
}
```

#### Success Response
```json
{
  "status": "success",
  "message": "Identifier deactivated",
  "data": {
    "identifierType": "biometricId",
    "reason": "Card lost / biometric re-scanned"
  }
}
```

#### Error Responses
- **Missing parameters**: `{"status": "error", "message": "userId and identifierType are required"}`
- **Invalid identifierType**: `{"status": "error", "message": "Invalid identifierType. Allowed: idCardNumber, biometricId. enrollmentNumber/employeeCode cannot be deleted."}`

---

## 4. Permissions & Authorization

| Action | Permission |
|---|---|
| `add` | `profile.academicDetail.add` |
| `view` | `profile.academicDetail.view.sel`, `profile.academicDetail.view.all` |
| `update` | `profile.academicDetail.update` |
| `delete` | `profile.academicDetail.delete` |
