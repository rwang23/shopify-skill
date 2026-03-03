# Admin GraphQL patterns

Sources:
- https://shopify.dev/docs/api/admin-graphql/latest
- https://shopify.dev/docs/api/usage/versioning

## Endpoint and versioning

- Endpoint:
  - `https://{store}.myshopify.com/admin/api/{api_version}/graphql.json`
- Pin explicit dated versions for production integrations.
- Use `latest` docs for discovery, then lock version in implementation.

## Baseline request shape

```bash
curl -X POST "https://{store}.myshopify.com/admin/api/{api_version}/graphql.json" \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Access-Token: {token}" \
  -d '{
    "query": "query Products($first: Int!) { products(first: $first) { nodes { id title handle } } }",
    "variables": { "first": 5 }
  }'
```

## Safety checklist

- Check HTTP status code.
- Check GraphQL top-level `errors`.
- Check mutation-level `userErrors`.
- Verify scopes when fields/mutations fail unexpectedly.