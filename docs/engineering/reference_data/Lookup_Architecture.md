# Lookup Architecture

## Schema Design (sch_core)

### 1. tb_reference_category
Defines the categories of reference data.
- `id` (UUID) - Primary Key
- `module_owner` (VARCHAR) - Which module owns this category
- `category_code` (VARCHAR) - Unique business identifier (e.g., 'AUTH_STATUS')
- `name` (VARCHAR) - Display Name
- `description` (VARCHAR) - Detailed description
- `is_extendable` (BOOLEAN) - Whether tenants can add Custom lookups
- `change_policy` (VARCHAR) - Governance policy (e.g., 'STRICT', 'FLEXIBLE')

### 2. tb_reference_data
Contains the actual lookup values.
- `id` (UUID) - Primary Key (Business tables reference this ID)
- `category_id` (UUID) - Foreign Key to tb_reference_category
- `lookup_code` (VARCHAR) - Unique code within category (e.g., 'ACTIVE')
- `external_code` (VARCHAR) - Code for integrations (e.g., UGC, SAP)
- `display_name` (VARCHAR) - UI Label
- `description` (VARCHAR) - Extended description
- `sort_order` (INT) - UI Ordering
- `is_active` (BOOLEAN) - Soft deletion / Activation
- `is_system` (BOOLEAN) - Cannot be modified by tenants
- `inst_id` (BIGINT) - Null for global platform lookups, assigned for tenant lookups
- `metadata` (JSONB) - Extended configuration
- `effective_from` (TIMESTAMPTZ) - Start of validity
- `effective_to` (TIMESTAMPTZ) - End of validity
- `row_version` (INT) - Version control

### Constraints
- `UNIQUE (category_id, lookup_code, inst_id)`
