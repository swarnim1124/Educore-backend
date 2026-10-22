# m_exam API Contract

**Version:** 1.1  
**Last verified:** 2026-07-28  
**Module:** `m_exam` — examinations and results  
**Base URL:** `https://dev.globaloneapp.com` (local default: `http://127.0.0.1:8000`)

This contract is based on the implemented `m_exam` handlers. It includes the canonical BRS route names, input fields, returned data, workflow verbs, and current implementation gaps.

## 1. Transport, envelope, and response

All Exam calls use `POST /` with `Content-Type: application/json`.

```json
{
  "mod": "m_exam",
  "subMod": "sm_schedule",
  "action": "examSchedule",
  "actionType": "view",
  "payload": {}
}
```

| Envelope field | Type | Required | Rule |
|---|---|---:|---|
| `mod` | string | Yes | `m_exam` |
| `subMod` | string | Yes | Canonical name in the route table. |
| `action` | string | Yes | Canonical action in the route table. |
| `actionType` | string | Yes | Usually `add`, `view`, `update`, or `delete`; workflow actions accept the aliases documented below. |
| `payload` | object | Yes | Operation input. |

Send `Authorization: Bearer <jwt>` for authenticated context. The shared framework parses the JWT into `ExecutionContext.security`.

Success:

```json
{ "status": "success", "message": "…", "data": {} }
```

Business error (normally still HTTP `200`):

```json
{ "status": "error", "message": "scheduleId is required", "error_code": "400" }
```

`error_code` may be absent or empty on individual handler errors. Invalid request-envelope validation returns HTTP `422` with `ERR422`; unhandled framework errors return HTTP `500` with full stack traces in development. Always branch on `body.status`.

The server also returns `X-Request-ID` and `X-Process-Time-Ms` headers. Incoming request payloads are recorded in JSON execution logs (`oneapp_requests.log`), with sensitive parameters automatically masked.

## 2. Canonical routes

Use the names below.

| Submodule | Action | Main purpose |
|---|---|---|
| `sm_exam_center` | `examCentre` | Exam centre CRUD |
| `sm_schedule` | `examSchedule` | Schedule CRUD |
| `sm_schedule` | `examSchedulePublication` | Publish/hold/unpublish schedule |
| `sm_seating` | `seatingPlan` | Seat allocations |
| `sm_invigilation` | `invigilatorAssignment` | Invigilator assignments |
| `sm_hall_ticket` | `hallTicket` | Hall-ticket generation |
| `sm_hall_ticket` | `hallTicketPublication` | Hall-ticket publication |
| `sm_hall_ticket` | `studentBlock` | Student exam blocks |
| `sm_question_paper` | `questionPaper` | Question paper lifecycle |
| `sm_question_paper` | `questionPaperSubmission` | Submission lifecycle |
| `sm_question_paper` | `questionPaperApproval` | Approval lifecycle |
| `sm_question_paper` | `questionBank` | Question-bank CRUD |
| `sm_external_exam` | `externalExaminer`, `externalPaperSetting`, `externalEvaluation` | External exam workflows |
| `sm_internal_exam` | `internalExam`, `internalMarksEntry`, `internalMarksConsolidation` | CIE workflows |
| `sm_marks` | `marksEntry`, `marksVerification`, `grade`, `gradeLock` | Marks and grades |
| `sm_evaluation` | `evaluationBundle`, `secondValuation`, `moderation` | Evaluation workflows |
| `sm_results` | `result` | Results generation/view |
| `sm_result_approval` | `resultApproval`, `resultPublication` | Result approval/publication |
| `sm_revaluation` | `revaluationRequest`, `revaluationProcessing`, `photocopyRequest`, `appeal`, `challengeRevaluation` | Post-result workflows |
| `sm_supplementary` | `supplementaryExam`, `supplementaryRegistration` | Supplementary exam workflows |
| `sm_reappear` | `reappearExam`, `reappearRegistration`, `reappearEligibility` | Reappear/improvement workflows |
| `sm_malpractice` | `malpracticeCase` | Malpractice cases |

