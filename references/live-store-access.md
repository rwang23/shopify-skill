# Live store access setup

Use this guide when user asks to run GraphQL and fetch real store data.

## 1) Where to store credentials

Do NOT store secrets under the skill folder.
Use project-root `.env` (gitignored) or user environment variables.

Project `.env` example:

```dotenv
SHOPIFY_SHOP=your-store.myshopify.com
SHOPIFY_ADMIN_TOKEN=shpat_xxx
SHOPIFY_API_VERSION=2026-01
```

Compatible key aliases:
- `SHOPIFY_STORE_URL` (same as `SHOPIFY_SHOP`)
- `SHOPIFY_ACCESS_TOKEN` (same as `SHOPIFY_ADMIN_TOKEN`)

## 2) Execute query

```bash
python scripts/admin_graphql_query.py --query "query { shop { name myshopifyDomain } }"
```

With variables:

```bash
python scripts/admin_graphql_query.py --query "query Products($first:Int!){ products(first:$first){ nodes { id title } } }" --variables "{\"first\":5}"
```

## 3) Common failure handling

- `Missing credentials`: create/update project `.env`
- `HTTP 401`: invalid token
- `HTTP 403`: missing scope
- `HTTP 404`: wrong store domain or API version
- `GraphQL errors`: invalid field, wrong input type, or unsupported version