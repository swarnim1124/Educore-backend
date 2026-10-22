# OneApp Implementation Log - `m_AAA`

This document maintains a chronological engineering journal of all work executed within the `m_AAA` module.

---

**Date**
2026-07-31

**Capability**
`passwordPolicy`, `sessionPolicy`, `loginPolicy` (Capability Provider Refactor)

**Files Modified**
- `xsc_lib/xsc_lib_app/xsc_liba_capability.py`
- `modules/m_AAA/providers/policy_provider.py`
- `modules/m_AAA/m_AAA_sm_auth.py`
- `scripts/verify_release.py`
- `tests/test_m_AAA.py`

**Summary of Changes**
- Elevated `CapabilityRegistry` to the shared `xsc_lib_app` framework.
- Abstracted database dependency via `PolicyProvider` interface.
- Implemented `DefaultPolicyProvider` to yield enterprise defaults safely without DB schemas.
- Implemented `DatabasePolicyProvider` natively mapping to SQLAlchemy ORM models.
- Updated `verify_release.py` to assert Capability Detection succeeds and cleanly falls back.

**Validation**
- Unit ✓
- Integration ✓
- Runtime ✓

**Notes**
- Capability Matrix generated and updated.
- Engineering Backlog generated.
- Release Certification passed (with DB conditions).

---

**Date**
2026-07-31

**Capability**
`passwordPolicy.view`, `sessionPolicy.view`, `loginPolicy.view`, `password.add`, `password.view`, `password.delete` (Sprint 1)

**Files Modified**
- `modules/m_AAA/m_AAA_sm_policy.py`
- `modules/m_AAA/m_AAA_sm_auth.py`
- `modules/m_AAA/m_AAA_data.py`
- `modules/m_AAA/db_init.py`
- `docs/m_AAA/01_Capability_Matrix.md`
- `docs/m_AAA/02_Engineering_Backlog.md`
- `docs/m_AAA/04_Release_Certification.md`

**Summary of Changes**
- Resolved refactor drift by updating `passwordPolicy_view`, `sessionPolicy_view`, and `loginPolicy_view` to use the dynamically resolved `CapabilityRegistry`.
- Implemented `password.add` with strong hashing (`XSCUtility.generate_hash`) and active policy validation.
- Implemented `password.view` returning a structured strength evaluation based on active `PasswordPolicy`.
- Designed and implemented `TbUserPasswordState` to decouple password expiration from the credential hash, ensuring cryptographic integrity.
- Refactored `session.add` to intercept `PWD_EXPIRED` based on `tb_user_password_state`.

**Validation**
- Unit ✓
- Integration ✓
- Runtime ✓

**Notes**
- Backlog cleared of P0/P1 password capabilities.
- Capability Matrix updated.

---

**Date**
2026-07-31

**Capability**
`passwordReset.delete`, `permission.*` (CRUD), `roleAssignment.update` (Sprint 2)

**Files Modified**
- `modules/m_AAA/m_AAA_data.py`
- `modules/m_AAA/m_AAA_sm_auth.py`
- `modules/m_AAA/m_AAA_sm_rbac.py`
- `docs/m_AAA/01_Capability_Matrix.md`
- `docs/m_AAA/02_Engineering_Backlog.md`
- `docs/m_AAA/04_Release_Certification.md`

**Summary of Changes**
- `passwordReset.delete`: Implemented secure revocation workflow via `revoke_password_reset_token` to atomic invalidation in DB.
- `permission.*`: Fully integrated CRUD operations targeting `sch_rbac.tb_permission` through the `AAADataLayer`. Handlers correctly route and validate structural payloads.
- `roleAssignment.update`: Explicitly architecturally rejected. Method now returns a structured `UNSUPPORTED_OPERATION` error enforcing the revoke/re-add pattern to preserve audit consistency.

**Validation**
- Unit ✓
- Integration ✓
- Runtime ✓

**Notes**
- Sprint 2 Application-level core components are completely mapped out.
- Capability Matrix updated.
