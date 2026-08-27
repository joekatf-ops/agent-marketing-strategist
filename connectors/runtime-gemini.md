# Gemini Setup

Last verified: 2026-08-27

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

## Ad analysis: connected-folder mode

Use this mode only when the current Gemini surface can read the strategist repository and write the
one selected brand folder. Ask `Analyse these ads for <brand>`, then:

1. Create a run with `scripts/init-ad-analysis-run.py`:

   ```bash
   python3 scripts/init-ad-analysis-run.py /path/to/brand \
     --mode creative-audit \
     --product-id product-code \
     --market AU
   ```

   Use `creative-audit` without adequate performance data and `performance-diagnosis` when the
   supplied performance pack is adequate.
2. Complete the generated `intake.json` and make its referenced files readable.
3. Validate the run and write its deterministic audit:

   ```bash
   python3 scripts/validate-ad-analysis-run.py /path/to/brand \
     /path/to/brand/outputs/ad-analysis/ADR-YYYYMMDD-001 --write-audit
   ```

4. Consume `input-audit.md`, then write the governed `creative-audit.md` or `diagnosis.md` report
   inside the run folder. A Performance Diagnosis uses the Ad Diagnosis contract. End with a
   Persistence Summary; controlled records still require human confirmation and no command performs
   a live Meta mutation.

Do not claim a connector or attachment is available until a read-only preflight succeeds in the
current session.

## Ad analysis: upload-only mode

When folder access is unavailable, attach `PROMPT.md`, `intake.json`,
`dist/knowledge-bundle.md`, the selected brand bundle, and every referenced attachment or source
file. Use the same `creative-audit` or `performance-diagnosis` mode in the intake. Validate against
the bundled schema guidance, return the input audit and governed `creative-audit.md` or
`diagnosis.md` content, and return any proposed persistence files to the canonical folder owner.
The runtime cannot claim it wrote the run folder or controlled records: upload-only output is a
patch, not persistence.
