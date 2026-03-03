# Shopify Skill 中文文档

英文主文档请查看 [README.md](./README.md)。

## 概述

`shopify-skill` 是一个 Shopify Dev MCP + Admin GraphQL 技能仓库，支持：
- 可审计执行
- 安全写入防护（默认只读）
- 库存与销售分析流程

## 兼容范围

- Agent：Codex、Claude、Antigravity、OpenClaw（以及任何可执行本地脚本的代理运行时）
- 系统：Windows / macOS / Linux
- 设备：本地电脑、远程服务器、CI Runner

## 快速安装

1. 准备 Python 3.10+ 与 Node.js  
2. 在你的代理工具中配置 MCP 命令：

```toml
command = "npx"
args = ["-y", "@shopify/dev-mcp@latest"]
```

3. 在项目根目录创建 `.env`：

```dotenv
SHOPIFY_SHOP=your-store.myshopify.com
SHOPIFY_ADMIN_TOKEN=shpat_xxx
SHOPIFY_API_VERSION=2026-01
```

## 常用命令

只读：

```bash
python scripts/admin_graphql_query.py capabilities
python scripts/admin_graphql_query.py query --query "{ shop { name } }"
python scripts/admin_graphql_query.py scan-stock --threshold 50 --exclude-product "Shipment Protection+"
python scripts/admin_graphql_query.py report-sales
```

写入（安全流程）：

```bash
# 先 dry-run
python scripts/admin_graphql_query.py randomize-stock --threshold 50 --target-min 20 --target-max 35 --exclude-product "Shipment Protection+"

# 再 apply
python scripts/admin_graphql_query.py randomize-stock --threshold 50 --target-min 20 --target-max 35 --exclude-product "Shipment Protection+" --apply --max-changes 20
```

回滚：

```bash
python scripts/admin_graphql_query.py rollback-stock --rollback-file shopify-skill-output/<date>/<run>/rollback-plan.json --apply --max-changes 20
```

## 审计输出

输出目录规范：

`shopify-skill-output/<YYYYMMDD>/<HHMMSS>-<operation>-<runid>/`

固定文件：
- `summary.json`
- `request.json`
- `result.json`

写操作附加文件：
- `applied.csv`
- `failed.csv`
- `rollback-plan.json`

详细规范见 [references/audit-output-convention.md](./references/audit-output-convention.md)。
