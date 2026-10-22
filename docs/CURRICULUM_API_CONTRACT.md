# OneApp Curriculum API Contract

This document defines the API Contract for the `m_curriculum` module based on the BRS, Framework Standards, and verified Database Metadata. Any inferred implementations are clearly marked with **[INFERRED]**.

---
## API Name
Programme Management (Add)

## Module
m_curriculum

## Submodule
sm_programme

## Action
programme

## ActionType
add

## Purpose
Creates a degree programme.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `institutionId` | bigint | Yes | Institution ID |
| `departmentId` | bigint | Yes | Department ID |
| `progCode` | varchar | Yes | Programme Code |
| `progName` | varchar | Yes | Programme Name |
| `progTypeId` | smallint | Yes | Programme Type Lookup ID |
| `duration` | smallint | Yes | Duration |
| `durationUnitId` | smallint | Yes | Duration Unit Lookup ID |
| `totalTerms` | smallint | Yes | Total terms/semesters |
| `totalCredits` | numeric | Yes | Total credits required |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Contains the created `programmeId` |

## Validation Rules
- Mandatory fields: `progCode`, `progName`, `progTypeId`, `duration`, `durationUnitId`, `totalTerms`, `totalCredits`.
- Unique constraint: `uk_prog_code`.
- Unique constraint: `uk_prog_name`.
- Lookup validation: `progTypeId`, `durationUnitId`.
- FK validation: `institutionId`, `departmentId`.

## Database Tables
- `sch_academic_struct.tb_prog` (WRITE)
- `sch_lookup.tb_lookup` (READ)
- `sch_org.tb_inst` (READ)
- `sch_org.tb_dept` (READ)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None [INFERRED: tb_prog lacks created_by/updated_by columns]

## Possible Error Codes
- Validation Error
- Conflict
- Dependency Error

## Dependencies
Organization, Lookup

## Notes


---
## API Name
Programme Management (View)

## Module
m_curriculum

## Submodule
sm_programme

## Action
programme

## ActionType
view

## Purpose
Returns programme details.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `programmeId` | integer | No | Specific programme ID to view |
| `institutionId` | bigint | No | Filter by institution |
| `departmentId` | bigint | No | Filter by department |
| `progTypeId` | smallint | No | Filter by degree type |
| `page` | integer | No | Pagination page |
| `limit` | integer | No | Pagination limit |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | array | List of programme records matching criteria |

## Validation Rules
- Mandatory fields: None.

## Database Tables
- `sch_academic_struct.tb_prog` (READ)

## Transaction Scope
Read Only

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Programme Management (Update)

## Module
m_curriculum

## Submodule
sm_programme

## Action
programme

## ActionType
update

## Purpose
Updates programme.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `programmeId` | integer | Yes | Programme ID |
| `progName` | varchar | No | Programme Name |
| `totalCredits` | numeric | No | Total credits required |
| `totalTerms` | smallint | No | Total terms |
| `statusId` | smallint | No | Status Lookup ID |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Updated programme object |

## Validation Rules
- Mandatory fields: `programmeId`.
- Unique constraint: `uk_prog_name`.

## Database Tables
- `sch_academic_struct.tb_prog` (UPDATE)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found
- Conflict

## Dependencies
None

## Notes


---
## API Name
Programme Management (Delete)

## Module
m_curriculum

## Submodule
sm_programme

## Action
programme

## ActionType
delete

## Purpose
Deactivates programme.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `programmeId` | integer | Yes | Programme ID |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `programmeId`.
- FK validation: Ensure no dependencies block deletion.

## Database Tables
- `sch_academic_struct.tb_prog` (UPDATE)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found
- Dependency Error

## Dependencies
None

## Notes


---
## API Name
Programme Approval (Add)

## Module
m_curriculum

## Submodule
sm_programme

## Action
programmeApproval

## ActionType
add

## Purpose
Approves programme creation or modification.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `programmeId` | integer | Yes | Programme ID |
| `remarks` | string | No | Approval remarks |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Approval result |

## Validation Rules
- Mandatory fields: `programmeId`.
- FK validation: `programmeId`.

## Database Tables
- `sch_academic_struct.tb_prog` (UPDATE)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
Lookup

## Notes
BRS mentions remarks, but `tb_prog` lacks a remarks column. [INFERRED: Remarks persistence requires Gap Analysis reference].

---
## API Name
Programme Approval (View)

## Module
m_curriculum

## Submodule
sm_programme

## Action
programmeApproval

## ActionType
view

## Purpose
Returns approval queue.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `approverId` | bigint | No | Approver ID filter |
| `programmeId` | integer | No | Programme ID filter |
| `statusFilter` | smallint | No | Status ID filter |
| `page` | integer | No | Pagination page |
| `limit` | integer | No | Pagination limit |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | array | List of programmes pending approval |

