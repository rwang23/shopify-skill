---
name: shopify-skill
description: Shopify Dev MCP and Admin GraphQL implementation skill for writing, validating, debugging, and executing Shopify store queries/mutations. Use when the agent needs Shopify docs lookup, schema introspection, GraphQL operation drafting, scope checks, and live store data analysis with auditable outputs.
---

# Shopify Skill

## Overview

Use Dev MCP for discovery/schema checks first, then execute Admin GraphQL via `scripts/admin_graphql_query.py`.

Default mode is read-only.
Any write operation must explicitly pass `--apply`.

## Workflow

1. Classify request intent.
- `write/debug`: draft or fix GraphQL only.
- `read/analyze`: run read-only queries and reports.
- `write/ops`: inventory or state-changing actions.

2. Enforce safety.
- For write commands, require `--apply`.
- Enforce `--max-changes` guardrail.
- Generate rollback plan for write inventory commands.

3. Use official MCP tooling before execution.
- `search_docs_chunks`, `fetch_full_docs`, `learn_shopify_api`
- `introspect_graphql_schema`, `validate_graphql_codeblocks`

4. Execute via CLI subcommands.
- `query`
- `capabilities`
- `scan-stock`
- `randomize-stock`
- `rollback-stock`
- `report-sales`
- `top-products`
- `inventory-alerts`
- `orders-export`
- For business analysis requests, prefer `query --query-file` with reusable templates in `references/templates/`.

5. Persist auditable outputs.
- Always emit `summary.json`, `request.json`, `result.json`.
- Write operations additionally emit `applied.csv`, `failed.csv`, and `rollback-plan.json`.

## Execution triggers

Treat these as execution intent:
- "run it", "execute", "fetch data", "analyze store", "scan stock", "adjust inventory"

For write intent, restate impact and require explicit confirmation in chat before using `--apply`.

## Output contract

Return in this order:
1. Goal
2. Required scopes
3. Command executed
4. Result summary
5. Audit output directory

## References

- MCP tools: `references/dev-mcp-tools.md`
- GraphQL patterns: `references/admin-graphql-patterns.md`
- Templates: `references/common-templates.md`
- Credentials and execution: `references/live-store-access.md`
- Audit naming standard: `references/audit-output-convention.md`
