# Common Admin GraphQL templates

All templates are derived from Shopify Admin GraphQL latest docs:
https://shopify.dev/docs/api/admin-graphql/latest

## 1) Products list (query)

Docs: https://shopify.dev/docs/api/admin-graphql/latest/queries/products
Scope: `read_products`

```graphql
query ProductsPage($first: Int!, $after: String) {
  products(first: $first, after: $after) {
    nodes {
      id
      title
      handle
      status
      updatedAt
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

## 2) Product update (mutation)

Docs: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productUpdate
Scope: `write_products`

```graphql
mutation ProductUpdate($product: ProductUpdateInput!) {
  productUpdate(product: $product) {
    product {
      id
      title
      handle
      updatedAt
    }
    userErrors {
      field
      message
    }
  }
}
```

Variables:

```json
{
  "product": {
    "id": "gid://shopify/Product/1234567890",
    "title": "Updated title"
  }
}
```

## 3) Product variants bulk update (mutation)

Docs: https://shopify.dev/docs/api/admin-graphql/latest/mutations/productVariantsBulkUpdate
Scope: `write_products`

```graphql
mutation ProductVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    product {
      id
    }
    productVariants {
      id
      title
      price
      compareAtPrice
    }
    userErrors {
      field
      message
    }
  }
}
```

## 4) Collection create (mutation)

Docs: https://shopify.dev/docs/api/admin-graphql/latest/mutations/collectionCreate
Scope: `write_products`

```graphql
mutation CollectionCreate($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection {
      id
      title
      handle
      updatedAt
    }
    userErrors {
      field
      message
    }
  }
}
```

## 5) Metafields set (mutation)

Docs: https://shopify.dev/docs/api/admin-graphql/latest/mutations/metafieldsSet
Scope: depends on owner type (for product usually `write_products`)

```graphql
mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields {
      id
      key
      namespace
      value
      updatedAt
    }
    userErrors {
      field
      message
      code
    }
  }
}
```

Variables example:

```json
{
  "metafields": [
    {
      "ownerId": "gid://shopify/Product/1234567890",
      "namespace": "custom",
      "key": "subtitle",
      "type": "single_line_text_field",
      "value": "Eco-friendly"
    }
  ]
}
```

## 6) Orders list (query)

Docs: https://shopify.dev/docs/api/admin-graphql/latest/queries/orders
Scope: `read_orders`

```graphql
query OrdersPage($first: Int!, $after: String, $query: String) {
  orders(first: $first, after: $after, query: $query, sortKey: UPDATED_AT, reverse: true) {
    nodes {
      id
      name
      createdAt
      updatedAt
      displayFinancialStatus
      totalPriceSet {
        shopMoney {
          amount
          currencyCode
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

## 7) Customers list (query)

Docs: https://shopify.dev/docs/api/admin-graphql/latest/queries/customers
Scope: `read_customers`

```graphql
query CustomersPage($first: Int!, $after: String, $query: String) {
  customers(first: $first, after: $after, query: $query, sortKey: UPDATED_AT, reverse: true) {
    nodes {
      id
      firstName
      lastName
      email
      updatedAt
      state
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

## 8) Inventory adjust quantities (mutation)

Docs: https://shopify.dev/docs/api/admin-graphql/latest/mutations/inventoryAdjustQuantities
Scope: inventory write scope for app/session

```graphql
mutation InventoryAdjustQuantities($input: InventoryAdjustQuantitiesInput!) {
  inventoryAdjustQuantities(input: $input) {
    userErrors {
      field
      message
    }
    inventoryAdjustmentGroup {
      createdAt
      reason
      referenceDocumentUri
      changes {
        name
        delta
      }
    }
  }
}
```

Notes:
- Keep `referenceDocumentUri` unique per external operation for traceability/idempotency strategy.
- Follow version-specific idempotency requirements in mutation docs.

## Usage pattern

- Start with query template to get IDs.
- Run mutation template with variables.
- Re-run query to verify update.
