# Seeding Strategy

Reference data must be seeded reliably across all environments without mixing business logic.

## Seed Directories
`database/seeds/` is strictly partitioned:
1. `/platform/` - Immutable system reference data.
2. `/institution/` - Tenant-specific baseline data.
3. `/demo/` - Fictional data for sales and presentation environments.
4. `/test/` - Pytest-specific mocks.

## Execution Rules
- Seeds must execute **after** structural migrations.
- Seeds must be fully **idempotent**.

## Example Idempotent SQL
```sql
INSERT INTO sch_core.tb_reference_data (id, category_id, lookup_code, display_name, is_system)
VALUES (gen_random_uuid(), (SELECT id FROM sch_core.tb_reference_category WHERE category_code = 'AUTH_STATUS'), 'ACTIVE', 'Active', TRUE)
ON CONFLICT (category_id, lookup_code, inst_id)
DO UPDATE SET display_name = EXCLUDED.display_name;
```
