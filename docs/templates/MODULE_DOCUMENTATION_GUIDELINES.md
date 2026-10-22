# OneApp Module Documentation Guidelines

This document is the official engineering documentation standard for OneApp. It establishes the mandatory documentation framework and workflow for every module in the system.

The primary objective of this standard is to ensure that documentation becomes a lightweight maintenance activity, allowing engineering focus to remain on functional completeness and production readiness.

---

## 1. Purpose of Each Artifact

### `01_Module_Capability_Register.md`
**Answers:** *"What exists?"*

**Contains:**
- Capability inventory
- Current implementation state
- Runtime state
- Validation state
- Production readiness
- Dependencies
- Ownership
- Traceability IDs

**Must NEVER contain:**
- Engineering tasks
- Future work
- Root causes
- Design discussions

### `02_Engineering_Backlog.md`
**Answers:** *"What remains?"*

**Contains only incomplete capabilities.** Completed capabilities must be removed.

**Every backlog item must include:**
- Priority
- Category
- Root Cause
- Engineering Tasks (atomic, independently executable tasks)
- Required Tests
- Definition of Done

### `03_Implementation_Log.md`
**Answers:** *"What changed?"*

A chronological engineering journal. Each completed backlog item appends one entry.

**Entries should include:**
- Date
- Capability ID
- Related Backlog ID
- Files Modified
- Summary
- Tests Executed
- Validation Results
- Runtime Results
- Documentation Updated
- Commit Hash (if available)

### `04_Release_Certification.md`
**Answers:** *"Can this module ship?"*

Contains only current release state. Do not duplicate implementation details or backlog information.

**Includes:**
- Executive Summary
- Capability Statistics
- Application Readiness
- Runtime Compatibility
- Infrastructure Dependencies
- Outstanding Blockers
- Certification Status

---

## 2. Standardized Terminology

Consistent status values must be used across all modules.

**Implementation Status**
- Not Implemented
- Placeholder
- Partially Implemented
- Implemented
- Deprecated

**Validation Status**
- Not Tested
- Unit Verified
- Integration Verified
- Runtime Verified
- Fully Verified

**Runtime Status**
- Working
- Working (Fallback)
- Working (Conditional)
- Placeholder
- Disabled
- Broken

**Production Readiness**
- Ready
- Conditional
- Blocked
- Deferred

---

## 3. Capability Identification

Every capability must have a permanent identifier following a standard convention. Future documents should reference IDs instead of repeating long capability names.

**Format:** `[MODULE_CODE]-[CATEGORY]-[SEQUENCE]`

**Examples:**
- `AAA-AUTH-001`
- `ATT-SESSION-004`
- `FEE-PAY-012`

---

## 4. Engineering Workflow

The required lifecycle for every capability is as follows. This is the mandatory engineering workflow for every OneApp module.

1. **New Capability identified**
   ↓
2. **Capability Register updated** (added with 'Not Implemented' / 'Placeholder' statuses)
   ↓
3. **Implementation** (development work executes backlog tasks)
   ↓
4. **Testing** (unit, integration, and runtime validation)
   ↓
5. **Capability marked complete**
   ↓
6. **Backlog updated** (completed item removed entirely from `02_Engineering_Backlog.md`)
   ↓
7. **Implementation Log appended** (new entry added to `03_Implementation_Log.md`)
   ↓
8. **Release Certification regenerated** (statistics and blockers updated in `04_Release_Certification.md`)

---

## Final Engineering Direction

Once this workspace is instantiated from the templates:
- Documentation is considered standardized.
- Documentation should evolve naturally alongside implementation.
- Future engineering effort should prioritize completing placeholders, resolving runtime failures, implementing missing action types, increasing test coverage, and achieving production-ready status.

The primary objective moving forward is **functional completeness and production readiness**, not expanding the documentation system.
