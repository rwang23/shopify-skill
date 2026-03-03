# Dev MCP tools reference

Primary source: https://shopify.dev/docs/apps/build/devmcp

## Tool map (official)

- `search_docs_chunks`
  - Use for targeted retrieval of relevant doc sections.

- `fetch_full_docs`
  - Use when full page context is needed.

- `learn_shopify_api`
  - Use for concept guidance and integration patterns.

- `introspect_graphql_schema`
  - Use to inspect schema fields, types, inputs, and enum values.

- `validate_graphql_codeblocks`
  - Use to validate GraphQL snippets before returning/executing.

- `validate_component_codeblocks`
  - Use to validate Shopify component code blocks.

- `validate_theme_codeblocks`
  - Use to validate Shopify theme (Liquid) code blocks.

## Recommended sequence

1. `search_docs_chunks`
2. `fetch_full_docs`
3. `introspect_graphql_schema`
4. `validate_graphql_codeblocks`
5. Execute + verify via follow-up query