## Validation Rules
- Mandatory fields: None.

## Database Tables
- `sch_academic_struct.tb_prog` (READ)

## Transaction Scope
Read Only

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
None

## Dependencies
None

## Notes


---
## API Name
Programme Approval (Update)

## Module
m_curriculum

## Submodule
sm_programme

## Action
programmeApproval

## ActionType
update

## Purpose
Changes previous decision or requests revision from submitter.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `programmeId` | integer | Yes | Programme ID |
| `remarks` | string | No | Revision remarks |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `programmeId`.
- FK validation: `programmeId`.

## Database Tables
- `sch_academic_struct.tb_prog` (UPDATE)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
Lookup

## Notes


---
## API Name
Programme Approval (Delete)

## Module
m_curriculum

## Submodule
sm_programme

## Action
programmeApproval

## ActionType
delete

## Purpose
Rejects the programme proposal.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `programmeId` | integer | Yes | Programme ID |
| `remarks` | string | No | Rejection remarks |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `programmeId`.
- FK validation: `programmeId`.

## Database Tables
- `sch_academic_struct.tb_prog` (UPDATE)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
Lookup

## Notes


---
## API Name
Course Definition (Add)

## Module
m_curriculum

## Submodule
sm_course

## Action
courseDefinition

## ActionType
add

## Purpose
Creates a course in the institutional catalog.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `crsCode` | varchar | Yes | Course Code |
| `crsName` | varchar | Yes | Course Name |
| `crsTypeId` | smallint | Yes | Course Type Lookup ID |
| `creditValue` | numeric | Yes | Credits |
| `lectureHours` | numeric | Yes | Lecture Hours |
| `tutorialHours` | numeric | Yes | Tutorial Hours |
| `practicalHours` | numeric | Yes | Practical Hours |
| `description` | string | No | Description |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Created course ID and version ID |

## Validation Rules
- Mandatory fields: `crsCode`, `crsName`, `crsTypeId`, `creditValue`.
- Unique constraint: `uk_crs_code`.
- Lookup validation: `crsTypeId`.

## Database Tables
- `sch_academic_struct.tb_crs` (WRITE)
- `sch_academic_struct.tb_crs_version` (WRITE)

## Transaction Scope
Multi-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Conflict

## Dependencies
Lookup

## Notes
[INFERRED] `institutionId` and `departmentId` are omitted as they do not exist on `tb_crs` per Gap Analysis.

---
## API Name
Course Definition (View)

## Module
m_curriculum

## Submodule
sm_course

## Action
courseDefinition

## ActionType
view

## Purpose
Returns course catalog.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `courseDefinitionId` | integer | No | Course ID |
| `crsTypeId` | smallint | No | Filter by type |
| `searchQuery` | string | No | Search by name/code |
| `page` | integer | No | Pagination page |
| `limit` | integer | No | Pagination limit |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | array | Course definitions |

## Validation Rules
- Mandatory fields: None.

## Database Tables
- `sch_academic_struct.tb_crs` (READ)
- `sch_academic_struct.tb_crs_version` (READ)

## Transaction Scope
Read Only

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Course Definition (Update)

## Module
m_curriculum

## Submodule
sm_course

## Action
courseDefinition

## ActionType
update

## Purpose
Updates course definition.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `courseDefinitionId` | integer | Yes | Course ID |
| `crsName` | varchar | No | Course Name |
| `creditValue` | numeric | No | Credits |
| `crsTypeId` | smallint | No | Course Type |
| `description` | string | No | Description |
| `statusId` | smallint | No | Status |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Updated course details |

## Validation Rules
- Mandatory fields: `courseDefinitionId`.
- FK validation: `courseDefinitionId`.

## Database Tables
- `sch_academic_struct.tb_crs` (UPDATE)
- `sch_academic_struct.tb_crs_version` (WRITE) [INFERRED if versioning triggered]

## Transaction Scope
Multi-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Course Definition (Delete)

## Module
m_curriculum

## Submodule
sm_course

## Action
courseDefinition

## ActionType
delete

## Purpose
Deactivates course from catalog.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `courseDefinitionId` | integer | Yes | Course ID |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `courseDefinitionId`.
- FK validation: `courseDefinitionId`.

## Database Tables
- `sch_academic_struct.tb_crs` (UPDATE)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found
- Dependency Error

## Dependencies
None

## Notes


---
## API Name
Course Outcome (Add)

## Module
m_curriculum

## Submodule
sm_course

## Action
courseOutcome

## ActionType
add

## Purpose
Defines Course Outcomes (COs) for OBE.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `courseDefinitionId` | integer | Yes | Course ID |
| `outcomes` | array | Yes | Array of CO objects |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Created COs |