## 3. Centres, schedules, seating, and invigilation

### Exam centre — `sm_examCenter / examCentre`

| actionType | Required payload | Optional payload | Successful `data` |
|---|---|---|---|
| `add` (also `create`) | `centreName`, `capacity` positive integer | `inst_id`/`instId`, `address`, `courses` array | Created centre row, or `{ centreName, capacity, courses, status: "active" }` |
| `view` (also `read`) | — | `inst_id`/`instId`, `centreId` | Array of centre rows |
| `update` | `centreId` | `capacity` positive integer, `courses`, `address` | Updated row, or `{ centreId }` |
| `delete` | `centreId` | `reason` | `{ centreId, reason }`; centre is deactivated, not removed |

Example create:

```json
{ "mod": "m_exam", 
  "subMod": "sm_examCenter", 
  "action": "examCentre", 
  "actionType": "add", 
  "payload": { 
        "instId": 1, 
        "centreName": "Main Campus Hall", 
        "capacity": 300, 
        "address": "Block A", 
        "courses": [101, 102] 
        } 
}
```

### Exam schedule — `sm_schedule / examSchedule`

| actionType | Required payload | Optional payload | Successful `data` |
|---|---|---|---|
| `add` (also `create`) | `examName`, `fromDate`, `toDate`, non-empty `courses[]`, non-empty `sessions[]` | `examType` (default `regular`), `inst_id`/`instId` | Created schedule row; fallback `{ examName, status: "draft", version: 1 }` |
| `view` (also `read`) | — | `inst_id`/`instId`, `scheduleId`, `versionHistory` boolean | Array of schedule rows; response additionally includes top-level `version_history` |
| `update` | `scheduleId` | `courses`, `fromDate`, `toDate`, `sessions` | `{ scheduleId }` |
| `delete` | `scheduleId` | `reason` | `{ scheduleId, reason }` |

Schedule rows are database-shaped, with fields such as `id`, `inst_id`, `exam_name`, `exam_type`, `from_date`, `to_date`, `courses`, `sessions`, and `status`. A published schedule cannot be updated unless it is put on hold or unpublished first.

```json
{ "mod": "m_exam", 
"subMod": "sm_schedule", 
"action": "examSchedule", 
"actionType": "add", 
"payload": { 
      "instId": 1, 
      "examName": "Semester End Examination", 
      "examType": "regular", 
      "fromDate": "2026-11-01", 
      "toDate": "2026-11-15", 
      "courses": [101, 102], 
      "sessions": [{ 
            "date": "2026-11-01", 
            "session": "FN" 
            }] 
      } 
}
```

### Schedule publication — `sm_schedule / examSchedulePublication`

| actionType | Required payload | Optional payload | Response `data` |
|---|---|---|---|
| `add` or `publish` | `scheduleId` | — | `{ scheduleId, status: "published" }` |
| `view` | — | `scheduleId` | `{ scheduleId, status: "published" }` |
| `update` or `hold` | `scheduleId` | `reason` | `{ scheduleId, status: "on-hold", reason }` |
| `delete` or `unpublish` | `scheduleId` | `reason` | `{ scheduleId, status: "draft", reason }` |

### Seating plan — `sm_seating / seatingPlan`

| actionType | Required payload | Optional payload | Response `data` |
|---|---|---|---|
| `add`, `create`, or `generate` | `scheduleId`, `venueId`, `courseId` | `allocationMethod` (default `auto`), `studentIds[]` | Created plan or `{ scheduleId, venueId, totalAllocated, allocationMethod }` |
| `view`/`read` | — | `scheduleId`, `venueId`, `studentId` | Array of seating rows |
| `update` | `seatingPlanId` | `reassignSeats` boolean, `studentIds[]` | `{ seatingPlanId, reassignSeats, updatedStudentsCount }` |
| `delete` | `seatingPlanId` | `reason` | `{ seatingPlanId, reason }` |

