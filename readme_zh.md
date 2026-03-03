# Shopify Skill 中文文档

英文主文档请查看 [README.md](./README.md)。

## 目录
- [1. 适用范围与兼容性](#1-适用范围与兼容性)
- [2. 核心功能](#2-核心功能)
- [3. 仓库结构](#3-仓库结构)
- [4. MCP 配置（多 Agent）](#4-mcp-配置多-agent)
- [5. 安装](#5-安装)
- [6. 使用](#6-使用)
- [7. 审计输出](#7-审计输出)
- [8. 测试](#8-测试)
- [9. 变更记录](#9-变更记录)
- [10. 发布](#10-发布)
- [11. 许可](#11-许可)

## 1. 适用范围与兼容性

本项目是多 Agent、多系统设计。

- Agent：Codex、Claude、Antigravity、OpenClaw（以及其他可执行本地脚本的运行时）
- 系统：Windows、macOS、Linux
- 设备：本地电脑、远程 VM/服务器、CI Runner

核心执行逻辑在 `scripts/admin_graphql_query.py`，与具体 Agent 实现解耦。

## 2. 核心功能

- 先文档后执行（Dev MCP -> Admin GraphQL）
- 统一 CLI：查询、库存扫描、库存调整、回滚、报表
- 新增常用命令：`top-products`、`inventory-alerts`、`orders-export`
- 默认只读；写入必须显式 `--apply`
- `--max-changes` 防止误批量改动
- 统一审计输出目录和命名
- 重试/退避 + 错误类型分类
- 支持文件输入：`--query-file`、`--variables-file`

## 3. 仓库结构

- `SKILL.md`：技能行为与触发规则
- `scripts/admin_graphql_query.py`：统一 CLI 入口
- `references/`：MCP 与 GraphQL 参考资料
- `documentation/`：维护型文档（MCP 矩阵、详细 changelog、计划文件）
- `tests/`：unittest 测试

## 4. MCP 配置（多 Agent）

完整矩阵见：[documentation/mcp-setup-matrix.md](./documentation/mcp-setup-matrix.md)

快速摘要：
- Codex：`~/.codex/config.toml`
- Claude Code：`<project-root>/.mcp.json`
- Claude Desktop：桌面设置中的 MCP 配置
- Antigravity：MCP 设置页（若支持原始配置则按相同 `mcpServers` 结构）
- OpenClaw：若支持 MCP 则注册；不支持时用脚本模式

统一服务定义：

```toml
command = "npx"
args = ["-y", "@shopify/dev-mcp@latest"]
```

## 5. 安装

### 5.1 前置要求

- Python 3.10+
- Node.js（用于 `npx` 拉起 Shopify Dev MCP）
- Shopify Admin API Token

### 5.2 克隆到对应 Agent 的 skills 目录

不要克隆到随意的项目目录。
请把仓库克隆到你当前使用的 Agent 的 skills/extensions 目录下。

Codex（Windows/macOS/Linux）示例：
```bash
git clone https://github.com/rwang23/shopify-skill.git ~/.codex/skills/shopify-skill
```

Claude（Code/Desktop）：
```bash
git clone https://github.com/rwang23/shopify-skill.git ~/.claude/skills/shopify-skill
```

Antigravity：
```bash
git clone https://github.com/rwang23/shopify-skill.git ~/.gemini/antigravity/skills/shopify-skill
```

OpenClaw：
```bash
git clone https://github.com/rwang23/shopify-skill.git ~/.openclaw/skills/shopify-skill
```

然后进入目录：
```bash
cd ~/.<agent>/skills/shopify-skill
```

备选方式：下载 ZIP 并解压到对应 Agent 的 skills 目录下。

### 5.3 项目凭据

在项目根目录创建 `.env`：

```dotenv
SHOPIFY_SHOP=your-store.myshopify.com
SHOPIFY_ADMIN_TOKEN=shpat_xxx
SHOPIFY_API_VERSION=2026-01
```

兼容别名：
- `SHOPIFY_STORE_URL` 等价于 `SHOPIFY_SHOP`
- `SHOPIFY_ACCESS_TOKEN` 等价于 `SHOPIFY_ADMIN_TOKEN`

## 6. 使用

### 6.1 不同系统命令入口

Windows PowerShell：

```powershell
py -3 scripts/admin_graphql_query.py capabilities
```

macOS/Linux：

```bash
python3 scripts/admin_graphql_query.py capabilities
```

### 6.2 查询与分析命令

```bash
python scripts/admin_graphql_query.py query --query "{ shop { name myshopifyDomain } }"
python scripts/admin_graphql_query.py query --query-file query.graphql --variables-file vars.json
python scripts/admin_graphql_query.py capabilities
python scripts/admin_graphql_query.py report-sales --page-size 100 --max-pages 10
python scripts/admin_graphql_query.py top-products --days 30 --limit 20 --by revenue
python scripts/admin_graphql_query.py orders-export --days 30 --page-size 100 --max-pages 10
```

### 6.3 业务用例模板

使用内置模板库 `references/templates/`：

```bash
python scripts/admin_graphql_query.py query --query-file references/templates/orders_recent.graphql --variables-file references/templates/orders_recent.variables.json
python scripts/admin_graphql_query.py query --query-file references/templates/customers_recent.graphql --variables-file references/templates/customers_recent.variables.json
python scripts/admin_graphql_query.py query --query-file references/templates/blogs_with_articles.graphql --variables-file references/templates/blogs_with_articles.variables.json
python scripts/admin_graphql_query.py query --query-file references/templates/products_performance.graphql --variables-file references/templates/products_performance.variables.json
python scripts/admin_graphql_query.py query --query-file references/templates/sales_shopifyql.graphql --variables-file references/templates/sales_shopifyql.variables.json
python scripts/admin_graphql_query.py query --query-file references/templates/subscription_contracts.graphql --variables-file references/templates/subscription_contracts.variables.json
python scripts/admin_graphql_query.py query --query-file references/templates/app_installation_subscriptions.graphql --variables-file references/templates/app_installation_subscriptions.variables.json
```

完整矩阵（scope + 场景说明）：[references/common-templates.md](./references/common-templates.md)

### 6.4 库存命令

```bash
python scripts/admin_graphql_query.py scan-stock --threshold 50 --exclude-product "Shipment Protection+"
python scripts/admin_graphql_query.py inventory-alerts --low-threshold 10 --high-threshold 50
```

### 6.5 安全写入流程

1. 先 dry-run：

```bash
python scripts/admin_graphql_query.py randomize-stock --threshold 50 --target-min 20 --target-max 35 --exclude-product "Shipment Protection+"
```

2. 再 apply（带保护）：

```bash
python scripts/admin_graphql_query.py randomize-stock --threshold 50 --target-min 20 --target-max 35 --exclude-product "Shipment Protection+" --apply --max-changes 20
```

3. 回滚：

```bash
python scripts/admin_graphql_query.py rollback-stock --rollback-file shopify-skill-output/<YYYYMMDD>/<HHMMSS>-randomize-stock-<runid>/rollback-plan.json --apply --max-changes 20
```

## 7. 审计输出

输出目录：

`shopify-skill-output/<YYYYMMDD>/<HHMMSS>-<operation>-<runid>/`

固定文件：
- `summary.json`
- `request.json`
- `result.json`

写操作附加文件：
- `applied.csv`
- `failed.csv`
- `rollback-plan.json`

详细规范见：[references/audit-output-convention.md](./references/audit-output-convention.md)

## 8. 测试

```bash
python -m unittest discover tests -v
```

## 9. 变更记录

README 保留简版，详细记录在：[documentation/CHANGELOG.md](./documentation/CHANGELOG.md)

### 1.1.0 (2026-03-03)

- 新增订单、客户、博客/文章、产品、销售（ShopifyQL）、订阅的模板包。
- 新增官方来源调查文档：`documentation/use-cases-research-2026-03-03.md`。
- 扩展使用说明，加入可直接复制执行的模板命令。

## 10. 发布

- 发布模板： [.github/release-template.md](./.github/release-template.md)
- v1.0.0 说明： [documentation/RELEASE_NOTES_v1.0.0.md](./documentation/RELEASE_NOTES_v1.0.0.md)

## 11. 许可

MIT，见 [LICENSE](./LICENSE)
