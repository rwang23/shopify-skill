# Audit output convention

Root directory:
`<project-root>/shopify-skill-output/`

Run directory:
`shopify-skill-output/<YYYYMMDD>/<HHMMSS>-<operation>-<runid>/`

Operations:
- `query`
- `capabilities`
- `scan-stock`
- `randomize-stock`
- `rollback-stock`
- `report-sales`

Mandatory files per run:
- `summary.json`
- `request.json`
- `result.json`

Write operation extra files:
- `applied.csv`
- `failed.csv`
- `rollback-plan.json` (when applicable)

Report operation extra file:
- `report.md`

Naming rules:
- lower-case kebab-case only
- UTC timestamps only
- no spaces in file/folder names