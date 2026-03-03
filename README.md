# Shopify Skill

Shopify Dev MCP + Admin GraphQL skill with auditable execution, safety guardrails, and reusable store analytics workflows.

Shopify Dev MCP + Admin GraphQL 技能，提供可审计执行、安全写入防护、以及可复用的数据分析流程。

## Features / 功能

- Official-doc-first workflow (Dev MCP)
  - 先查官方文档再执行（Dev MCP）
- Unified CLI commands for query, stock ops, rollback, and reporting
  - 统一 CLI：查询、库存操作、回滚、报表
- Read-only by default, write requires explicit `--apply`
  - 默认只读，写操作必须显式 `--apply`
- `--max-changes` guardrail for mass update prevention
  - `--max-changes` 限制单次最大变更量
- Structured audit outputs for every run
  - 每次运行自动输出结构化审计文件

## Repository Layout / 仓库结构

- `SKILL.md` - skill behavior and trigger instructions
- `scripts/admin_graphql_query.py` - unified CLI entry
- `references/` - MCP and GraphQL guidance
- `tests/` - basic unittest suite
- `INSTALL.md` - setup guide
- `USAGE.md` - command examples and operational flow

## Installation / 安装

See [INSTALL.md](./INSTALL.md).

核心步骤：
1. 放置目录到 `~/.codex/skills/shopify-skill`
2. 在 `~/.codex/config.toml` 配置 `shopify-dev-mcp`
3. 在项目根目录创建 `.env`：

```dotenv
SHOPIFY_SHOP=your-store.myshopify.com
SHOPIFY_ADMIN_TOKEN=shpat_xxx
SHOPIFY_API_VERSION=2026-01
```

## Quick Start / 快速开始

```bash
python scripts/admin_graphql_query.py capabilities
python scripts/admin_graphql_query.py query --query "{ shop { name myshopifyDomain } }"
python scripts/admin_graphql_query.py scan-stock --threshold 50 --exclude-product "Shipment Protection+"
python scripts/admin_graphql_query.py report-sales --page-size 100 --max-pages 10
```

## Safe Write Workflow / 安全写入流程

1. Dry-run preview / 先预览：

```bash
python scripts/admin_graphql_query.py randomize-stock --threshold 50 --target-min 20 --target-max 35 --exclude-product "Shipment Protection+"
```

2. Apply with guardrail / 带保护执行：

```bash
python scripts/admin_graphql_query.py randomize-stock --threshold 50 --target-min 20 --target-max 35 --exclude-product "Shipment Protection+" --apply --max-changes 20
```

3. Rollback if needed / 需要时回滚：

```bash
python scripts/admin_graphql_query.py rollback-stock --rollback-file shopify-skill-output/<date>/<run>/rollback-plan.json --apply --max-changes 20
```

## Audit Outputs / 审计输出

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

More details: [references/audit-output-convention.md](./references/audit-output-convention.md)

## Testing / 测试

```bash
python -m unittest discover tests -v
```

## Releases / 发布

- Changelog: [CHANGELOG.md](./CHANGELOG.md)
- Release template: [.github/release-template.md](./.github/release-template.md)
- v1.0.0 notes: [RELEASE_NOTES_v1.0.0.md](./RELEASE_NOTES_v1.0.0.md)

## License / 许可

MIT. See [LICENSE](./LICENSE).