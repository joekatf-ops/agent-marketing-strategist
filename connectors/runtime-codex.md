# Codex Setup

Last verified: 2026-08-26

Official MCP reference: https://developers.openai.com/codex/mcp

## Install the strategist

Place or link this repository in Codex's recognized skills location, then open the active brand folder as part of the workspace. Keep the universal skill separate from the brand folder.

For a runtime that cannot read the full repository, build and upload the universal knowledge bundle plus the current brand bundle.

## Optional Notion governance

The repository snapshot is sufficient for normal use. If the current Codex host exposes a
user-authenticated Notion connected tool, it may run the read-only freshness check in
`connectors/notion-composio.md`. Treat setup as host-dependent, require a successful current-session
preflight and fall back to the repository snapshot when the connection is unavailable or incomplete.
Any detected change is `review-needed`; it must not edit or promote the skill automatically.

## Add remote MCP servers

Codex uses `~/.codex/config.toml` for user configuration and can use `.codex/config.toml` for trusted project configuration. A remote Streamable HTTP server has this shape:

```toml
[mcp_servers.firecrawl]
url = "https://mcp.firecrawl.dev/v2/mcp"
bearer_token_env_var = "FIRECRAWL_API_KEY"
```

For OAuth-capable servers, add the server and run `codex mcp login SERVER_NAME`. For local stdio servers, use `codex mcp add SERVER_NAME --env KEY=VALUE -- COMMAND`.

Use `codex mcp list` and the `/mcp` command to confirm connection and discovered tools. Store secrets in environment variables, not TOML committed to the project.

## Brand session

1. Open the strategist repository and exactly one active brand folder.
2. Ask the skill to run the brand readiness and connector preflight.
3. Confirm the brand identity before research or writing.
4. Save outputs and learning events back to the active brand folder.
