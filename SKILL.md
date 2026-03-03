---
name: shopify-skill
description: Shopify Dev MCP and Admin GraphQL implementation skill for writing, validating, debugging, and executing Shopify store queries/mutations. Use when Codex needs Shopify docs lookup, schema introspection, GraphQL operation drafting, scope checks, and live store data access through Admin API credentials.
---

# Shopify Skill

## Overview

Use Dev MCP for discovery/schema checks first, then run Admin GraphQL with explicit credentials. Keep operations scope-aware, version-pinned, and validation-first.

## Workflow

1. Classify request intent.
- `write/debug`: user asks to write or fix GraphQL.
- `execute/read data`: user asks to run query, fetch results, or read live store data.

2. Confirm prerequisites.
- Confirm MCP server is enabled (`shopify-dev-mcp`).
- Confirm target store, token/session, and API version.
- If execution is requested and credentials are missing, follow `references/live-store-access.md`.

3. Research from official docs.
- Use `search_docs_chunks` for focused sections.
- Use `fetch_full_docs` for canonical details.
- Use `learn_shopify_api` for concepts/migration clarifications.

4. Build GraphQL safely.
- Use `introspect_graphql_schema` to verify fields, inputs, enums, deprecations, and payload shape.
- Draft operations with variables.
- Run `validate_graphql_codeblocks` before returning or executing GraphQL.

5. Validate UI/theme code when relevant.
- Use `validate_component_codeblocks` for Shopify component snippets.
- Use `validate_theme_codeblocks` for Liquid/theme snippets.

6. Execute and verify.
- Prefer read query before write mutation.
- Include `userErrors { field message }` for mutation responses.
- For live execution, use `scripts/admin_graphql_query.py`.
- Re-query changed resource to confirm result.

## Live execution trigger phrases

Treat phrases below as execution intent:
- "run it", "execute", "fetch data", "get results", "query my store", "read live data"

When triggered:
1. Verify `.env` in project root has required keys.
2. Run `python scripts/admin_graphql_query.py --query "<graphql>"`.
3. Return concise result summary plus structured response.

## Output contract

Return implementation guidance in this order:
1. Goal (one line)
2. Required scopes
3. Final operation (validated)
4. Verification checks

## References

- MCP tools and decision map: `references/dev-mcp-tools.md`
- Admin GraphQL endpoint and conventions: `references/admin-graphql-patterns.md`
- Ready-to-use common templates: `references/common-templates.md`
- Credentials/setup/execution guide: `references/live-store-access.md`