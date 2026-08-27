# Gemini Setup

Last verified: 2026-08-26

Official MCP reference: https://geminicli.com/docs/tools/mcp-server/

## Gemini CLI

Open the strategist repository and active brand folder in the same workspace. Use the repository instructions and `SKILL.md` as the agent's operating context.

The repository snapshot is sufficient for normal use. If the current Gemini host exposes a
user-authenticated Notion connected tool, it may optionally follow
`connectors/notion-composio.md` for a read-only method freshness check. Treat setup as
host-dependent, require a successful current-session preflight and use the repository snapshot when
the connection is unavailable or incomplete. A detected change is `review-needed` only and must not
edit or promote the skill automatically.

Gemini CLI supports stdio, SSE, and Streamable HTTP MCP transports. Use Firecrawl's OAuth endpoint
so the API key is not placed in `settings.json`. Streamable HTTP configuration uses `httpUrl` in
`~/.gemini/settings.json` or project `.gemini/settings.json`:

```json
{
  "mcpServers": {
    "firecrawl": {
      "httpUrl": "https://mcp.firecrawl.dev/v2/mcp-oauth",
      "trust": false
    }
  }
}
```

Restart or reload Gemini CLI, then run `/mcp auth firecrawl` to complete the OAuth flow. Keep
confirmation enabled until the connector is understood. Gemini CLI also supports `gemini mcp add`,
`gemini mcp list`, `/mcp`, and `/mcp reload`.

The current Gemini MCP documentation describes environment-variable expansion for the `env` block,
not arbitrary HTTP header values. Do not put a Firecrawl API key or a shell-style variable in the
`headers` object unless Gemini officially documents a secure mechanism for the installed version.

TrendTrack and Foreplay should be added using their provider-approved command or URL, never a guessed value.

## Other Gemini surfaces

When local workspace or arbitrary MCP access is unavailable, upload the universal knowledge bundle and current brand bundle. Use upload mode as the source context and sync approved changes back to the durable brand folder after the session.