## Validation Rules
- Mandatory fields: `courseDefinitionId`, `outcomes`.
- FK validation: `courseDefinitionId`.

## Database Tables
- [INFERRED] Reference Gap Analysis: Table missing

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Course Outcome (View)

## Module
m_curriculum

## Submodule
sm_course

## Action
courseOutcome

## ActionType
view

## Purpose
Returns all COs for a course.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `courseDefinitionId` | integer | Yes | Course ID |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | array | List of COs |

## Validation Rules
- Mandatory fields: `courseDefinitionId`.

## Database Tables
- [INFERRED] Reference Gap Analysis: Table missing

## Transaction Scope
Read Only

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Course Outcome (Update)

## Module
m_curriculum

## Submodule
sm_course

## Action
courseOutcome

## ActionType
update

## Purpose
Updates course outcomes.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `courseDefinitionId` | integer | Yes | Course ID |
| `outcomes` | array | Yes | Array of modified CO objects |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `courseDefinitionId`, `outcomes`.

## Database Tables
- [INFERRED] Reference Gap Analysis: Table missing

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Course Outcome (Delete)

## Module
m_curriculum

## Submodule
sm_course

## Action
courseOutcome

## ActionType
delete

## Purpose
Removes a specific CO.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `courseDefinitionId` | integer | Yes | Course ID |
| `outcomeCode` | string | Yes | CO Code to delete |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `courseDefinitionId`, `outcomeCode`.

## Database Tables
- [INFERRED] Reference Gap Analysis: Table missing

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Course Requisite (Add)

## Module
m_curriculum

## Submodule
sm_course

## Action
courseRequisite

## ActionType
add

## Purpose
Adds a prerequisite or corequisite link between two courses.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `crsVersionId` | integer | Yes | Base Course Version ID |
| `requisiteCrsVersionId` | integer | Yes | Requisite Course Version ID |
| `requisiteType` | string | Yes | PRE or COREQ |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Created requisite |

## Validation Rules
- Mandatory fields: `crsVersionId`, `requisiteCrsVersionId`, `requisiteType`.
- CHECK constraint: `chk_crs_prerequisite`.
- Unique constraints: `uk_crs_prerequisite`, `uk_crs_corequisite`.

## Database Tables
- `sch_academic_struct.tb_crs_prerequisite` (WRITE)
- `sch_academic_struct.tb_crs_corequisite` (WRITE)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Conflict
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Course Requisite (View)

## Module
m_curriculum

## Submodule
sm_course

## Action
courseRequisite

## ActionType
view

## Purpose
Returns all prerequisites and corequisites for a course.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `crsVersionId` | integer | Yes | Course Version ID |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | array | List of requisites |

## Validation Rules
- Mandatory fields: `crsVersionId`.

## Database Tables
- `sch_academic_struct.tb_crs_prerequisite` (READ)
- `sch_academic_struct.tb_crs_corequisite` (READ)

## Transaction Scope
Read Only

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Course Requisite (Update)

## Module
m_curriculum

## Submodule
sm_course

## Action
courseRequisite

## ActionType
update

## Purpose
Changes a requisite.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `requisiteId` | integer | Yes | Requisite ID |
| `currentType` | string | Yes | PRE or COREQ |
| `newType` | string | Yes | PRE or COREQ |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `requisiteId`, `currentType`, `newType`.

## Database Tables
- `sch_academic_struct.tb_crs_prerequisite` (WRITE/DELETE)
- `sch_academic_struct.tb_crs_corequisite` (WRITE/DELETE)

## Transaction Scope
Multi-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Course Requisite (Delete)

## Module
m_curriculum

## Submodule
sm_course

## Action
courseRequisite

## ActionType
delete

## Purpose
Removes a requisite link.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `requisiteId` | integer | Yes | Requisite ID |
| `requisiteType` | string | Yes | PRE or COREQ |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `requisiteId`, `requisiteType`.

## Database Tables
- `sch_academic_struct.tb_crs_prerequisite` (DELETE)
- `sch_academic_struct.tb_crs_corequisite` (DELETE)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Curriculum Management (Add)

## Module
m_curriculum

## Submodule
sm_curriculum

## Action
curriculumManagement

## ActionType
add

## Purpose
Creates a curriculum.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `progId` | integer | Yes | Programme ID |
| `currName` | string | Yes | Curriculum Name |
| `terms` | array | Yes | Array of term objects |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Created curriculum ID and version ID |

## Validation Rules
- Mandatory fields: `progId`, `currName`, `terms`.
- Unique constraint: `uk_curr_name`.
- FK validation: `progId`.

## Database Tables
- `sch_academic_struct.tb_curr` (WRITE)
- `sch_academic_struct.tb_curr_version` (WRITE)
- `sch_academic_struct.tb_curr_term` (WRITE)
- `sch_academic_struct.tb_curr_term_crs` (WRITE)

