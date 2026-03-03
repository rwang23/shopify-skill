# Changelog
All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [1.0.0] - 2026-03-03
### Added
- Unified CLI with subcommands: `query`, `capabilities`, `scan-stock`, `randomize-stock`, `rollback-stock`, `report-sales`.
- Auditable output structure under `shopify-skill-output/<YYYYMMDD>/<HHMMSS>-<operation>-<runid>/`.
- Safety guardrails for write operations: explicit `--apply`, `--max-changes`, and rollback plan generation.
- File-based inputs support: `--query-file` and `--variables-file`.
- Initial tests (`unittest`) for core helper behavior.
- Documentation set: `README.md`, `INSTALL.md`, `USAGE.md`, audit-output reference.

### Changed
- Default behavior is read-only.
- Error handling now includes retry/backoff and error classification.

### Notes
- Customer PII access may be restricted by Shopify plan and app approval.