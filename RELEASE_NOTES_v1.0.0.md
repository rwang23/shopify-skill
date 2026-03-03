# Release Notes - v1.0.0 (2026-03-03)

## Summary
First stable release of `shopify-skill` with auditable operations and safe write controls.

`shopify-skill` 首个稳定版本，重点是“可审计 + 可安全写入”。

## What's New

- Unified CLI entry:
  - `query`
  - `capabilities`
  - `scan-stock`
  - `randomize-stock`
  - `rollback-stock`
  - `report-sales`

- Safety controls:
  - read-only by default
  - write requires `--apply`
  - `--max-changes` guardrail
  - rollback plan auto-generation

- Audit outputs (standardized):
  - `summary.json`
  - `request.json`
  - `result.json`
  - `applied.csv` / `failed.csv` / `rollback-plan.json` (write ops)

- Better usability:
  - `--query-file`
  - `--variables-file`

- Documentation:
  - `README.md` (bilingual)
  - `INSTALL.md`
  - `USAGE.md`
  - `references/audit-output-convention.md`

- Tests:
  - initial unittest coverage for helper behaviors

## Breaking Changes

- Default behavior changed to read-only; write commands now require explicit `--apply`.

## Validation

- `python scripts/admin_graphql_query.py --help`
- `python -m unittest discover tests -v`
- `quick_validate.py` passed

## Notes

- Customer PII access is constrained by Shopify plan and app approvals.