Seat numbers generated by the backend are `S-001`, `S-002`, etc. A role check attempts to restrict a `Student` role to its own row, but uses `context.security.role` rather than the JWT roles array; do not rely on it for access control.

### Invigilation — `sm_invigilation / invigilatorAssignment`

| actionType | Required payload | Optional payload | Response `data` |
|---|---|---|---|
| `add`, `create`, or `assign` | `scheduleId`, `venueId`, `facultyId` | `dutyType` (default `assistant_invigilator`) | Assigned row or `{ scheduleId, venueId, facultyId, dutyType }` |
| `view`/`read` | — | `scheduleId`, `facultyId` | Array of assignment rows |
| `update` or `swap` | `assignmentId`, `facultyId` | `dutyType` | `{ assignmentId, newFacultyId, dutyType }` |
| `delete` | `assignmentId` | `reason` | `{ assignmentId, reason }` |

## 4. Hall tickets

### Hall ticket — `sm_hallTicket / hallTicket`

| actionType | Required payload | Optional payload | Response `data` |
|---|---|---|---|
| `add`, `create`, or `generate` | `scheduleId`, `studentIds[]` | `venueDetails` | Created ticket(s) or generated summary |
| `view`/`read` | `scheduleId` | `studentId` | Array of ticket rows |
| `update` | `hallTicketId` | `seatNumber`, `venueDetails` | `{ hallTicketId, seatNumber, venueDetails }` |
| `delete` | `hallTicketId` | `reason` | `{ hallTicketId, reason }` |

### Hall-ticket publication — `sm_hallTicket / hallTicketPublication`

| actionType | Required payload | Optional payload | Response `data` |
|---|---|---|---|
| `add` or `publish` | `scheduleId` | — | `{ scheduleId, status: "published" }` |
| `view` | `scheduleId` | — | Publication status |
| `update` or `hold` | `scheduleId` | `reason` | `{ scheduleId, status: "on-hold", reason }` |
| `delete` or `unpublish` | `scheduleId` | `reason` | `{ scheduleId, status: "unpublished", reason }` |

### Student block — `sm_hallTicket / studentBlock`

| actionType | Required payload | Optional payload | Response `data` |
|---|---|---|---|
| `add`/`create` | `studentId`, `scheduleId`, `reason` | `blockedBy` | Created block row/summary |
| `view`/`read` | `studentId` | `scheduleId` | Array of block rows |
| `update` | `blockId` | `reason` | Block update summary |
| `delete` | `blockId` | `reason` | `{ blockId, reason }` |

## 5. Question papers and external examination

### Question-paper routes — `sm_questionPaper`

| Action | actionType → required payload | Optional payload / result |
|---|---|---|
| `questionPaper` | `add`: `scheduleId`, `courseId`, `setBy`; `view`: any of `scheduleId`, `courseId`, `questionPaperId`; `update`: `questionPaperId`; `delete`: `questionPaperId` | `content`, `remarks`, `reason`. Create returns paper data; view returns paper rows; update/delete return status summary. |
| `questionPaperSubmission` | `add`: `questionPaperId`; `view`: `submissionId` or `questionPaperId`; `update`: `submissionId`; `delete`: `submissionId` | `remarks`, `reason`. `add` submits a paper. |
| `questionPaperApproval` | `add`: `questionPaperId`; `view`: `questionPaperId`; `update`: `questionPaperId`; `delete`: `questionPaperId` | `remarks`, `reason`. `add` approves; `update` requests changes; `delete` rejects. |
| `questionBank` | `add`: `courseId`, `content`; `view`: optional `courseId`, `bankId`; `update`: `bankId`; `delete`: `bankId` | `category`, `difficultyLevel`, `tags`, `reason`. |

Example paper creation:

```json
{ "mod": "m_exam", "subMod": "sm_questionPaper", "action": "questionPaper", "actionType": "add", "payload": { "scheduleId": 9, "courseId": 101, "setBy": 22, "content": "<document reference>", "remarks": "Set A" } }
```

### External examination — `sm_externalExam`

| Action | actionType → required payload | Optional payload / result |
|---|---|---|
| `externalExaminer` | `add`: `examinerName`; `view`: optional `examinerId`; `update`/`delete`: `examinerId` | `qualification`, `specialization`, `contactEmail`, `contactPhone`, `inst_id`, `reason`. |
| `externalPaperSetting` | `add`: `examinerId`, `courseId`, `scheduleId`; `view`: optional `examinerId`, `courseId`, `scheduleId`; `update`/`delete`: assignment identifier supplied as `examinerId` | `remarks`, `reason`. |
| `externalEvaluation` | `add`: `examinerId`, `scheduleId`, `scriptBundleIds[]`; `view`: optional `evaluationId`, `examinerId`, `scheduleId`; `update`/`delete`: `evaluationId` | `marks`, `discrepancyDetected`, `remarks`, `reason`. |

## 6. Internal exams, marks, grading, and evaluation

### Internal exam — `sm_internalExam`

| Action | actionType → required payload | Optional payload / result |
|---|---|---|
| `internalExam` | `add`: `courseOfferingId`, `examName`, `examTypeId`, `examDate`, `totalMaxMarks`; `view`: optional `internalExamId`, `courseOfferingId`, `academicTermId`; `update`/`delete`: `internalExamId` | `statusId`, `reason`. |
| `internalMarksEntry` | `add`: `internalExamId`, `records[]`; `view`: optional `internalExamId`, `studentId`, `componentId`; `update`/`delete`: `markId` | `componentId`, `overrideMarks`, `reason`. `records[]` is the marks batch. |
| `internalMarksConsolidation` | `add`: `internalExamId`; `view`: optional `internalExamId`, `studentId`; `update`/`delete`: `consolidationId` | `components[]`, `reason`. |

### Marks and grades — `sm_marks`

| Action | actionType → required payload | Optional payload / result |
|---|---|---|
| `marksEntry` | `add`: `scheduleId`, `courseId`, `examinerId`, `records[]`; `view`: optional `scheduleId`, `courseId`; `update`/`delete`: `marksEntryId` | `reason`, `remarks`. |
| `marksVerification` | `add`: `scheduleId`, `courseId`, `verifiedBy`; `view`: `scheduleId`, `courseId`; `update`: `scheduleId`, `courseId`; `delete`: `scheduleId`, `courseId` | `remarks`, `reason`. `add` verifies; `update` flags a discrepancy. |
| `grade` | `add`: `scheduleId`, `studentId`, `courseId`, `grade`; `view`: optional `scheduleId`, `studentId`, `courseId`; `update`/`delete`: `gradeId` | `gradingSchemeId`, `remarks`, `reason`. `add` generates; `update` overrides. |
| `gradeLock` | `add`: `scheduleId`; `view`: optional `scheduleId`, `lockId`; `update`: `lockId`; `delete`: `lockId` | `reason`. `add` locks grades; `delete` unlocks them. |

`records[]` is passed directly to the data layer. For mark-entry batches, each record should identify the student and the marks value required by the institution’s marks schema, for example `{ "studentId": 42, "marks": 78 }`.

### Evaluation — `sm_evaluation`

| Action | actionType → required payload | Optional payload / result |
|---|---|---|
| `evaluationBundle` | `add`: `scheduleId`, `courseId`, `evaluatorId`, `studentIds[]`; `view`: optional `bundleId`, `scheduleId`, `evaluatorId`; `update`/`delete`: `bundleId` | `reason`. |
| `secondValuation` | `add`: `bundleId`, `secondEvaluatorId`; `view`: optional `secondValuationId`, `bundleId`; `update`/`delete`: `secondValuationId` | `marks`, `reason`. |
| `moderation` | `add`: `scheduleId`, `courseId`, `moderationRule`; `view`: optional `moderationId`, `scheduleId`, `courseId`; `update`/`delete`: `moderationId` | `adjustment`, `reason`. |