## Transaction Scope
Multi-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Conflict
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Curriculum Management (View)

## Module
m_curriculum

## Submodule
sm_curriculum

## Action
curriculumManagement

## ActionType
view

## Purpose
Returns curriculum.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `currId` | integer | No | Curriculum ID |
| `progId` | integer | No | Filter by Programme |
| `page` | integer | No | Pagination page |
| `limit` | integer | No | Pagination limit |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | array | List of curricula |

## Validation Rules
- Mandatory fields: None.

## Database Tables
- `sch_academic_struct.tb_curr` (READ)
- `sch_academic_struct.tb_curr_version` (READ)
- `sch_academic_struct.tb_curr_term` (READ)
- `sch_academic_struct.tb_curr_term_crs` (READ)

## Transaction Scope
Read Only

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Curriculum Management (Update)

## Module
m_curriculum

## Submodule
sm_curriculum

## Action
curriculumManagement

## ActionType
update

## Purpose
Updates curriculum.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `currId` | integer | Yes | Curriculum ID |
| `terms` | array | Yes | Array of updated terms/courses |
| `statusId` | smallint | No | Status ID |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Updated data |

## Validation Rules
- Mandatory fields: `currId`.
- FK validation: `currId`.

## Database Tables
- `sch_academic_struct.tb_curr` (UPDATE)
- `sch_academic_struct.tb_curr_version` (WRITE/UPDATE)
- `sch_academic_struct.tb_curr_term` (WRITE/UPDATE)
- `sch_academic_struct.tb_curr_term_crs` (WRITE/UPDATE)

## Transaction Scope
Multi-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
None

## Notes


---
## API Name
Curriculum Management (Delete)

## Module
m_curriculum

## Submodule
sm_curriculum

## Action
curriculumManagement

## ActionType
delete

## Purpose
Deletes a draft curriculum.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `currId` | integer | Yes | Curriculum ID |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `currId`.
- FK validation: `currId`.

## Database Tables
- `sch_academic_struct.tb_curr` (UPDATE)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found
- Dependency Error

## Dependencies
None

## Notes


---
## API Name
Curriculum Approval (Add)

## Module
m_curriculum

## Submodule
sm_curriculum

## Action
curriculumApproval

## ActionType
add

## Purpose
Approves curriculum.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `currVersionId` | integer | Yes | Curriculum Version ID |
| `remarks` | string | No | Remarks |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `currVersionId`.
- FK validation: `currVersionId`.

## Database Tables
- `sch_academic_struct.tb_curr_version` (UPDATE)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
Lookup

## Notes


---
## API Name
Curriculum Approval (View)

## Module
m_curriculum

## Submodule
sm_curriculum

## Action
curriculumApproval

## ActionType
view

## Purpose
Returns curriculum approval queue.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `statusFilter` | smallint | No | Status ID |
| `page` | integer | No | Pagination page |
| `limit` | integer | No | Pagination limit |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | array | List of pending curricula |

## Validation Rules
- Mandatory fields: None.

## Database Tables
- `sch_academic_struct.tb_curr_version` (READ)

## Transaction Scope
Read Only

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
None

## Dependencies
None

## Notes


---
## API Name
Curriculum Approval (Update)

## Module
m_curriculum

## Submodule
sm_curriculum

## Action
curriculumApproval

## ActionType
update

## Purpose
Changes previous decision or requests revision.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `currVersionId` | integer | Yes | Curriculum Version ID |
| `remarks` | string | No | Remarks |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `currVersionId`.
- FK validation: `currVersionId`.

## Database Tables
- `sch_academic_struct.tb_curr_version` (UPDATE)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
Lookup

## Notes


---
## API Name
Curriculum Approval (Delete)

## Module
m_curriculum

## Submodule
sm_curriculum

## Action
curriculumApproval

## ActionType
delete

## Purpose
Rejects the curriculum.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `currVersionId` | integer | Yes | Curriculum Version ID |
| `remarks` | string | No | Remarks |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `currVersionId`.
- FK validation: `currVersionId`.

## Database Tables
- `sch_academic_struct.tb_curr_version` (UPDATE)

## Transaction Scope
Single-table Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
Lookup

## Notes


---
## API Name
Enrollment (Add)

## Module
m_curriculum

## Submodule
sm_enrollment

## Action
enrollment

## ActionType
add

## Purpose
Enrolls a student into a programme/batch.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `studId` | bigint | Yes | Student ID |
| `progIntakeId` | integer | Yes | Programme Intake ID |
| `admTypeId` | smallint | Yes | Admission Type ID |
| `enrollmentDate` | date | Yes | Enrollment Date |
| `expectedGraduationDate` | date | Yes | Expected Grad Date |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Created enrollment ID |

