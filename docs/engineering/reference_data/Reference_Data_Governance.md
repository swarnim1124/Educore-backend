# Reference Data Governance

Reference data directly impacts platform stability. Strict governance policies dictate how categories and lookups are managed.

## Ownership
Every `tb_reference_category` must define a `module_owner`. 
- Only the owning module team is permitted to modify the category semantics.
- Example: `m_AAA` owns `AUTH_STATUS`.

## Extensibility (is_extendable)
- **FALSE (System-Closed):** Tenants cannot add custom lookup values. (e.g., `AUTH_STATUS` - the authentication state machine depends strictly on these values).
- **TRUE (Tenant-Open):** Tenants can define their own lookup values to supplement system defaults. (e.g., `LEAVE_REASON`).

## Change Policies
1. **STRICT:** Values cannot be deleted. They can only be expired via `effective_to`.
2. **FLEXIBLE:** Values can be modified or hard-deleted if no foreign key constraints exist.
