# Changelog (Detailed)

## 1.0.0 - 2026-03-03

### Added
- Unified CLI: `query`, `capabilities`, `scan-stock`, `randomize-stock`, `rollback-stock`, `report-sales`.
- Structured audit outputs with deterministic naming under `shopify-skill-output/`.
- Safety controls for writes: `--apply`, `--max-changes`, rollback plan generation.
- File-based query inputs: `--query-file`, `--variables-file`.
- Initial unittest coverage.

### Changed
- Default execution mode is read-only.
- Added retry/backoff and error classification.

### Notes
- Customer PII access depends on Shopify plan and app approval.