# Common Admin GraphQL templates

Primary source docs:
- https://shopify.dev/docs/api/admin-graphql/latest

## Template library

All templates below are runnable with:

```bash
python scripts/admin_graphql_query.py query --query-file <template.graphql> --variables-file <template.variables.json>
```

## Scenario matrix

| Scenario | Template | Typical scope(s) | Notes |
|---|---|---|---|
| Orders feed and status monitoring | `references/templates/orders_recent.graphql` | `read_orders` | Includes customer identity fields, requires protected customer data level. |
| Customer activity segmentation | `references/templates/customers_recent.graphql` | `read_customers` | Includes email and spend fields, requires protected customer data level. |
| Blog and article editorial operations | `references/templates/blogs_with_articles.graphql` | `read_content` | Supports blog/article publishing workflow checks. |
| Product catalog and inventory visibility | `references/templates/products_performance.graphql` | `read_products` | Good for SKU-level merchandising snapshots. |
| Sales trend analytics (ShopifyQL) | `references/templates/sales_shopifyql.graphql` | `read_reports` | Requires ShopifyQL support and reports access. |
| Subscription commerce lifecycle | `references/templates/subscription_contracts.graphql` | `read_own_subscription_contracts` or related subscription scopes | For subscription contracts and next billing ops. |
| App billing subscription status | `references/templates/app_installation_subscriptions.graphql` | app billing scopes (`read_billing`/app context) | For app subscription health and billing visibility. |

## 1) Orders

Docs: https://shopify.dev/docs/api/admin-graphql/latest/queries/orders

```bash
python scripts/admin_graphql_query.py query \
  --query-file references/templates/orders_recent.graphql \
  --variables-file references/templates/orders_recent.variables.json
```

## 2) Customers

Docs: https://shopify.dev/docs/api/admin-graphql/latest/queries/customers

```bash
python scripts/admin_graphql_query.py query \
  --query-file references/templates/customers_recent.graphql \
  --variables-file references/templates/customers_recent.variables.json
```

## 3) Blogs and articles

Docs:
- https://shopify.dev/docs/api/admin-graphql/latest/queries/blogs
- https://shopify.dev/docs/api/admin-graphql/latest/queries/articles

```bash
python scripts/admin_graphql_query.py query \
  --query-file references/templates/blogs_with_articles.graphql \
  --variables-file references/templates/blogs_with_articles.variables.json
```

## 4) Products

Docs: https://shopify.dev/docs/api/admin-graphql/latest/queries/products

```bash
python scripts/admin_graphql_query.py query \
  --query-file references/templates/products_performance.graphql \
  --variables-file references/templates/products_performance.variables.json
```

## 5) Sales analytics (ShopifyQL)

Docs: https://shopify.dev/docs/api/admin-graphql/latest/queries/shopifyqlQuery

```bash
python scripts/admin_graphql_query.py query \
  --query-file references/templates/sales_shopifyql.graphql \
  --variables-file references/templates/sales_shopifyql.variables.json
```

## 6) Subscription contracts

Docs: https://shopify.dev/docs/api/admin-graphql/latest/queries/subscriptionContracts

```bash
python scripts/admin_graphql_query.py query \
  --query-file references/templates/subscription_contracts.graphql \
  --variables-file references/templates/subscription_contracts.variables.json
```

## 7) App installation subscriptions

Docs: https://shopify.dev/docs/api/admin-graphql/latest/objects/AppInstallation

```bash
python scripts/admin_graphql_query.py query \
  --query-file references/templates/app_installation_subscriptions.graphql \
  --variables-file references/templates/app_installation_subscriptions.variables.json
```

## Operational pattern

- Start with read-only template queries.
- Verify data quality in audit outputs.
- Promote stable templates to scheduled jobs or dashboards.
- For write operations, use explicit `--apply` command flows with rollback artifacts.
