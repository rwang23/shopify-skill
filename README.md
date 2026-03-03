# Shopify Skill

Shopify Dev MCP + Admin GraphQL skill with auditable execution, safety guardrails, and reusable store analytics workflows.

For 中文, see [readme_zh.md](./readme_zh.md).

## Table of Contents
- [1. Scope and Compatibility](#1-scope-and-compatibility)
- [2. Features](#2-features)
- [3. Repository Layout](#3-repository-layout)
- [4. Setup Matrix (Agents, OS, Devices)](#4-setup-matrix-agents-os-devices)
- [5. Installation](#5-installation)
- [6. Usage](#6-usage)
- [7. Audit Outputs](#7-audit-outputs)
- [8. Testing](#8-testing)
- [9. Changelog](#9-changelog)
- [10. Release](#10-release)
- [11. License](#11-license)

## 1. Scope and Compatibility

This project is agent-agnostic and OS-agnostic.

- Agents: Codex, Claude, Antigravity, OpenClaw, or any agent runtime that can execute local scripts and read this repository.
- OS: Windows, macOS, Linux.
- Devices: desktop/laptop, remote VM, CI runner.

The execution core is `scripts/admin_graphql_query.py`, so behavior is portable across runtimes.

## 2. Features

- Official-doc-first workflow (Dev MCP first, then execution).
- Unified CLI commands for query, stock operations, rollback, and reporting.
- Read-only by default; write requires explicit `--apply`.
- `--max-changes` guardrail for mass update prevention.
- Structured audit outputs for every run.
- Retry/backoff and error classification.
- File-based inputs: `--query-file`, `--variables-file`.

## 3. Repository Layout

- `SKILL.md` - agent behavior and triggering instructions.
- `scripts/admin_graphql_query.py` - unified CLI entry.
- `references/` - MCP and GraphQL guidance.
- `tests/` - unittest suite.
- `.github/release-template.md` - release drafting template.

## 4. Setup Matrix (Agents, OS, Devices)

### 4.1 Agent runtime configuration

For all agents, use the same MCP server command:

```toml
command = "npx"
args = ["-y", "@shopify/dev-mcp@latest"]
```

Where to place this depends on the runtime:
- Codex: `~/.codex/config.toml`
- Claude: Claude MCP config location in your Claude environment
- Antigravity/OpenClaw: their MCP/tool config location

If a runtime has no MCP support, you can still use this repository in script-only mode via `scripts/admin_graphql_query.py`.

### 4.2 OS command conventions

- Windows PowerShell: `py -3 ...` (or `python ...` if mapped to Python 3)
- macOS/Linux shell: `python3 ...` (or `python ...` if mapped to Python 3)

### 4.3 Device profiles

- Local desktop/laptop: store `.env` in project root.
- Remote VM/server: use environment variables or secret manager injection.
- CI/CD runner: inject `SHOPIFY_SHOP`, `SHOPIFY_ADMIN_TOKEN`, and `SHOPIFY_API_VERSION` from CI secrets.

## 5. Installation

### 5.1 Prerequisites

- Python 3.10+
- Node.js (for Shopify Dev MCP via `npx`)
- Shopify Admin API token

### 5.2 Configure MCP (example: Codex)

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.shopify-dev-mcp]
command = "npx"
args = ["-y", "@shopify/dev-mcp@latest"]
```

### 5.3 Configure project credentials

Create project-root `.env`:

```dotenv
SHOPIFY_SHOP=your-store.myshopify.com
SHOPIFY_ADMIN_TOKEN=shpat_xxx
SHOPIFY_API_VERSION=2026-01
```

Alias keys also supported:
- `SHOPIFY_STORE_URL` -> same as `SHOPIFY_SHOP`
- `SHOPIFY_ACCESS_TOKEN` -> same as `SHOPIFY_ADMIN_TOKEN`

## 6. Usage

### 6.1 Base command by OS

Windows (PowerShell):

```powershell
py -3 scripts/admin_graphql_query.py capabilities
```

macOS / Linux:

```bash
python3 scripts/admin_graphql_query.py capabilities
```

### 6.2 Read-only examples

```bash
python scripts/admin_graphql_query.py query --query "{ shop { name myshopifyDomain } }"
python scripts/admin_graphql_query.py query --query-file query.graphql --variables-file vars.json
python scripts/admin_graphql_query.py scan-stock --threshold 50 --exclude-product "Shipment Protection+"
python scripts/admin_graphql_query.py report-sales --page-size 100 --max-pages 10
python scripts/admin_graphql_query.py capabilities
```

### 6.3 Safe write flow

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
python scripts/admin_graphql_query.py rollback-stock --rollback-file shopify-skill-output/<YYYYMMDD>/<HHMMSS>-randomize-stock-<runid>/rollback-plan.json --apply --max-changes 20
```

## 7. Audit Outputs

Output root:

`shopify-skill-output/<YYYYMMDD>/<HHMMSS>-<operation>-<runid>/`

Mandatory files:
- `summary.json`
- `request.json`
- `result.json`

Write operations also emit:
- `applied.csv`
- `failed.csv`
- `rollback-plan.json`

Detailed convention: [references/audit-output-convention.md](./references/audit-output-convention.md)

## 8. Testing

```bash
python -m unittest discover tests -v
```

## 9. Changelog

### 1.0.0 (2026-03-03)

Added:
- Unified CLI: `query`, `capabilities`, `scan-stock`, `randomize-stock`, `rollback-stock`, `report-sales`
- Auditable output structure
- Safety controls (`--apply`, `--max-changes`, rollback plan)
- File-based inputs (`--query-file`, `--variables-file`)
- Initial unittest coverage

Changed:
- Default behavior is read-only.
- Error handling includes retry/backoff and classification.

Notes:
- Customer PII access can be restricted by Shopify plan/app approval.

## 10. Release

- Release template: [.github/release-template.md](./.github/release-template.md)
- v1.0.0 notes: [RELEASE_NOTES_v1.0.0.md](./RELEASE_NOTES_v1.0.0.md)

## 11. License

MIT. See [LICENSE](./LICENSE).
