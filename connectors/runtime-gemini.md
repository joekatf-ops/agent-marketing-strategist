# Gemini Setup

Last verified: 2026-08-26

Official MCP reference: https://geminicli.com/docs/tools/mcp-server/

## Gemini CLI

Open the strategist repository and active brand folder in the same workspace. Use the repository instructions and `SKILL.md` as the agent's operating context.

Gemini CLI supports stdio, SSE, and Streamable HTTP MCP transports. Streamable HTTP configuration uses `httpUrl` in `~/.gemini/settings.json` or project `.gemini/settings.json`:

```json
{
  "mcpServers": {
    "firecrawl": {
      "httpUrl": "https://mcp.firecrawl.dev/v2/mcp",
      "headers": {
        "Authorization": "Bearer $FIRECRAWL_API_KEY"
      },
      "trust": false
    }
  }
}
```

Keep confirmation enabled until the connector is understood. Gemini CLI also supports `gemini mcp add`, `gemini mcp list`, `/mcp`, `/mcp auth SERVER_NAME`, and `/mcp reload`. Use environment references for secrets instead of hard-coding them.

TrendTrack and Foreplay should be added using their provider-approved command or URL, never a guessed value.

## Other Gemini surfaces

When local workspace or arbitrary MCP access is unavailable, upload the universal knowledge bundle and current brand bundle. Use upload mode as the source context and sync approved changes back to the durable brand folder after the session.

