# Reference Data Lifecycle

The lifecycle of a single lookup value inside the OneApp Platform.

## 1. Creation
- Values are inserted via System Seed or Tenant Admin UI.
- `effective_from` is set to `CURRENT_TIMESTAMP`.
- `effective_to` is `NULL` (infinite validity).

## 2. Active Usage
- Values are cached and consumed by the `LookupProvider`.
- Business tables reference the UUID.

## 3. Version Update
- If a display name or metadata changes, `row_version` is incremented.
- External systems relying on data syncing can track changes via `row_version`.

## 4. Deprecation (Soft Delete)
- Lookups are rarely hard-deleted to preserve historical reporting.
- To deprecate: `is_active` is set to `FALSE` OR `effective_to` is populated with a past date.
- The `LookupProvider` ceases returning this value in dropdowns, but `resolve_id()` continues to successfully map historical records.
