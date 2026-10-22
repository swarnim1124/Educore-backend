# OneApp Engineering Backlog - `m_AAA`

This document tracks every capability that is not yet fully complete. 

---

## P0 - Critical Fixes

*(All P0 critical fixes have been resolved)*

---

## P1 - Core Authentication

*(Password lifecycle capabilities completed in Sprint 1)*

---

## P2 - Security Features

### `passwordReset.delete`
*(Capability completed in Sprint 2)*

### `mfa.add`, `mfa.view`, `mfa.update`, `mfa.delete`
**Category:** Stub / Placeholder
**Root Cause:** Deferred feature implementation.
**Required Tests:** Unit Tests, Integration Tests, Runtime Validation
**Dependencies:** DB Schema (MFA tables)
**Definition of Done:** Done when users can seamlessly enroll TOTP devices, require TOTP during login, and securely manage their MFA authenticators.

**Engineering Tasks:**
- Implement TOTP secret generation and encrypted storage.
- Generate QR code payloads for authenticator apps.
- Implement verification challenge for primary selection.
- Intercept standard login flow to issue MFA challenge when active.
- Expose CRUD actions for user MFA management.
- Write unit tests.
- Write integration tests.
- Execute runtime validation.
- Update Capability Matrix.
- Update Release Certification.

---

## P3 - Administrative Functionality

### `permission.add`, `permission.view`, `permission.update`, `permission.delete`
*(Capabilities completed in Sprint 2)*

### Policy Persistence (`add`, `update`, `delete`)
**Category:** Environment / Infrastructure Dependency
**Root Cause:** Missing target production DB tables.
**Required Tests:** Production Validation
**Dependencies:** Database Team (Infrastructure)
**Definition of Done:** Done when schemas are provisioned and operations persist natively to the database instead of the fallback provider.

**Engineering Tasks:**
- Track dependency.
- Validate table creation with DB Team.
- Run production integration suite.
- Update Release Certification block status.

### `role.delete`
**Category:** Environment / Infrastructure Dependency
**Root Cause:** Awaits infrastructure constraint migration for structural safety.
**Required Tests:** Production Validation
**Dependencies:** Database Team (Infrastructure)
**Definition of Done:** Done when the DBA applies the migration script ensuring cascade deletion.

**Engineering Tasks:**
- Track dependency.
- Validate `ON DELETE CASCADE` applied to role foreign keys.
- Run production integration suite.
- Update Release Certification block status.

---

## P4 - Enhancements

### `roleAssignment.update`
*(Capability rejected and documented in Sprint 2 to preserve audit trail)*
