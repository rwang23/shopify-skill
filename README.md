# Shopify Skill

Shopify Dev MCP + Admin GraphQL skill with auditable execution, safety guardrails, and reusable store analytics workflows.

For Chinese documentation, see [readme_zh.md](./readme_zh.md).

## Table of Contents
- [1. Scope and Compatibility](#1-scope-and-compatibility)
- [2. Features](#2-features)
- [3. Repository Layout](#3-repository-layout)
- [4. Configure MCP (Multi-Agent)](#4-configure-mcp-multi-agent)
- [5. Installation](#5-installation)
- [6. Usage](#6-usage)
- [7. Audit Outputs](#7-audit-outputs)
- [8. Testing](#8-testing)
- [9. Changelog](#9-changelog)
- [10. Release](#10-release)
- [11. License](#11-license)

## 1. Scope and Compatibility

This project is agent-agnostic and OS-agnostic.

- Agents: Codex, Claude, Antigravity, OpenClaw, or any runtime that can execute local scripts.
- OS: Windows, macOS, Linux.
- Devices: desktop/laptop, remote VM/server, CI runner.

Core execution is runtime-independent because it lives in `scripts/admin_graphql_query.py`.

## 2. Features

- Official-doc-first workflow (Dev MCP first, then execution).
- Unified CLI commands for query, stock operations, rollback, and reporting.
- Extra common commands: `top-products`, `inventory-alerts`, `orders-export`.
- Read-only by default; write requires explicit `--apply`.
- `--max-changes` guardrail for mass update prevention.
- Structured audit outputs for every run.
- Retry/backoff and error classification.
- File-based inputs: `--query-file`, `--variables-file`.

## 3. Repository Layout

- `SKILL.md` - skill behavior and triggering instructions.
- `scripts/admin_graphql_query.py` - unified CLI entry.
- `references/` - MCP and GraphQL guidance.
- `documentation/` - maintainable docs (MCP matrix, detailed changelog, planning notes).
- `tests/` - unittest suite.

## 4. Configure MCP (Multi-Agent)

See full matrix: [documentation/mcp-setup-matrix.md](./documentation/mcp-setup-matrix.md)

Quick summary:
- Codex: `~/.codex/config.toml`
- Claude Code: `<project-root>/.mcp.json`
- Claude Desktop: app settings / desktop MCP config
- Antigravity: MCP settings UI (or raw config if supported)
- OpenClaw: MCP settings if available, otherwise script-only mode

Server definition used across all runtimes:

```toml
command = "npx"
args = ["-y", "@shopify/dev-mcp@latest"]
```

## 5. Installation

### 5.1 Prerequisites

- Python 3.10+
- Node.js (for Shopify Dev MCP via `npx`)
- Shopify Admin API token

### 5.2 Clone into your agent's skills directory

Do not clone this repository into an arbitrary project folder.
Clone it into the skills/extensions directory of the runtime (agent) you are currently using.

Codex:
```bash
git clone https://github.com/rwang23/shopify-skill.git ~/.codex/skills/shopify-skill
```

Claude:
```bash
git clone https://github.com/rwang23/shopify-skill.git ~/.claude/skills/shopify-skill
```

Antigravity:
```bash
git clone https://github.com/rwang23/shopify-skill.git ~/.gemini/antigravity/skills/shopify-skill
```

OpenClaw:
```bash
git clone https://github.com/rwang23/shopify-skill.git ~/.openclaw/skills/shopify-skill
```

Then open the cloned folder:
```bash
cd ~/.<agent>/skills/shopify-skill
```

Alternative: download ZIP from GitHub and extract it under the corresponding agent skills folder.

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

macOS/Linux:

```bash
python3 scripts/admin_graphql_query.py capabilities
```

### 6.2 Query and analysis commands

```bash
python scripts/admin_graphql_query.py query --query "{ shop { name myshopifyDomain } }"
python scripts/admin_graphql_query.py query --query-file query.graphql --variables-file vars.json
python scripts/admin_graphql_query.py capabilities
python scripts/admin_graphql_query.py report-sales --page-size 100 --max-pages 10
python scripts/admin_graphql_query.py top-products --days 30 --limit 20 --by revenue
python scripts/admin_graphql_query.py orders-export --days 30 --page-size 100 --max-pages 10
```

### 6.3 Inventory commands

```bash
python scripts/admin_graphql_query.py scan-stock --threshold 50 --exclude-product "Shipment Protection+"
python scripts/admin_graphql_query.py inventory-alerts --low-threshold 10 --high-threshold 50
```

### 6.4 Safe write flow

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

Short changelog summary is kept here. Detailed history is in [documentation/CHANGELOG.md](./documentation/CHANGELOG.md).

### 1.0.0 (2026-03-03)

- Added unified CLI with safety controls and audit outputs.
- Added report and inventory workflows.
- Set default mode to read-only.

## 10. Release

- Release template: [.github/release-template.md](./.github/release-template.md)
- v1.0.0 notes: [documentation/RELEASE_NOTES_v1.0.0.md](./documentation/RELEASE_NOTES_v1.0.0.md)

## 11. License

MIT. See [LICENSE](./LICENSE).