## Validation Rules
- Mandatory fields: `studId`, `progIntakeId`, `admTypeId`, `enrollmentDate`.
- Unique constraint: `uk_stud_enrollment`.
- FK validation: `studId`.

## Database Tables
- `sch_student.tb_stud_enrollment` (WRITE)

## Transaction Scope
Cross-schema Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
created_on, updated_on

## Possible Error Codes
- Validation Error
- Conflict
- Resource Not Found

## Dependencies
Student, Lookup

## Notes


---
## API Name
Enrollment (View)

## Module
m_curriculum

## Submodule
sm_enrollment

## Action
enrollment

## ActionType
view

## Purpose
Returns a single enrollment or a roster.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `enrollmentId` | bigint | No | Enrollment ID |
| `studId` | bigint | No | Student ID |
| `progIntakeId` | integer | No | Intake ID |
| `page` | integer | No | Pagination page |
| `limit` | integer | No | Pagination limit |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | array | List of enrollments |

## Validation Rules
- Mandatory fields: None.

## Database Tables
- `sch_student.tb_stud_enrollment` (READ)

## Transaction Scope
Read Only

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found

## Dependencies
Student

## Notes


---
## API Name
Enrollment (Update)

## Module
m_curriculum

## Submodule
sm_enrollment

## Action
enrollment

## ActionType
update

## Purpose
Updates enrollment.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `enrollmentId` | bigint | Yes | Enrollment ID |
| `statusId` | smallint | No | Status ID |
| `isCurrent` | boolean | No | Current flag |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Updated data |

## Validation Rules
- Mandatory fields: `enrollmentId`.
- FK validation: `enrollmentId`.

## Database Tables
- `sch_student.tb_stud_enrollment` (UPDATE)

## Transaction Scope
Cross-schema Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
updated_on

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
Student

## Notes


---
## API Name
Enrollment (Delete)

## Module
m_curriculum

## Submodule
sm_enrollment

## Action
enrollment

## ActionType
delete

## Purpose
Withdraws/cancels the enrollment.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `enrollmentId` | bigint | Yes | Enrollment ID |
| `reason` | string | No | Deletion reason |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `enrollmentId`.
- FK validation: `enrollmentId`.

## Database Tables
- `sch_student.tb_stud_enrollment` (UPDATE)

## Transaction Scope
Cross-schema Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
updated_on

## Possible Error Codes
- Resource Not Found
- Dependency Error

## Dependencies
Student

## Notes


---
## API Name
Semester Registration (Add)

## Module
m_curriculum

## Submodule
sm_enrollment

## Action
semesterRegistration

## ActionType
add

## Purpose
Registers the student for a semester.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `studId` | bigint | Yes | Student ID |
| `crsOfferingIds` | array | Yes | Array of Course Offering IDs |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Created registration IDs |

## Validation Rules
- Mandatory fields: `studId`, `crsOfferingIds`.
- Unique constraint: `uk_stud_crs_registration`.
- FK validation: `studId`.

## Database Tables
- `sch_course_delivery.tb_stud_crs_registration` (WRITE)
- `sch_academic_struct.tb_crs_prerequisite` (READ)

## Transaction Scope
Cross-schema Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
created_on, created_by, updated_on, updated_by

## Possible Error Codes
- Validation Error
- Conflict
- Dependency Error
- Resource Not Found

## Dependencies
Course Delivery, AAA

## Notes


---
## API Name
Semester Registration (View)

## Module
m_curriculum

## Submodule
sm_enrollment

## Action
semesterRegistration

## ActionType
view

## Purpose
Returns a student's semester registration.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `studId` | bigint | No | Student ID |
| `crsOfferingId` | bigint | No | Course Offering ID |
| `page` | integer | No | Pagination page |
| `limit` | integer | No | Pagination limit |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | array | Registration objects |

## Validation Rules
- Mandatory fields: None.

## Database Tables
- `sch_course_delivery.tb_stud_crs_registration` (READ)

## Transaction Scope
Read Only

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found

## Dependencies
Course Delivery

## Notes


---
## API Name
Semester Registration (Update)

## Module
m_curriculum

## Submodule
sm_enrollment

## Action
semesterRegistration

## ActionType
update

## Purpose
Modifies registration.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `registrationId` | bigint | Yes | Registration ID |
| `registrationStatusId` | smallint | Yes | Status ID |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Updated data |

## Validation Rules
- Mandatory fields: `registrationId`, `registrationStatusId`.
- FK validation: `registrationId`.

## Database Tables
- `sch_course_delivery.tb_stud_crs_registration` (UPDATE)

## Transaction Scope
Cross-schema Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
updated_by, updated_on

## Possible Error Codes
- Validation Error
- Resource Not Found

## Dependencies
Course Delivery