## 7. Results, approvals, and publication

### Results — `sm_results / result`

| actionType | Required payload | Optional payload | Response `data` |
|---|---|---|---|
| `add` or `generate` | `scheduleId` | — | Result-generation summary, typically generated-result count/status |
| `view`/`read` | — | `scheduleId`, `studentId` | Array of result rows |
| `update` | `scheduleId` | `reason` | Result update/recalculation summary |
| `delete` | `scheduleId` | `reason` | Result removal/reversal summary |

### Result approval — `sm_resultApproval / resultApproval`

| actionType | Required payload | Optional payload | Response `data` |
|---|---|---|---|
| `add` or `approve` | `scheduleId` | `remarks` | Approval summary |
| `view` | `scheduleId` | — | Array of approval rows |
| `update` | `scheduleId` | `remarks` | Approval update summary |
| `delete` or `reject` | `scheduleId` | `reason` | Rejection summary |

### Result publication — `sm_resultApproval / resultPublication`

| actionType | Required payload | Optional payload | Response `data` |
|---|---|---|---|
| `add` or `publish` | `scheduleId` | — | `{ scheduleId, status: "published" }` |
| `view` | `scheduleId` | — | Publication record/status |
| `update` or `hold` | `scheduleId` | `reason` | `{ scheduleId, status: "on-hold", reason }` |
| `delete` or `unpublish` | `scheduleId` | `reason` | `{ scheduleId, status: "unpublished", reason }` |

## 8. Revaluation, supplementary, reappear, and malpractice

### Revaluation — `sm_revaluation`

| Action | actionType → required payload | Optional payload / result |
|---|---|---|
| `revaluationRequest` | `add`: `studentId`, `scheduleId`, `courseId`; `view`: optional `requestId`, `studentId`, `scheduleId`; `update`/`delete`: `requestId` | `reason`, `remarks`. |
| `revaluationProcessing` | `add`: `revaluationRequestId`, `reEvaluatorId`; `view`: optional `requestId`, `revaluationRequestId`; `update`: `requestId`, `revisedMarks`; `delete`: `requestId` | `remarks`, `reason`. |
| `photocopyRequest` | `add`: `studentId`, `scheduleId`, `courseId`; `view`: optional `requestId`, `studentId`; `update`/`delete`: `requestId` | `reason`, `remarks`. |
| `appeal` | `add`: `studentId`, `referenceId`, `referenceType`; `view`: optional `appealId`, `studentId`; `update`: `appealId`, `decision`; `delete`: `appealId` | `remarks`, `reason`. |
| `challengeRevaluation` | `add`: `studentId`, `scheduleId`, `courseId`; `view`: optional `challengeId`, `studentId`; `update`: `challengeId`, `decision`; `delete`: `challengeId` | `panelMembers[]`, `remarks`, `reason`. |

### Supplementary — `sm_supplementary`

| Action | actionType → required payload | Optional payload / result |
|---|---|---|
| `supplementaryExam` | `add`: `inst_id`, `fromDate`, `toDate`, `courses[]`/`courseIds[]`; `view`: optional `supplementaryExamId`, `inst_id`; `update`/`delete`: `supplementaryExamId` | `registrationWindow`, `isWindowOpen`, `reason`. |
| `supplementaryRegistration` | `add`: `studentId`, `supplementaryExamId`, `courseIds[]`; `view`: optional `registrationId`, `studentId`, `supplementaryExamId`; `update`/`delete`: `registrationId` | `reason`. |

### Reappear/improvement — `sm_reappear`

