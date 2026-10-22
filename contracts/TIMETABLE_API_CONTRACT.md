# m_timetable API Contract

**Version:** 1.0  
**Last verified:** 2026-07-28  
**Module:** `m_timetable` — Timetable Management, Scheduling, Allocations, and Substitutions  
**Base URL:** `https://dev.globaloneapp.com` (local default: `http://127.0.0.1:8000`)

This document describes the API contract implemented by the `m_timetable` module. It defines the payload structures, actions, workflow rules, and response shapes for timetable configuration, schedule generation, room/faculty allocation, substitutions, and approval workflows.

---

## 1. Transport and Request Envelope

All operations use a single HTTP endpoint:

| Method | Path | Content-Type |
|---|---|---|
| `POST` | `/` | `application/json` |

Every request MUST include the top-level envelope properties:

```json
{
  "mod": "m_timetable",
  "subMod": "sm_configuration",
  "action": "workingDay",
  "actionType": "view",
  "payload": {}
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `mod` | string | Yes | Must be `m_timetable`. |
| `subMod` | string | Yes | Submodule identifier (e.g. `sm_configuration`, `sm_schedule`, `sm_allocation`, `sm_substitution`, `sm_approval`). |
| `action` | string | Yes | Canonical action string (e.g., `workingDay`, `timeSlot`, `timetable`, `facultyAllocation`, `roomAllocation`, `substitution`, `timetableApproval`). |
| `actionType` | string | Yes | Action type verb (`add`, `view`, `update`, or `delete`). |
| `payload` | object | Yes | Operation-specific data. Use `{}` when no parameters are needed. |

### Headers

```http
Content-Type: application/json
Authorization: Bearer <jwt>
```

---

## 2. Response and Error Handling

All responses return a single top-level JSON envelope:

### Successful Response

```json
{
  "status": "success",
  "message": "Working day pattern retrieved successfully",
  "data": { ... }
}
```

### Business Error Response

```json
{
  "status": "error",
  "message": "inst_id is required",
  "error_code": "400"
}
```

---

## 3. Submodule & Action Index

| Submodule (`subMod`) | Action (`action`) | Supported Action Types | Description |
|---|---|---|---|
| `sm_configuration` | `workingDay` | `add`, `view`, `update`, `delete` | Working day patterns & academic calendar day settings |
| `sm_configuration` | `timeSlot` | `add`, `view`, `update`, `delete` | Time slot grid configuration & period timings |
| `sm_configuration` | `academicCalendar` | `add`, `view`, `update`, `delete` | Academic calendar linkage and term schedule settings |
| `sm_schedule` | `timetable` | `add`, `view`, `update`, `delete` | Master timetable generation, viewing, revision & publishing |
| `sm_allocation` | `facultyAllocation` | `add`, `view`, `update`, `delete` | Faculty workload and subject teaching assignment |
| `sm_allocation` | `roomAllocation` | `add`, `view`, `update`, `delete` | Classroom and lab capacity assignment |
| `sm_substitution` | `substitution` | `add`, `view`, `update`, `delete` | Temporary faculty substitution management |
| `sm_approval` | `timetableApproval` | `add`, `view`, `update`, `delete` | Timetable workflow approval, rejection, & change requests |

---

## 4. Configuration Submodule — `sm_configuration`

### `workingDay` — Working Day Management

#### `add` — Batch create working day patterns
```json
{
  "mod": "m_timetable",
  "subMod": "sm_configuration",
  "action": "workingDay",
  "actionType": "add",
  "payload": {
    "inst_id": 1,
    "academicYearId": 2026,
    "records": [
      {
        "name": "Standard Weekday Pattern",
        "effectiveFrom": "2026-08-01",
        "effectiveTo": "2026-12-31",
        "days": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
      }
    ]
  }
}
```

#### `view` — Retrieve working day pattern
```json
{
  "mod": "m_timetable",
  "subMod": "sm_configuration",
  "action": "workingDay",
  "actionType": "view",
  "payload": { "inst_id": 1, "academicYearId": 2026 }
}
```

---

### `timeSlot` — Time Slot Grid Management

#### `add` — Create time slots
```json
{
  "mod": "m_timetable",
  "subMod": "sm_configuration",
  "action": "timeSlot",
  "actionType": "add",
  "payload": {
    "inst_id": 1,
    "slotName": "Period 1",
    "startTime": "09:00",
    "endTime": "10:00",
    "isBreak": false
  }
}
```

#### `view` — Retrieve time slots
```json
{
  "mod": "m_timetable",
  "subMod": "sm_configuration",
  "action": "timeSlot",
  "actionType": "view",
  "payload": { "inst_id": 1 }
}
```

---

## 5. Timetable Schedule Submodule — `sm_schedule`

### `timetable` — Schedule Generation & Management

#### `add` — Generate / Create Timetable
```json
{
  "mod": "m_timetable",
  "subMod": "sm_schedule",
  "action": "timetable",
  "actionType": "add",
  "payload": {
    "inst_id": 1,
    "academicTermId": 5,
    "departmentId": 2,
    "programId": 10,
    "semesterId": 3,
    "sectionId": 1,
    "name": "Fall 2026 CSE Semester 3 Section A"
  }
}
```

#### `view` — Retrieve Timetable Schedule
```json
{
  "mod": "m_timetable",
  "subMod": "sm_schedule",
  "action": "timetable",
  "actionType": "view",
  "payload": {
    "inst_id": 1,
    "sectionId": 1
  }
}
```

---

## 6. Allocation Submodule — `sm_allocation`

### `facultyAllocation` — Faculty Teaching Assignments

#### `add` — Assign Faculty to Subject & Class
```json
{
  "mod": "m_timetable",
  "subMod": "sm_allocation",
  "action": "facultyAllocation",
  "actionType": "add",
  "payload": {
    "inst_id": 1,
    "facultyId": 102,
    "courseOfferingId": 45,
    "weeklyHours": 4
  }
}
```

#### `view` — View Faculty Allocations
```json
{
  "mod": "m_timetable",
  "subMod": "sm_allocation",
  "action": "facultyAllocation",
  "actionType": "view",
  "payload": { "inst_id": 1, "facultyId": 102 }
}
```

---

### `roomAllocation` — Room & Venue Assignments

#### `add` — Assign Venue/Room to Schedule Slot
```json
{
  "mod": "m_timetable",
  "subMod": "sm_allocation",
  "action": "roomAllocation",
  "actionType": "add",
  "payload": {
    "inst_id": 1,
    "roomId": 304,
    "timetableSlotId": 1012
  }
}
```

---

## 7. Substitution Submodule — `sm_substitution`

### `substitution` — Temporary Faculty Substitute Management

#### `add` — Request/Assign Substitute Faculty
```json
{
  "mod": "m_timetable",
  "subMod": "sm_substitution",
  "action": "substitution",
  "actionType": "add",
  "payload": {
    "inst_id": 1,
    "originalFacultyId": 102,
    "substituteFacultyId": 108,
    "timetableSlotId": 1012,
    "substitutionDate": "2026-09-15",
    "reason": "Medical leave"
  }
}
```

---

## 8. Approval Submodule — `sm_approval`

### `timetableApproval` — Workflow Approval & Sign-Off

#### `add` — Submit or Approve Timetable
```json
{
  "mod": "m_timetable",
  "subMod": "sm_approval",
  "action": "timetableApproval",
  "actionType": "add",
  "payload": {
    "timetableId": 42,
    "status": "APPROVED",
    "remarks": "Approved by HOD"
  }
}
```

#### `view` — Check Approval Status
```json
{
  "mod": "m_timetable",
  "subMod": "sm_approval",
  "action": "timetableApproval",
  "actionType": "view",
  "payload": { "timetableId": 42 }
}
```
