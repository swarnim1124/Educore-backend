# Lookup Migration Strategy (V004)

The transition from the legacy `sch_lookup.tb_lookup` to the new `sch_core.tb_reference_data` framework will be executed in five measurable phases to prevent a flag-day catastrophe.

## Phase 1: Legacy Lookup Active
- Current State. `tb_lookup` is fully active and serves all application needs.

## Phase 2: Dual Read
- The `LookupProvider` is introduced. It attempts to read from the new framework, falling back to legacy `tb_lookup` if the category does not exist in the new structure.

## Phase 3: Dual Write (If Required)
- As modules migrate, new lookups may need to be written to both systems temporarily if legacy services still depend on them.

## Phase 4: Reference Framework Only
- All OneApp modules use the `LookupProvider`. 
- Existing Foreign Keys in business tables are migrated to reference `tb_reference_data(id)`.
- Legacy `tb_lookup` queries in application code are completely removed.

## Phase 5: Legacy Lookup Removed
- A destructive SQL migration formally drops `sch_lookup.tb_lookup` and `sch_lookup.tb_lookup_cat`.
