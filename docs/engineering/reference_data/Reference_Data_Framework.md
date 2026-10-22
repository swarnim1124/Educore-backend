# OneApp Reference Data Framework

The OneApp Reference Data Framework (V004) replaces the legacy generic `tb_lookup` structure with a highly structured, strongly-typed system.

## Objective
To provide a unified, performant, and type-safe reference data platform for all OneApp modules.

## Key Principles
1. **Type Safety:** Business tables reference specific `category_id` values instead of generic lookups.
2. **Immutability of Codes:** `lookup_code` is the business identifier and remains immutable.
3. **Tenant Isolation:** Platform lookups and institution-specific lookups are separated by `inst_id`.
4. **Provider Gateway:** Direct database queries for reference data are prohibited; all access must route through the `LookupProvider`.

## Core Entities
- `sch_core.tb_reference_category`
- `sch_core.tb_reference_data`

See `Lookup_Architecture.md` for schema details.