## Notes


---
## API Name
Semester Registration (Delete)

## Module
m_curriculum

## Submodule
sm_enrollment

## Action
semesterRegistration

## ActionType
delete

## Purpose
Cancels the semester registration.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `registrationId` | bigint | Yes | Registration ID |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `registrationId`.
- FK validation: `registrationId`.

## Database Tables
- `sch_course_delivery.tb_stud_crs_registration` (DELETE)

## Transaction Scope
Cross-schema Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found
- Dependency Error

## Dependencies
Course Delivery

## Notes


---
## API Name
Elective Registration (Add)

## Module
m_curriculum

## Submodule
sm_enrollment

## Action
electiveRegistration

## ActionType
add

## Purpose
Picks a course for a specific elective slot.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `studId` | bigint | Yes | Student ID |
| `electiveCrsOfferingId` | bigint | Yes | Offering ID for the elective |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Created registration ID |

## Validation Rules
- Mandatory fields: `studId`, `electiveCrsOfferingId`.
- FK validation: `studId`, `electiveCrsOfferingId`.

## Database Tables
- `sch_course_delivery.tb_stud_crs_registration` (WRITE)
- `sch_course_delivery.tb_crs_offering` (READ)

## Transaction Scope
Cross-schema Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
created_by, created_on, updated_by, updated_on

## Possible Error Codes
- Validation Error
- Conflict
- Resource Not Found

## Dependencies
Course Delivery

## Notes


---
## API Name
Elective Registration (View)

## Module
m_curriculum

## Submodule
sm_enrollment

## Action
electiveRegistration

## ActionType
view

## Purpose
Returns a student's elective picks.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `electiveGroupId` | integer | No | Elective Group ID |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | array | Capacity details |

## Validation Rules
- Mandatory fields: None.

## Database Tables
- `sch_course_delivery.tb_crs_offering` (READ)

## Transaction Scope
Read Only

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found

## Dependencies
Course Delivery

## Notes


---
## API Name
Elective Registration (Update)

## Module
m_curriculum

## Submodule
sm_enrollment

## Action
electiveRegistration

## ActionType
update

## Purpose
Changes an elective pick.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `registrationId` | bigint | Yes | Registration ID |
| `newCrsOfferingId` | bigint | Yes | New Offering ID |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `registrationId`, `newCrsOfferingId`.
- FK validation: `registrationId`.

## Database Tables
- `sch_course_delivery.tb_stud_crs_registration` (UPDATE)

## Transaction Scope
Cross-schema Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
updated_by, updated_on

## Possible Error Codes
- Validation Error
- Conflict
- Resource Not Found

## Dependencies
Course Delivery

## Notes


---
## API Name
Elective Registration (Delete)

## Module
m_curriculum

## Submodule
sm_enrollment

## Action
electiveRegistration

## ActionType
delete

## Purpose
Withdraws the elective pick.

## Request Payload
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `registrationId` | bigint | Yes | Registration ID |

## Response Payload
| Field | Type | Description |
| --- | --- | --- |
| `status` | string | API status |
| `message` | string | Human readable message |
| `data` | object | Empty |

## Validation Rules
- Mandatory fields: `registrationId`.
- FK validation: `registrationId`.

## Database Tables
- `sch_course_delivery.tb_stud_crs_registration` (DELETE)

## Transaction Scope
Cross-schema Transaction

## Permissions
[To be defined by AAA Permission Matrix]

## Audit Requirements
None

## Possible Error Codes
- Resource Not Found
- Dependency Error

## Dependencies
Course Delivery

## Notes


---
# Matrices

## API Coverage Matrix
| Submodule | Action | Add | View | Update | Delete |
| --- | --- | --- | --- | --- | --- |
| sm_course | courseDefinition | Yes | Yes | Yes | Yes |
| sm_course | courseOutcome | Yes | Yes | Yes | Yes |
| sm_course | courseRequisite | Yes | Yes | Yes | Yes |
| sm_curriculum | curriculumApproval | Yes | Yes | Yes | Yes |
| sm_curriculum | curriculumManagement | Yes | Yes | Yes | Yes |
| sm_enrollment | electiveRegistration | Yes | Yes | Yes | Yes |
| sm_enrollment | enrollment | Yes | Yes | Yes | Yes |
| sm_enrollment | semesterRegistration | Yes | Yes | Yes | Yes |
| sm_programme | programme | Yes | Yes | Yes | Yes |
| sm_programme | programmeApproval | Yes | Yes | Yes | Yes |

