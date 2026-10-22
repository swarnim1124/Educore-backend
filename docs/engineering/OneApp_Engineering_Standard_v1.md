# OneApp Engineering Standard v1.0

This document serves as the definitive engineering standard for the OneApp platform, converging both the application architecture and database infrastructure onto a single, scalable, enterprise-grade foundation. 

Neither the legacy database nor the initial application implementations are the sole source of truth. All future modules (Student, Attendance, Fees, Curriculum, Finance, etc.) must be designed against this standard from the outset.

---

## 1. Primary Key Strategy
- **Standard**: Native PostgreSQL `UUID`
- **Implementation**: 
  - DB: `UUID DEFAULT gen_random_uuid() PRIMARY KEY`
  - App: SQLAlchemy `UUID` type. No `VARCHAR` identifiers for surrogate primary keys.
  - **Generation Ownership**:
    - The application may generate UUIDs before persistence (required for offline/mobile/distributed workflows).
    - The database must generate a UUID using `gen_random_uuid()` if one is not supplied.
    - UUIDs remain the canonical identifier throughout the platform.

## 2. Foreign Key Strategy
- **Standard**: DB-Enforced Referential Integrity.
- **Implementation**: 
  - Every foreign key must reference a PRIMARY KEY or UNIQUE constraint.
  - Every foreign key must have an explicitly named constraint.
  - Deletion behaviour must always be intentionally documented.
  - Default behaviour is `ON DELETE RESTRICT`.
  - Use `ON DELETE CASCADE` exclusively for true composition relationships where the child entity cannot logically exist without its parent (e.g., `MFA Method -> Backup Codes`, `Institution -> Institution Policy`). 
  - Audit tables must never cascade.

## 3. Audit Columns
- **Standard**: Standardized tracking of creation, modification, and accountability.
- **Implementation**: 
  - `created_at` (TIMESTAMP WITH TIME ZONE)
  - `created_by` (UUID) -> References `sch_iam.tb_user(id)`
  - `updated_at` (TIMESTAMP WITH TIME ZONE)
  - `updated_by` (UUID) -> References `sch_iam.tb_user(id)`
  - `deleted_at` (TIMESTAMP WITH TIME ZONE)
  - `deleted_by` (UUID) -> References `sch_iam.tb_user(id)`
  - The shared ORM mixins must support these fields. This prevents different teams from implementing incompatible audit models.

## 4. Timestamp Standards
- **Standard**: Time zone-aware timestamps.
- **Implementation**: 
  - DB: `TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP`
  - App: SQLAlchemy `DateTime(timezone=True)`. No String-based timestamp mappings allowed in the ORM.

## 5. JSONB Usage
- **Standard**: `JSONB` for Configuration; Relational tables for Entities.
- **Implementation**: 
  - `JSONB` is appropriate for configuration, provider metadata, IP allow/block lists, authentication configuration, and notification payloads.
  - `JSONB` should **not** replace relational modelling. Entities such as Users, Roles, Permissions, Courses, Attendance, and Fees must remain relational.

## 6. Lookup Strategy
- **Standard**: Normalized Lookup Framework.
- **Implementation**: 
  - The lookup architecture consists of a properly normalized lookup system (e.g., `tb_lookup_category`, `tb_lookup_value`).
  - At minimum every lookup should contain: `id`, `category_code`, `lookup_code`, `display_name`, `description`, `sort_order`, `is_active`, `is_system`, `created_at`.
  - Must include strict foreign keys, unique lookup codes, category enforcement, migration-based seeding, and application caching.

## 7. Multi-tenancy
- **Standard**: Institution Boundary.
- **Implementation**: 
  - `inst_id` must be mandatory for every tenant-scoped table.
  - If a table intentionally omits `inst_id`, it must be explicitly documented as a global/system table with justification.

## 8. Soft Delete Strategy
- **Standard**: Recoverable Deletions.
- **Implementation**: 
  - `is_deleted` (BOOLEAN DEFAULT FALSE)
  - `deleted_at` (TIMESTAMP WITH TIME ZONE)
  - `deleted_by` (UUID) -> References `sch_iam.tb_user(id)`
  - Soft deletion does **not** replace auditing. Every delete operation should continue generating an immutable audit event.

## 9. Naming Standards
- **Standard**: Predictable and Deterministic Naming.
- **Implementation**: 
  - Tables: `tb_<name>`
  - Primary Key: `tb_<name>_pkey` (e.g., `tb_user_pkey`)
  - Foreign Key: `fk_<table_name>_<referenced_table>` (e.g., `fk_tb_user_role_user`)
  - Unique Constraints: `uq_<table_name>_<column>` (e.g., `uq_tb_permission_code`)
  - Views: `vw_<name>`
  - Functions: `fn_<name>`
  - Stored Procedures: `sp_<name>`
  - Triggers: `trg_<name>`
  - Sequences: `seq_<name>`
  - Avoid PostgreSQL-generated anonymous constraint names.

## 10. Constraint Standards
- **Standard**: Database-level Integrity.
- **Implementation**: 
  - Business rules must be enforced at the database level wherever appropriate using `CHECK`, `UNIQUE`, `NOT NULL`, and `FOREIGN KEY` constraints. 
  - The application validates inputs, but the database guarantees integrity.

## 11. Index Standards
- **Standard**: Proactive Indexing.
- **Implementation**: 
  - All foreign keys must be indexed.
  - Every UNIQUE constraint implicitly creates an index and duplicate indexes must not be created.
  - Composite indexes should be designed proactively during schema design rather than reactively after performance issues arise (e.g., `(inst_id)`, `(inst_id, user_id)`, `(inst_id, status_id)`).

## 12. ORM Compatibility
- **Standard**: Faithful Representation.
- **Implementation**: 
  - The SQLAlchemy models must accurately mirror the database schema. No type approximations or String representations of database-native types.

## 13. Migration Strategy
- **Standard**: Strict Migration Lifecycle.
- **Implementation**: 
  - Versioned SQL migrations (Alembic compatibility).
  - Repeatable seed scripts.
  - Forward-only migrations.
  - Migrations should be idempotent wherever practical.
  - Every migration must include rollback instructions unless the migration is intentionally irreversible (and explicitly documented as such).
  - No manual schema edits in production.

## 14. Security Standards
- **Standard**: Defense in Depth.
- **Implementation**: 
  - Row-Level Security (RLS) where applicable.
  - Least privilege via distinct roles: Migration, Application, Read-only, Audit.

## 15. Performance Standards
- **Standard**: Enterprise Scalability.
- **Implementation**: 
  - Avoid `SELECT *`. Always specify explicit column lists.
  - Paginate all collection endpoints by default.
  - Review complex queries using `EXPLAIN ANALYZE` before release.
  - Connection pooling.
  - Statement timeouts.
