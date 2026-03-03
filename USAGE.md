# Usage Guide

## Read-only examples

```bash
python scripts/admin_graphql_query.py query --query "{ products(first: 5) { nodes { id title } } }"
python scripts/admin_graphql_query.py scan-stock --threshold 50 --exclude-product "Shipment Protection+"
python scripts/admin_graphql_query.py report-sales --page-size 100 --max-pages 10
```

## Write flow (safe)

1. Dry-run preview:

```bash
python scripts/admin_graphql_query.py randomize-stock --threshold 50 --target-min 20 --target-max 35 --exclude-product "Shipment Protection+"
```

2. Apply with guardrail:

```bash
python scripts/admin_graphql_query.py randomize-stock --threshold 50 --target-min 20 --target-max 35 --exclude-product "Shipment Protection+" --apply --max-changes 20
```

3. Rollback if needed:

```bash
python scripts/admin_graphql_query.py rollback-stock --rollback-file shopify-skill-output/<date>/<run>/rollback-plan.json --apply --max-changes 20
```

## Output audit files

All runs are saved under:

`shopify-skill-output/<YYYYMMDD>/<HHMMSS>-<operation>-<runid>/`

Core files:
- `summary.json`
- `request.json`
- `result.json`

Write runs add:
- `applied.csv`
- `failed.csv`
- `rollback-plan.json`