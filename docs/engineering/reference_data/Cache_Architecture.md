# Reference Data Caching Architecture

To minimize database load, all reference data requests route through a multi-tiered cache.

## Cache Versioning
Keys must include a schema version to support seamless invalidation during upgrades.
- Format: `ref:v1:{category_code}:global`
- Tenant Format: `ref:v1:{category_code}:inst:{inst_id}`

## Loading Strategy
1. **Startup Warming:** All global/system lookups are eagerly loaded into Redis upon application startup.
2. **Lazy Loading:** Institution-specific lookups are loaded on first access.

## Time-to-Live (TTL)
- **System/Global Lookups:** 24 Hours
- **Institution Lookups:** 1 Hour

## Invalidation Rules
- Any mutation via the admin interface triggers a targeted eviction (`DEL ref:v1:AUTH_STATUS:inst:101`).
- Schema or core migrations increment the version string (e.g., `v2`), automatically isolating the new cache.
