# Live store access and command usage

## Credentials

Store secrets in project-root `.env` (do not store in skill folder):

```dotenv
SHOPIFY_SHOP=your-store.myshopify.com
SHOPIFY_ADMIN_TOKEN=shpat_xxx
SHOPIFY_API_VERSION=2026-01
```

Aliases supported:
- `SHOPIFY_STORE_URL` (for `SHOPIFY_SHOP`)
- `SHOPIFY_ACCESS_TOKEN` (for `SHOPIFY_ADMIN_TOKEN`)

## Core commands

```bash
python scripts/admin_graphql_query.py capabilities
python scripts/admin_graphql_query.py query --query "{ shop { name } }"
python scripts/admin_graphql_query.py query --query-file query.graphql --variables-file vars.json
python scripts/admin_graphql_query.py scan-stock --threshold 50 --exclude-product "Shipment Protection+"
python scripts/admin_graphql_query.py randomize-stock --threshold 50 --target-min 20 --target-max 35 --exclude-product "Shipment Protection+"   # dry-run
python scripts/admin_graphql_query.py randomize-stock --threshold 50 --target-min 20 --target-max 35 --exclude-product "Shipment Protection+" --apply --max-changes 20
python scripts/admin_graphql_query.py rollback-stock --rollback-file shopify-skill-output/.../rollback-plan.json   # dry-run
python scripts/admin_graphql_query.py rollback-stock --rollback-file shopify-skill-output/.../rollback-plan.json --apply --max-changes 20
python scripts/admin_graphql_query.py report-sales --page-size 100 --max-pages 10
```

Cross-platform note:
- Windows PowerShell: `py -3 scripts/admin_graphql_query.py ...`
- macOS/Linux: `python3 scripts/admin_graphql_query.py ...`
- If `python` maps to Python 3, `python ...` works on all platforms.

## Safety defaults

- Read-only by default.
- Write operations require `--apply`.
- `--max-changes` prevents accidental mass writes.

## Audit outputs

Every run writes structured files to `shopify-skill-output/`.
See `references/audit-output-convention.md`.