## Table Access Matrix
| Table | Read | Write | Update | Delete |
| --- | --- | --- | --- | --- |
| `sch_academic_struct.tb_prog` | Yes | Yes | Yes | Yes |
| `sch_academic_struct.tb_crs` | Yes | Yes | Yes | Yes |
| `sch_academic_struct.tb_crs_version` | Yes | Yes | Yes | No |
| `sch_academic_struct.tb_crs_prerequisite` | Yes | Yes | Yes | Yes |
| `sch_academic_struct.tb_crs_corequisite` | Yes | Yes | Yes | Yes |
| `sch_academic_struct.tb_curr` | Yes | Yes | Yes | Yes |
| `sch_academic_struct.tb_curr_version` | Yes | Yes | Yes | Yes |
| `sch_student.tb_stud_enrollment` | Yes | Yes | Yes | Yes |
| `sch_course_delivery.tb_stud_crs_registration` | Yes | Yes | Yes | Yes |

## Permission Matrix
| API | Permission |
| --- | --- |
| programme (add) | [To be defined by AAA Permission Matrix] |
| programme (view) | [To be defined by AAA Permission Matrix] |
| programme (update) | [To be defined by AAA Permission Matrix] |
| programme (delete) | [To be defined by AAA Permission Matrix] |
| programmeApproval (add) | [To be defined by AAA Permission Matrix] |
| programmeApproval (view) | [To be defined by AAA Permission Matrix] |
| programmeApproval (update) | [To be defined by AAA Permission Matrix] |
| programmeApproval (delete) | [To be defined by AAA Permission Matrix] |
| courseDefinition (add) | [To be defined by AAA Permission Matrix] |
| courseDefinition (view) | [To be defined by AAA Permission Matrix] |
| courseDefinition (update) | [To be defined by AAA Permission Matrix] |
| courseDefinition (delete) | [To be defined by AAA Permission Matrix] |
| courseOutcome (add) | [To be defined by AAA Permission Matrix] |
| courseOutcome (view) | [To be defined by AAA Permission Matrix] |
| courseOutcome (update) | [To be defined by AAA Permission Matrix] |
| courseOutcome (delete) | [To be defined by AAA Permission Matrix] |
| courseRequisite (add) | [To be defined by AAA Permission Matrix] |
| courseRequisite (view) | [To be defined by AAA Permission Matrix] |
| courseRequisite (update) | [To be defined by AAA Permission Matrix] |
| courseRequisite (delete) | [To be defined by AAA Permission Matrix] |
| curriculumManagement (add) | [To be defined by AAA Permission Matrix] |
| curriculumManagement (view) | [To be defined by AAA Permission Matrix] |
| curriculumManagement (update) | [To be defined by AAA Permission Matrix] |
| curriculumManagement (delete) | [To be defined by AAA Permission Matrix] |
| curriculumApproval (add) | [To be defined by AAA Permission Matrix] |
| curriculumApproval (view) | [To be defined by AAA Permission Matrix] |
| curriculumApproval (update) | [To be defined by AAA Permission Matrix] |
| curriculumApproval (delete) | [To be defined by AAA Permission Matrix] |
| enrollment (add) | [To be defined by AAA Permission Matrix] |
| enrollment (view) | [To be defined by AAA Permission Matrix] |
| enrollment (update) | [To be defined by AAA Permission Matrix] |
| enrollment (delete) | [To be defined by AAA Permission Matrix] |
| semesterRegistration (add) | [To be defined by AAA Permission Matrix] |
| semesterRegistration (view) | [To be defined by AAA Permission Matrix] |
| semesterRegistration (update) | [To be defined by AAA Permission Matrix] |
| semesterRegistration (delete) | [To be defined by AAA Permission Matrix] |
| electiveRegistration (add) | [To be defined by AAA Permission Matrix] |
| electiveRegistration (view) | [To be defined by AAA Permission Matrix] |
| electiveRegistration (update) | [To be defined by AAA Permission Matrix] |
| electiveRegistration (delete) | [To be defined by AAA Permission Matrix] |

## Cross Module Dependency Matrix
| API | Module | Dependency Type |
| --- | --- | --- |
| programme | Organization, Lookup | Shared Table / FK |
| programmeApproval | Lookup | Shared Table / FK |
| programmeApproval | Lookup | Shared Table / FK |
| programmeApproval | Lookup | Shared Table / FK |
| courseDefinition | Lookup | Shared Table / FK |
| curriculumApproval | Lookup | Shared Table / FK |
| curriculumApproval | Lookup | Shared Table / FK |
| curriculumApproval | Lookup | Shared Table / FK |
| enrollment | Student, Lookup | Shared Table / FK |
| enrollment | Student | Shared Table / FK |
| enrollment | Student | Shared Table / FK |
| enrollment | Student | Shared Table / FK |
| semesterRegistration | Course Delivery, AAA | Shared Table / FK |
| semesterRegistration | Course Delivery | Shared Table / FK |
| semesterRegistration | Course Delivery | Shared Table / FK |
| semesterRegistration | Course Delivery | Shared Table / FK |
| electiveRegistration | Course Delivery | Shared Table / FK |
| electiveRegistration | Course Delivery | Shared Table / FK |
| electiveRegistration | Course Delivery | Shared Table / FK |
| electiveRegistration | Course Delivery | Shared Table / FK |