| Action | actionType → required payload | Optional payload / result |
|---|---|---|
| `reappearExam` | `add`: `inst_id`, `academicTermId`, `examStartDate`, `examEndDate`, `courses[]`/`courseIds[]`; `view`: optional `reappearExamId`, `inst_id`; `update`/`delete`: `reappearExamId` | `registrationStartDate`, `registrationEndDate`, `reason`. |
| `reappearRegistration` | `add`: `studentId`, `reappearExamId`, `courseIds[]`; `view`: optional `registrationId`, `studentId`, `reappearExamId`; `update`/`delete`: `registrationId` | `reason`. |
| `reappearEligibility` | `add`: `studentId`, `courseId`, `reappearExamId`; `view`: optional `eligibilityId`, `studentId`, `reappearExamId`; `update`/`delete`: `eligibilityId` | `eligibilityCriteria`, `attemptsExceeded`, `reason`. |

### Malpractice — `sm_malpractice / malpracticeCase`

| actionType | Required payload | Optional payload | Result |
|---|---|---|---|
| `add` or `report` | `studentId`, `scheduleId`, `description`, `reportedBy` | — | Created case data/summary |
| `view`/`read` | — | `caseId`, `studentId`, `scheduleId` | Array of case rows |
| `update` | `caseId` | `committee`, `hearingDate`, `verdict` | Updated case data/summary |
| `delete` or `dismiss` | `caseId` | `reason` | Dismissal summary |

## 9. Common payload conventions

| Field | Meaning |
|---|---|
| `inst_id` / `instId` | Institution ID. Some actions default to the JWT institution ID or `1`. |
| `scheduleId` | Exam schedule ID. |
| `courseId`, `courseIds`, `courses` | A course identifier, identifiers array, or course definitions array, depending on the action. |
| `studentId`, `studentIds` | Student identifier or batch of student IDs. |
| `records` | Batch payload for marks. Send an array; its per-record schema is institution-specific. |
| `reason`, `remarks` | Free-text audit/workflow explanation. A handler often supplies a default when omitted. |
| `fromDate`, `toDate`, `examDate` | Use ISO date strings (`YYYY-MM-DD`) unless the database contract requires a timestamp. |

## 10. Important current limitations

| Area | Current implementation behavior |
|---|---|
| Authorization | Permissions declared in the manifest are not consistently checked by handlers. Protect sensitive operations outside the module until RBAC is enforced. |
| Workflow persistence | Several update/delete and publication operations return a successful workflow summary without writing a corresponding database change. Verify critical state with a `view` call. |
| Read schemas | Many views return raw data-layer/database rows. Field names may be snake_case and vary by table. Client code should not assume all example fields exist on every row. |
| Required-field checks | Validation varies per action. A successful response does not necessarily guarantee a complete domain validation beyond the fields listed above. |
| Role checks | Seating and invigilation attempt role-based self-filtering through `context.security.role`; the standard JWT context provides `roles`, so this restriction may not activate. |
| Schedule delete | The current handler returns a draft-delete success response but does not invoke a data-layer delete. |
| Custom aliases | `create`, `read`, `generate`, `assign`, `swap`, `publish`, `hold`, `unpublish`, `approve`, `reject`, `report`, and `dismiss` are handler-specific aliases. Prefer the documented canonical action types when integrating. |

## 11. Frontend checklist

1. Use `POST /`, the exact envelope, and the canonical route/action names in §2.
2. Treat `body.status === "error"` as failure even when HTTP is `200`.
3. Store IDs returned by `view` calls; some create flows do not return an ID suitable for a later update/delete.
4. Re-fetch schedule, publication, and workflow state after a mutation that is operationally important.
5. Display backend `message` verbatim for validation feedback and include `X-Request-ID` when reporting a failure.

## 12. Change log

| Date | Version | Notes |
|---|---|---|
| 2026-07-24 | 1.0 | Initial API contract for all implemented `m_exam` routes and workflow handlers. |
