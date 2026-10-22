# OneApp Module Capability Matrix - `m_AAA`

This matrix is the authoritative inventory of every capability implemented within the `m_AAA` module.

## Capability Inventory

| Submodule | Action | Action Type | Description | Implementation Status | Validation Status | Runtime Status | Production Readiness | Dependencies | Notes |
|-----------|--------|------------|-------------|----------------------|------------------|----------------|----------------------|--------------|------|
| `sm_auth` | `session` | `add` | Authenticates user credentials and provisions a secure session. | ✅ Implemented | Unit ✓, Integration ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | Employs CapabilityRegistry to seamlessly consume the DefaultPolicyProvider when the DB schema is unprovisioned. |
| `sm_auth` | `session` | `view` | Retrieves current active sessions for the user. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_auth` | `session` | `update` | Refreshes the active session token to extend validity. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_auth` | `session` | `delete` | Logs the user out and invalidates the session payload. | ✅ Implemented | Unit ✓, Integration ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_auth` | `passwordReset` | `add` | Initiates a password reset flow, typically via email link. | ✅ Implemented | Unit ✓, Integration ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_auth` | `passwordReset` | `view` | Validates an incoming password reset token. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_auth` | `passwordReset` | `update` | Executes the password reset and atomically revokes active sessions. | ✅ Implemented | Unit ✓, Integration ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | Revokes active sessions transactionally. |
| `sm_auth` | `passwordReset` | `delete` | Cancels a pending password reset request. | ✅ Implemented | Unit ✓, Integration ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | Revokes token via `TbPasswordReset`. |
| `sm_auth` | `password` | `add` | Sets an initial password for a newly provisioned user. | ✅ Implemented | Unit ✓, Integration ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | Uses `TbUserPasswordState` |
| `sm_auth` | `password` | `view` | Evaluates prospective password strength against enterprise policies. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | Structured strength assessment. |
| `sm_auth` | `password` | `update` | Changes the password for an authenticated session. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | Validates dynamically against the CapabilityRegistry active policy. |
| `sm_auth` | `password` | `delete` | Forces an immediate password expiration. | ✅ Implemented | Unit ✓, Integration ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | Marks `is_expired` in `TbUserPasswordState` and revokes sessions. |
| `sm_auth` | `mfa` | `add` | Enrolls a new Multi-Factor Authentication method. | 🟨 Partially Implemented | Unit ✓ | ⚠ Placeholder | 🟨 Conditional | DB Schema (MFA tables) | Returns static placeholder response. |
| `sm_auth` | `mfa` | `view` | Retrieves a list of registered MFA methods. | 🟨 Partially Implemented | Unit ✓ | ⚠ Placeholder | 🟨 Conditional | DB Schema (MFA tables) | Returns static placeholder response. |
| `sm_auth` | `mfa` | `update` | Sets or promotes a primary MFA method. | 🟨 Partially Implemented | Unit ✓ | ⚠ Placeholder | 🟨 Conditional | DB Schema (MFA tables) | Returns static placeholder response. |
| `sm_auth` | `mfa` | `delete` | Disables or removes a registered MFA method. | 🟨 Partially Implemented | Unit ✓ | ⚠ Placeholder | 🟨 Conditional | DB Schema (MFA tables) | Returns static placeholder response. |
| `sm_auth` | `user` | `view` | Retrieves the authorized user execution context. | ✅ Implemented | Unit ✓ | ✅ Working | ✅ Ready | None | |
| `sm_rbac` | `role` | `add` | Creates a new RBAC role inside the institution. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_rbac` | `role` | `view` | Retrieves the catalog of available institutional roles. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_rbac` | `role` | `update` | Modifies an existing RBAC role definition. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_rbac` | `role` | `delete` | Deletes a role (blocked if assigned to active users). | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | Database Team (`ON DELETE CASCADE`) | Depends on native constraint migration for full safety. |
| `sm_rbac` | `roleAssignment` | `add` | Assigns an RBAC role to a user within an institution. | ✅ Implemented | Unit ✓, Integration ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_rbac` | `roleAssignment` | `view` | Retrieves a user's assigned RBAC roles. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_rbac` | `roleAssignment` | `update` | Updates an existing role assignment status. | ✅ Implemented | Unit ✓ | ❌ Rejected | ✅ Ready | None | Explicitly returns `UNSUPPORTED_OPERATION` to enforce revoke/re-add pattern. |
| `sm_rbac` | `roleAssignment` | `delete` | Revokes an existing role assignment. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_rbac` | `permission` | `add` | Registers a new granular permission. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_rbac` | `permission` | `view` | Retrieves the granular permission catalog. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_rbac` | `permission` | `update` | Updates a permission description. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_rbac` | `permission` | `delete` | Deletes a granular permission. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_rbac` | `accessibleModules`| `view` | Evaluates modules accessible to the current user token. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | |
| `sm_policy` | `passwordPolicy` | `add` | Initializes a password policy configuration. | ✅ Implemented | Unit ✓, Integration ✓ | ⚠ Environment Dependent | 🟨 Conditional | Database Team (Schema provision) | Succeeds in ORM but errors dynamically without table. |
| `sm_policy` | `passwordPolicy` | `view` | Retrieves the active password policy configuration. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | Uses CapabilityRegistry for policy resolution. |
| `sm_policy` | `passwordPolicy` | `update` | Updates the password policy configuration. | ✅ Implemented | Unit ✓ | ⚠ Environment Dependent | 🟨 Conditional | Database Team (Schema provision) | |
| `sm_policy` | `passwordPolicy` | `delete` | Clears the institution password policy back to system defaults. | ✅ Implemented | Unit ✓ | ⚠ Environment Dependent | 🟨 Conditional | Database Team (Schema provision) | |
| `sm_policy` | `sessionPolicy` | `add` | Initializes a session policy configuration. | ✅ Implemented | Unit ✓ | ⚠ Environment Dependent | 🟨 Conditional | Database Team (Schema provision) | |
| `sm_policy` | `sessionPolicy` | `view` | Retrieves the active session policy configuration. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | Uses CapabilityRegistry for policy resolution. |
| `sm_policy` | `sessionPolicy` | `update` | Updates the session policy configuration. | ✅ Implemented | Unit ✓ | ⚠ Environment Dependent | 🟨 Conditional | Database Team (Schema provision) | |
| `sm_policy` | `sessionPolicy` | `delete` | Clears the institution session policy back to system defaults. | ✅ Implemented | Unit ✓ | ⚠ Environment Dependent | 🟨 Conditional | Database Team (Schema provision) | |
| `sm_policy` | `loginPolicy` | `add` | Initializes a login policy configuration. | ✅ Implemented | Unit ✓ | ⚠ Environment Dependent | 🟨 Conditional | Database Team (Schema provision) | |
| `sm_policy` | `loginPolicy` | `view` | Retrieves the active login policy configuration. | ✅ Implemented | Unit ✓, Runtime ✓ | ✅ Working | ✅ Ready | None | Uses CapabilityRegistry for policy resolution. |
| `sm_policy` | `loginPolicy` | `update` | Updates the login policy configuration. | ✅ Implemented | Unit ✓ | ⚠ Environment Dependent | 🟨 Conditional | Database Team (Schema provision) | |
| `sm_policy` | `loginPolicy` | `delete` | Clears the institution login policy back to system defaults. | ✅ Implemented | Unit ✓ | ⚠ Environment Dependent | 🟨 Conditional | Database Team (Schema provision) | |
