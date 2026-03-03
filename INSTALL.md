# Installation Guide

## 1. Prerequisites

- Python 3.10+
- Node.js (for Shopify Dev MCP via `npx`)
- Codex CLI configured

## 2. Install skill folder

Place this folder under:

`C:\Users\<you>\.codex\skills\shopify-skill`

## 3. Configure MCP

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.shopify-dev-mcp]
command = "npx"
args = ["-y", "@shopify/dev-mcp@latest"]
```

## 4. Configure project credentials

Create project-root `.env`:

```dotenv
SHOPIFY_SHOP=your-store.myshopify.com
SHOPIFY_ADMIN_TOKEN=shpat_xxx
SHOPIFY_API_VERSION=2026-01
```

## 5. Verify

```bash
python scripts/admin_graphql_query.py capabilities
python scripts/admin_graphql_query.py query --query "{ shop { name } }"
```