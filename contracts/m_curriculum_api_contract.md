# m_curriculum API Contract

**Version:** 2.0  
**Last verified:** 2026-07-29  
**Module:** `m_curriculum`  
**Base URL:** `https://dev.globaloneapp.com` (local default: `http://127.0.0.1:8000`)

This document outlines the API surface for the Curriculum Management module (`m_curriculum`), covering academic degree programmes, terms/semesters, course offerings, and syllabus definitions.

---

## 1. Transport & Common Request Format

All calls use standard framework gateway (`POST /`):

```json
{
  "mod": "m_curriculum",
  "subMod": "sm_programme",
  "action": "programme",
  "actionType": "add",
  "payload": {}
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `mod` | string | Yes | Must be `m_curriculum`. |
| `subMod` | string | Yes | Must be one of: `sm_programme`, `sm_term`, `sm_course`, `sm_syllabus`. |
| `action` | string | Yes | Action string (`programme`, `term`, `course`, `syllabus`). |
| `actionType` | string | Yes | One of `add`, `view`, `update`, `delete`. |
| `payload` | object | Yes | Action-specific request payload. |

---

## 2. Submodule Index

| Submodule (`subMod`) | Action (`action`) | Action Types | Description |
|---|---|---|---|
| `sm_programme` | `programme` | `add`, `view`, `update`, `delete` | Degree programme definitions |
| `sm_term` | `term` | `add`, `view`, `update`, `delete` | Academic term / semester structure |
| `sm_course` | `course` | `add`, `view`, `update`, `delete` | Course catalog & credit definitions |
| `sm_syllabus` | `syllabus` | `add`, `view`, `update`, `delete` | Syllabus topics & unit outlines |

---

## 3. Submodule: Programme Management (`sm_programme`)

### 3.1 `add` — Create Degree Programme

```json
{
  "mod": "m_curriculum",
  "subMod": "sm_programme",
  "action": "programme",
  "actionType": "add",
  "payload": {
    "instId": 1,
    "programmeCode": "BTECH-CS",
    "programmeName": "Bachelor of Technology in Computer Science",
    "degreeTypeId": 1,
    "durationYears": 4,
    "totalSemesters": 8
  }
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `instId` | integer | Yes | Target institution ID (> 0). |
| `programmeCode` | string | Yes | Unique code identifier (e.g. `BTECH-CS`). |
| `programmeName` | string | Yes | Full programme name. |
| `degreeTypeId` | integer | Yes | Degree level lookup ID (UG=1, PG=2, PhD=3). |
| `durationYears` | integer | Yes | Programme length in years. |
| `totalSemesters` | integer | Yes | Total number of terms/semesters. |

---

## 4. Submodule: Course Catalog (`sm_course`)

### 4.1 `add` — Define Course

```json
{
  "mod": "m_curriculum",
  "subMod": "sm_course",
  "action": "course",
  "actionType": "add",
  "payload": {
    "instId": 1,
    "courseCode": "CS101",
    "courseName": "Data Structures & Algorithms",
    "credits": 4,
    "lectureHours": 3,
    "labHours": 2,
    "isElective": false
  }
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `instId` | integer | Yes | Institution ID (> 0). |
| `courseCode` | string | Yes | Unique course code (e.g. `CS101`). |
| `courseName` | string | Yes | Descriptive course title. |
| `credits` | number | Yes | Total academic credits. |
| `lectureHours` | number | Yes | Weekly lecture hours. |
| `labHours` | number | Yes | Weekly practical lab hours. |
| `isElective` | boolean | No | Elective course flag (default: `false`). |
