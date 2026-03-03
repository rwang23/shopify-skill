# MCP Setup Matrix

This document provides runtime-specific MCP configuration guidance for `shopify-dev-mcp`.

## Shared server definition

All runtimes should use the same server command:

- command: `npx`
- args: `-y @shopify/dev-mcp@latest`

## 1) Codex

Config file:
- `~/.codex/config.toml`
Recommended skills dir:
- `~/.codex/skills`
Clone:
- `git clone https://github.com/rwang23/shopify-skill.git ~/.codex/skills/shopify-skill`

Example:

```toml
[mcp_servers.shopify-dev-mcp]
command = "npx"
args = ["-y", "@shopify/dev-mcp@latest"]
```

## 2) Claude Code (project-scoped)

Config file:
- `<project-root>/.mcp.json`
Recommended skills dir:
- `~/.claude/skills`
Clone:
- `git clone https://github.com/rwang23/shopify-skill.git ~/.claude/skills/shopify-skill`

Example:

```json
{
  "mcpServers": {
    "shopify-dev-mcp": {
      "command": "npx",
      "args": ["-y", "@shopify/dev-mcp@latest"]
    }
  }
}
```

## 3) Claude Desktop

Recommended way:
- Use Claude Desktop settings and edit MCP config from the app.

Common OS paths (may vary by build/channel):
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
Recommended skills dir:
- `~/.claude/skills`
Clone:
- `git clone https://github.com/rwang23/shopify-skill.git ~/.claude/skills/shopify-skill`

Example JSON shape:

```json
{
  "mcpServers": {
    "shopify-dev-mcp": {
      "command": "npx",
      "args": ["-y", "@shopify/dev-mcp@latest"]
    }
  }
}
```

## 4) Antigravity

Use Antigravity MCP/tool settings UI to register a new MCP server with:
- command: `npx`
- args: `-y @shopify/dev-mcp@latest`

If your Antigravity build supports raw config file editing, use the same `mcpServers` JSON shape as above.
Recommended skills dir:
- `~/.gemini/antigravity/skills`
Clone:
- `git clone https://github.com/rwang23/shopify-skill.git ~/.gemini/antigravity/skills/shopify-skill`

## 5) OpenClaw

OpenClaw environments may differ by version and extension model.

Recommended order:
1. Try native MCP server registration in settings (if available) with the same command/args.
2. If MCP registration is unavailable, run this repository in script mode (`scripts/admin_graphql_query.py`) and keep MCP features optional.
Recommended skills dir:
- `~/.openclaw/skills`
Clone:
- `git clone https://github.com/rwang23/shopify-skill.git ~/.openclaw/skills/shopify-skill`

## 6) Device contexts

### Local desktop/laptop
- Keep `.env` in project root.
- Run commands directly in terminal.

### Remote VM / server
- Prefer environment variables or secret manager injection.
- Avoid storing tokens in shell history.

### CI runner
- Inject `SHOPIFY_SHOP`, `SHOPIFY_ADMIN_TOKEN`, `SHOPIFY_API_VERSION` via CI secrets.
- Use read-only commands by default in CI jobs.