## Transaction Matrix
| API | Transaction Type | Tables Involved |
| --- | --- | --- |
| programme (add) | Single-table Transaction | sch_academic_struct.tb_prog, sch_lookup.tb_lookup, sch_org.tb_inst, sch_org.tb_dept |
| programme (view) | Read Only | sch_academic_struct.tb_prog |
| programme (update) | Single-table Transaction | sch_academic_struct.tb_prog |
| programme (delete) | Single-table Transaction | sch_academic_struct.tb_prog |
| programmeApproval (add) | Single-table Transaction | sch_academic_struct.tb_prog |
| programmeApproval (view) | Read Only | sch_academic_struct.tb_prog |
| programmeApproval (update) | Single-table Transaction | sch_academic_struct.tb_prog |
| programmeApproval (delete) | Single-table Transaction | sch_academic_struct.tb_prog |
| courseDefinition (add) | Multi-table Transaction | sch_academic_struct.tb_crs, sch_academic_struct.tb_crs_version |
| courseDefinition (view) | Read Only | sch_academic_struct.tb_crs, sch_academic_struct.tb_crs_version |
| courseDefinition (update) | Multi-table Transaction | sch_academic_struct.tb_crs, sch_academic_struct.tb_crs_version |
| courseDefinition (delete) | Single-table Transaction | sch_academic_struct.tb_crs |
| courseRequisite (add) | Single-table Transaction | sch_academic_struct.tb_crs_prerequisite, sch_academic_struct.tb_crs_corequisite |
| courseRequisite (view) | Read Only | sch_academic_struct.tb_crs_prerequisite, sch_academic_struct.tb_crs_corequisite |
| courseRequisite (update) | Multi-table Transaction | sch_academic_struct.tb_crs_prerequisite, sch_academic_struct.tb_crs_corequisite |
| courseRequisite (delete) | Single-table Transaction | sch_academic_struct.tb_crs_prerequisite, sch_academic_struct.tb_crs_corequisite |
| curriculumManagement (add) | Multi-table Transaction | sch_academic_struct.tb_curr, sch_academic_struct.tb_curr_version, sch_academic_struct.tb_curr_term, sch_academic_struct.tb_curr_term_crs |
| curriculumManagement (view) | Read Only | sch_academic_struct.tb_curr, sch_academic_struct.tb_curr_version, sch_academic_struct.tb_curr_term, sch_academic_struct.tb_curr_term_crs |
| curriculumManagement (update) | Multi-table Transaction | sch_academic_struct.tb_curr, sch_academic_struct.tb_curr_version, sch_academic_struct.tb_curr_term, sch_academic_struct.tb_curr_term_crs |
| curriculumManagement (delete) | Single-table Transaction | sch_academic_struct.tb_curr |
| curriculumApproval (add) | Single-table Transaction | sch_academic_struct.tb_curr_version |
| curriculumApproval (view) | Read Only | sch_academic_struct.tb_curr_version |
| curriculumApproval (update) | Single-table Transaction | sch_academic_struct.tb_curr_version |
| curriculumApproval (delete) | Single-table Transaction | sch_academic_struct.tb_curr_version |
| enrollment (add) | Cross-schema Transaction | sch_student.tb_stud_enrollment |
| enrollment (view) | Read Only | sch_student.tb_stud_enrollment |
| enrollment (update) | Cross-schema Transaction | sch_student.tb_stud_enrollment |
| enrollment (delete) | Cross-schema Transaction | sch_student.tb_stud_enrollment |
| semesterRegistration (add) | Cross-schema Transaction | sch_course_delivery.tb_stud_crs_registration, sch_academic_struct.tb_crs_prerequisite |
| semesterRegistration (view) | Read Only | sch_course_delivery.tb_stud_crs_registration |
| semesterRegistration (update) | Cross-schema Transaction | sch_course_delivery.tb_stud_crs_registration |
| semesterRegistration (delete) | Cross-schema Transaction | sch_course_delivery.tb_stud_crs_registration |
| electiveRegistration (add) | Cross-schema Transaction | sch_course_delivery.tb_stud_crs_registration, sch_course_delivery.tb_crs_offering |
| electiveRegistration (view) | Read Only | sch_course_delivery.tb_crs_offering |
| electiveRegistration (update) | Cross-schema Transaction | sch_course_delivery.tb_stud_crs_registration |
| electiveRegistration (delete) | Cross-schema Transaction | sch_course_delivery.tb_stud_crs_registration |