# Platform Baseline v1.0

The database schema and referential integrity state has been formally frozen and captured as the **V003.5 Platform Baseline**.

## Location
All baseline artifacts are stored in `database/baseline/`.

## Contents
- `schema.sql`: Structural DDL.
- `constraints.sql`: Primary keys, foreign keys, and unique constraints.
- `views.sql`, `functions.sql`, `extensions.sql`
- `statistics.md`: Volume and object counts.
- `relationship_inventory.csv`: Full accounting of all 1,151 relationships.
- `ownership_matrix.csv`: Module ownership assignments.

This baseline represents the certified foundation of the OneApp Platform before the introduction of the V004 Reference Data Framework.
