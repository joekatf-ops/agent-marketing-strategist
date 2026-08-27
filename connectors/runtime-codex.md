# Codex Setup

Last verified: 2026-08-27

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

## Ad analysis: connected-folder mode

Use this mode only when the current session can read the strategist repository and write the one
selected brand folder. Ask `Analyse these ads for <brand>`, then:

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

When folder access is unavailable, use upload-only mode.

The exact upload pack is:

1. `PROMPT.md`;
2. `intake.json`;
3. `dist/knowledge-bundle.md`;
4. the selected generated brand bundle;
5. every referenced attachment or source file whose content the runtime must inspect.

URL and table labels do not become uploaded files or prove connector access. Use the same
`creative-audit` or `performance-diagnosis` mode in the intake. Validate against the bundled schema
guidance, return the input audit and governed `creative-audit.md` or `diagnosis.md` content, and
return any proposed persistence files to the canonical folder owner. The runtime cannot claim it
wrote the run folder or controlled records: upload-only output is a patch, not persistence.
