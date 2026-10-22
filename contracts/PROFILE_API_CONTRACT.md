# m_profile API Contract

**Version:** 1.1  
**Last verified:** 2026-07-28  
**Module:** `m_profile`  
**Base URL:** `https://dev.globaloneapp.com` (local default: `http://127.0.0.1:8000`)

This document describes the Profile module exactly as implemented in the backend. It covers personal details, academic identifiers, family/guardian records, emergency contacts, medical details, and user preferences.

## 1. Transport and common request format

All operations use one endpoint.

| Method | Path | Content type |
|---|---|---|
| `POST` | `/` | `application/json` |

Send all five properties in every request:

```json
{
  "mod": "m_profile",
  "subMod": "sm_personal_detail",
  "action": "personalDetail",
  "actionType": "view",
  "payload": {}
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `mod` | string | Yes | Must be `m_profile`. |
| `subMod` | string | Yes | `sm_personal_detail`, `sm_academic_detail`, `sm_family_detail`, `sm_medical_detail`, or `sm_settings`. |
| `action` | string | Yes | See the operation table below. Case-sensitive. |
| `actionType` | string | Yes | One of `add`, `view`, `update`, or `delete`. |
| `payload` | object | Yes | Operation-specific input. Use `{}` when no input is needed. |

### Headers

```http
Content-Type: application/json
Authorization: Bearer <jwt>
```

The framework reads a valid Bearer JWT and makes its `user_id`, roles, and permissions available to the module. Supplying the header is strongly recommended for every Profile call. Medical-detail actions enforce role/self access and reject unauthenticated requests.

Each response also includes these diagnostic headers:

| Header | Description |
|---|---|
| `X-Request-ID` | Unique server-side request identifier; include it in support tickets. |
| `X-Process-Time-Ms` | Server processing time in milliseconds. |

Incoming request objects are logged in `oneapp_requests.log` with sensitive input parameters automatically masked.

## 2. Response and error handling

Responses are a **single** envelope (there is no outer/inner `data.status` wrapper).

### Successful operation

```json
{
  "status": "success",
  "message": "Personal detail retrieved",
  "data": {}
}
```

`data` is omitted for some successful writes.

### Business error

```json
{
  "status": "error",
  "message": "userId is required",
  "error_code": ""
}
```

`error_code` is usually an empty string. The sensitive-personal-detail grace-window error returns `GRACE_WINDOW_EXPIRED`.

### HTTP outcomes

| Scenario | HTTP status | Response |
|---|---:|---|
| Handled success or business validation error | `200` | Profile response envelope |
| Missing required envelope fields, invalid JSON/type | `422` | `{ "status": "error", "message": "Invalid Request Payload", "error_code": "ERR422" }` |
| Unknown module/action or unhandled exception | Usually `500` | `{ "status": "error", "message": "…", "stack_trace": "…" }` |
| Unsupported HTTP method | `405` | FastAPI default response |

Frontend code must check `body.status`, not only the HTTP status.

## 3. Operation index

| Submodule | Action | Supported action types |
|---|---|---|
| `sm_personal_detail` | `personalDetail` | add, view, update, delete |
| `sm_academic_detail` | `academicDetail` | add, view, update, delete |
| `sm_family_detail` | `familyDetail` | add, view, update, delete |
| `sm_family_detail` | `emergencyContact` | add, view, update, delete |
| `sm_medical_detail` | `medicalDetail` | add, view, update, delete |
| `sm_settings` | `userPreference` | add, view, update, delete |

## 4. Personal detail

Use `subMod: "sm_personal_detail"` and `action: "personalDetail"`.

### `add` — Create personal detail

`userId`, `firstName`, `lastName`, `dob`, `genderId`, and `mobile` are required. The user must already exist, must not already have a profile, and `mobile` must be unique.

```json
{
  "mod": "m_profile", "subMod": "sm_personal_detail", "action": "personalDetail", "actionType": "add",
  "payload": {
    "userId": 42,
    "firstName": "Asha",
    "middleName": "K.",
    "lastName": "Sharma",
    "dob": "2000-08-15",
    "genderId": 1,
    "mobile": "9876543210",
    "photoDocId": 501,
    "nationalityId": 91,
    "bloodGroupId": 3
  }
}
```

| Payload field | Type | Required | Notes |
|---|---|---:|---|
| `userId` | number/string | Yes | Existing `sch_iam.tb_user` ID. |
| `firstName`, `middleName`, `lastName` | string | First/last yes | `middleName` is optional. |
| `dob` | string | Yes | Date value accepted by PostgreSQL; use `YYYY-MM-DD`. |
| `genderId`, `nationalityId`, `photoDocId`, `bloodGroupId` | number | No* | `genderId` is required; remaining IDs are optional lookup/document IDs. |
| `mobile` | string | Yes | Must be unique across users. |

Success:

```json
{ "status": "success", "message": "Personal detail created successfully", "data": { "userId": 42 } }
```

Common errors: `userId is required`; `User does not exist in m_aaa`; `Personal detail record already exists for this user`; `Missing mandatory fields: firstName, lastName, dob, genderId, mobile`; `Mobile number is already in use`.

### `view` — Retrieve personal detail

Pass `userId` to retrieve a profile. If omitted, the backend uses the JWT user ID when available; with neither, it returns an unimplemented directory result.

```json
{ "mod": "m_profile", "subMod": "sm_personal_detail", "action": "personalDetail", "actionType": "view", "payload": { "userId": 42 } }
```

Success (`data.addresses` is an array and may be empty):

```json
{
  "status": "success", "message": "Personal detail retrieved",
  "data": {
    "userId": 42, "email": "asha@example.com", "alternateEmail": "asha@example.com",
    "mobile": "9876543210", "firstName": "Asha", "middleName": "K.", "lastName": "Sharma",
    "dob": "2000-08-15", "genderId": 1, "photoDocId": 501, "nationalityId": 91,
    "primaryLangId": null, "bloodGroupId": 3,
    "createdAt": "2026-07-24 10:00:00", "updatedAt": "2026-07-24 10:00:00",
    "addresses": []
  }
}
```

If no `userId` and no authenticated user are available: `{ "status": "success", "message": "Directory view not yet implemented", "data": [] }`. If the user has no core user record: `Profile not found`.

### `update` — Update personal detail

`fieldsToUpdate` contains any of the fields below. `mobile` is processed separately and must remain unique.

```json
{
  "mod": "m_profile", "subMod": "sm_personal_detail", "action": "personalDetail", "actionType": "update",
  "payload": { "userId": 42, "fieldsToUpdate": { "firstName": "Aashi", "mobile": "9988776655", "primaryLangId": 1 } }
}
```

Allowed logical fields: `firstName`, `middleName`, `lastName`, `dob`, `genderId`, `photoDocId`, `nationalityId`, `primaryLangId`, and `mobile`. The implementation also accepts `gender_id` and `nationality_id` as aliases. Unknown fields are passed through as database column names and should not be sent by clients.

Changes to `dob`, `gender_id`, and `nationality_id` are allowed only during the first 14 days after profile creation. Note that the camel-case keys `genderId` and `nationalityId` are currently not included in this grace-window check; this is an implementation inconsistency, not a client-side bypass to rely on.

Success: `{ "status": "success", "message": "Personal detail updated successfully" }`.

### `delete` — Anonymise personal detail

This does not delete the row. It replaces the first/last name with `REDACTED`, clears selected fields, and returns the supplied reason.

```json
{ "mod": "m_profile", "subMod": "sm_personal_detail", "action": "personalDetail", "actionType": "delete", "payload": { "userId": 42, "reason": "Account closure" } }
```

```json
{ "status": "success", "message": "Personal detail anonymised successfully", "data": { "reason": "Account closure" } }
```

## 5. Academic detail / identifiers

Use `subMod: "sm_academic_detail"` and `action: "academicDetail"`. A personal-detail record must exist before `add`.

### `add` — Create identifiers

At least one of `idCardNumber` or `biometricId` should be supplied. If neither is sent, the current implementation still returns success with an empty identifier list.

```json
{ "mod": "m_profile", "subMod": "sm_academic_detail", "action": "academicDetail", "actionType": "add", "payload": { "userId": 42, "idCardNumber": "ID-2026-0042", "biometricId": "BIO-9981" } }
```

```json
{ "status": "success", "message": "Academic identifiers created successfully", "data": { "userId": 42, "identifiers": [{ "type": "idCardNumber", "id": 101 }, { "type": "biometricId", "id": 102 }] } }
```

### `view` — Look up academic detail

Provide exactly one lookup selector: `userId`, `enrollmentNumber`, or `employeeCode`.

```json
{ "mod": "m_profile", "subMod": "sm_academic_detail", "action": "academicDetail", "actionType": "view", "payload": { "userId": 42 } }
```

By `userId`, `data` has this shape:

```json
{ "status": "success", "message": "Academic detail retrieved", "data": { "identifiers": [{ "id": 101, "user_id": 42, "identifier_type_id": 1, "identifier_type_name": "ID Card", "identifier_value": "ID-2026-0042", "status_id": 1, "status_name": "Active" }], "enrollmentNumber": "STU-2026-42", "branch": "Computer Science and Engineering", "batch": "2022-2026", "semester": 5, "section": "Section A", "cgpa": 8.32, "employeeCode": null } }
```

By `enrollmentNumber` or `employeeCode`, `data` is an array of matching database rows. Missing all selectors returns `Provide userId, enrollmentNumber, or employeeCode`.

### `update` — Reissue card/biometric identifiers

`enrollmentNumber` and `employeeCode` are immutable. A supplied `idCardNumber` and/or `biometricId` deactivates the existing identifier of that type and creates a new one.

```json
{ "mod": "m_profile", "subMod": "sm_academic_detail", "action": "academicDetail", "actionType": "update", "payload": { "userId": 42, "idCardNumber": "ID-2026-0099" } }
```

```json
{ "status": "success", "message": "Academic identifiers updated", "data": { "reIssued": ["idCardNumber"] } }
```

### `delete` — Deactivate an identifier

```json
{ "mod": "m_profile", "subMod": "sm_academic_detail", "action": "academicDetail", "actionType": "delete", "payload": { "userId": 42, "identifierType": "biometricId", "reason": "Device replaced" } }
```

`identifierType` must be `idCardNumber` or `biometricId`. Enrollment and employee numbers cannot be deleted.

```json
{ "status": "success", "message": "Identifier deactivated", "data": { "identifierType": "biometricId", "reason": "Device replaced" } }
```

## 6. Family / guardian detail

Use `subMod: "sm_family_detail"` and `action: "familyDetail"`. This action is scoped to students. `studentId` is the student-record ID, not necessarily the user ID.

### `add`

```json
{
  "mod": "m_profile", "subMod": "sm_family_detail", "action": "familyDetail", "actionType": "add",
  "payload": { "studentId": 17, "relation": 2, "name": "Ravi Sharma", "mobile": "9876500000", "email": "ravi@example.com", "occupation": "Teacher", "annualIncome": 650000, "isEmergencyContact": true }
}
```

Required: `studentId`, `relation` (relationship lookup ID), `name`, `mobile`. Optional: `email`, `occupation`, `annualIncome` (number >= 0), `isEmergencyContact` (default `false`). A `true` emergency-contact flag clears that flag from the student's other family records.

Success: `{ "status": "success", "message": "Family detail created successfully" }`.

### `view`

```json
{ "mod": "m_profile", "subMod": "sm_family_detail", "action": "familyDetail", "actionType": "view", "payload": { "studentId": 17 } }
```

```json
{ "status": "success", "message": "Family details retrieved", "data": [{ "id": 8, "first_name": "Ravi", "middle_name": null, "last_name": "Sharma", "gender_id": null, "dob": null, "mobile_no": "9876500000", "email": "ravi@example.com", "occupation": "Teacher", "annual_income": 650000, "photo_doc_id": null, "status_id": 1, "relationship_type_id": 2, "is_primary_guardian": false, "is_emergency_contact": true }] }
```

### `update`

```json
{ "mod": "m_profile", "subMod": "sm_family_detail", "action": "familyDetail", "actionType": "update", "payload": { "familyDetailId": 8, "fieldsToUpdate": { "name": "Ravi K Sharma", "occupation": "Principal", "annualIncome": 700000 } } }
```

Allowed keys in `fieldsToUpdate`: `name`, `mobile`, `email`, `occupation`, `annualIncome`. Unknown keys are ignored; an all-unknown field object still currently returns success with no change. Success: `{ "status": "success", "message": "Family detail updated successfully" }`.

### `delete`

```json
{ "mod": "m_profile", "subMod": "sm_family_detail", "action": "familyDetail", "actionType": "delete", "payload": { "familyDetailId": 8, "reason": "Record requested removal" } }
```

```json
{ "status": "success", "message": "Family detail removed", "data": { "reason": "Record requested removal" } }
```

## 7. Emergency contacts

Use `subMod: "sm_family_detail"` and `action: "emergencyContact"`. This is distinct from a family record and can apply to any user type.

### `add`

```json
{ "mod": "m_profile", "subMod": "sm_family_detail", "action": "emergencyContact", "actionType": "add", "payload": { "userId": 42, "name": "Ravi Sharma", "relation": 2, "mobile": "9876500000", "priorityOrder": 1 } }
```

Required: `userId`, `name`, `relation`, `mobile`, `priorityOrder`. `relation` is validated as present but is not persisted by the current implementation. `priorityOrder: 1` maps to `is_primary: true`; all other numeric values map to `false`.

Success: `{ "status": "success", "message": "Emergency contact created successfully" }`.

### `view`

```json
{ "mod": "m_profile", "subMod": "sm_family_detail", "action": "emergencyContact", "actionType": "view", "payload": { "userId": 42 } }
```

```json
{ "status": "success", "message": "Emergency contacts retrieved", "data": [{ "id": 12, "user_id": 42, "f_name": "Ravi", "m_name": null, "l_name": "Sharma", "mobile": "9876500000", "email": null, "is_primary": true, "status_id": 1 }] }
```

### `update`

```json
{ "mod": "m_profile", "subMod": "sm_family_detail", "action": "emergencyContact", "actionType": "update", "payload": { "contactId": 12, "fieldsToUpdate": { "name": "Ravi K Sharma", "mobile": "9999999999", "priorityOrder": 2 } } }
```

Allowed fields: `name`, `mobile`, `priorityOrder`. Success: `{ "status": "success", "message": "Emergency contact updated successfully" }`.

### `delete`

```json
{ "mod": "m_profile", "subMod": "sm_family_detail", "action": "emergencyContact", "actionType": "delete", "payload": { "contactId": 12 } }
```

Success: `{ "status": "success", "message": "Emergency contact removed" }`.

## 8. Medical detail

Use `subMod: "sm_medical_detail"` and `action: "medicalDetail"`. A personal-detail record must exist before `add`.

**Access rule:** `view`, `update`, and `delete` are allowed only for the same authenticated user or a JWT containing `MEDICAL_OFFICER`, `EMERGENCY_STAFF`, or `ADMIN` in `roles`. `add` currently does not run this access check. Denied calls return `Access denied: Only self, Medical Officer, or Emergency Staff may access medical records`.

### `add`

```json
{
  "mod": "m_profile", "subMod": "sm_medical_detail", "action": "medicalDetail", "actionType": "add",
  "payload": {
    "userId": 42, "bloodGroupId": 3,
    "allergies": ["Penicillin"], "chronicConditions": ["Asthma"], "medications": ["Inhaler"],
    "doctorName": "Dr Rao", "doctorContact": "9876543211", "insurancePolicyNo": "POL-100"
  }
}
```

All fields except `userId` are optional. Lists are returned as arrays, but stored internally as JSON text. The backend rejects creation when a medical row already exists.

Success: `{ "status": "success", "message": "Medical detail created successfully" }`.

### `view`

```json
{ "mod": "m_profile", "subMod": "sm_medical_detail", "action": "medicalDetail", "actionType": "view", "payload": { "userId": 42 } }
```

```json
{
  "status": "success", "message": "Medical detail retrieved",
  "data": { "userId": 42, "bloodGroupId": 3, "allergies": ["Penicillin"], "chronicConditions": ["Asthma"], "medications": ["Inhaler"], "height": null, "weight": null, "disabilityTypeId": null, "doctorName": "Dr Rao", "doctorContact": "9876543211", "insurancePolicyNo": "POL-100" }
}
```

When no row exists: `{ "status": "success", "message": "No medical detail found" }` (the `data` property is omitted because it is `null`).

### `update`

```json
{ "mod": "m_profile", "subMod": "sm_medical_detail", "action": "medicalDetail", "actionType": "update", "payload": { "userId": 42, "fieldsToUpdate": { "allergies": ["Penicillin", "Peanuts"], "medications": ["Inhaler", "Antihistamine"] } } }
```

Accepted fields: `bloodGroupId`, `allergies`, `chronicConditions`, `medications`, `doctorName`, `doctorContact`, `insurancePolicyNo`. `height`, `weight`, `disabilityTypeId`, and `emergencyNote` are returned by `view` but cannot currently be updated through this action. Success: `{ "status": "success", "message": "Medical detail updated successfully" }`.

### `delete`

```json
{ "mod": "m_profile", "subMod": "sm_medical_detail", "action": "medicalDetail", "actionType": "delete", "payload": { "userId": 42, "reason": "Requested by user" } }
```

```json
{ "status": "success", "message": "Medical detail removed", "data": { "reason": "Requested by user" } }
```

## 9. User preferences

Use `subMod: "sm_settings"` and `action: "userPreference"`.

Supported preference keys and defaults:

| Key | Value type | Default |
|---|---|---|
| `language` | string | `en` |
| `theme` | string | `light` |
| `timezone` | string | `UTC` |
| `defaultLandingModule` | string | `m_student` |

Values are stored and returned as strings. The backend currently does not validate language tags, time zones, themes, or module names.

### `add` — Create preferences

The profile must exist and no preference rows may already exist. Omitted keys receive the defaults above.

```json
{ "mod": "m_profile", "subMod": "sm_settings", "action": "userPreference", "actionType": "add", "payload": { "userId": 42, "theme": "dark", "timezone": "Asia/Kolkata" } }
```

```json
{ "status": "success", "message": "User preferences created with defaults", "data": { "language": "en", "theme": "dark", "timezone": "Asia/Kolkata", "defaultLandingModule": "m_student" } }
```

### `view` — Read preferences

```json
{ "mod": "m_profile", "subMod": "sm_settings", "action": "userPreference", "actionType": "view", "payload": { "userId": 42 } }
```

The response always merges stored values onto defaults, so it returns all four keys even if no rows exist.

```json
{ "status": "success", "message": "User preferences retrieved", "data": { "language": "en", "theme": "dark", "timezone": "Asia/Kolkata", "defaultLandingModule": "m_student" } }
```

### `update` — Upsert selected preferences

```json
{ "mod": "m_profile", "subMod": "sm_settings", "action": "userPreference", "actionType": "update", "payload": { "userId": 42, "fieldsToUpdate": { "theme": "light", "defaultLandingModule": "m_exam" } } }
```

Unknown keys are skipped. If none of the supplied keys are valid, the operation fails with `No valid preference keys provided`.

```json
{ "status": "success", "message": "User preferences updated", "data": { "updated": ["theme", "defaultLandingModule"] } }
```

### `delete` — Reset preferences

This does not leave preferences deleted: it deletes all current rows and immediately recreates all four platform defaults.

```json
{ "mod": "m_profile", "subMod": "sm_settings", "action": "userPreference", "actionType": "delete", "payload": { "userId": 42 } }
```

```json
{ "status": "success", "message": "User preferences reset to platform defaults", "data": { "language": "en", "theme": "light", "timezone": "UTC", "defaultLandingModule": "m_student" } }
```

## 10. Frontend integration notes

1. Send a JSON object with every envelope property. `actionType` is required and cannot be `null`.
2. Treat `status: "error"` in a `200` response as a failed operation and display/use `message`.
3. Use numeric lookup IDs where a field is named `*Id` or documented as a relationship/lookup ID.
4. Persist the `id` returned by read operations for `familyDetailId` and `contactId` update/delete calls. Creation responses do not currently include those IDs, so re-query after creating if they are needed.
5. Do not rely on server-side authorization for non-medical Profile actions until RBAC enforcement is added. Limit UI actions and protect the API at the gateway if required.
6. Use the documented logical/camel-case fields only. Several handlers silently ignore unknown fields, which can otherwise look like a successful update.

## 11. Implementation limitations to account for

| Area | Current behavior |
|---|---|
| Profile directory | `personalDetail:view` without a target user returns an empty “not yet implemented” result. |
| Authorization | JWT parsing is global, but only medical read/update/delete checks access roles/self. |
| Personal sensitive fields | Grace-window enforcement recognizes snake-case `gender_id`/`nationality_id`, not their normal camel-case API aliases. |
| Family/emergency relationship | `familyDetail.relation` is stored; `emergencyContact.relation` is required but is not stored/returned. |
| Emergency priority | Only priority `1` is persisted; all other priorities are represented as `is_primary: false`. |
| Medical fields | `height`, `weight`, and `disabilityTypeId` are read-only in the current API; the medical create route does not enforce medical-role/self access. |
| Delete semantics | Personal records are anonymised; academic identifiers are deactivated; preferences are reset to defaults. Only family, emergency-contact, and medical rows are physically deleted. |

## 12. Change log

| Date | Version | Notes |
|---|---|---|
| 2026-07-24 | 1.0 | Initial Profile API contract based on the implemented `m_profile` module and framework router. |
