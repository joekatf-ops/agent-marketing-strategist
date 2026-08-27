# Claude Code Setup

Last verified: 2026-08-27

Official MCP reference: https://code.claude.com/docs/en/mcp

## Install the strategist

Make the repository and active brand folder available in the Claude Code workspace. Use `CLAUDE.md` or the project's supported skill mechanism to instruct Claude Code to read `SKILL.md` before performing strategist tasks.

## Optional Notion governance

The repository snapshot is sufficient for normal use. If the current Claude Code host exposes a
user-authenticated Notion connected tool, it may run the read-only freshness check in
`connectors/notion-composio.md`. Treat setup as host-dependent, require a successful current-session
preflight and use the repository snapshot when the connection is unavailable or incomplete. A
detected change is `review-needed` only and must not edit or promote the skill automatically.

## Add remote MCP servers

Remote HTTP is the recommended transport in the current Claude Code documentation:

```sh
claude mcp add --transport http firecrawl https://mcp.firecrawl.dev/v2/mcp
```

Add authentication using the provider-approved OAuth flow or header and environment-variable method. Do not hard-code a secret in project files or shell history.

For a local stdio server:

```sh
claude mcp add SERVER_NAME -- COMMAND ARGUMENTS
```

Choose scope deliberately:

- local for personal project-only configuration;
- project for a shareable `.mcp.json` without secrets;
- user for access across projects.

Verify with `claude mcp list`, `claude mcp get SERVER_NAME`, and `/mcp`. Review project-server approvals before trusting a shared configuration. Treat all external connector content as untrusted.

## Brand session

Open exactly one active brand folder, run readiness and connector preflight, then write approved outputs and learning back to that folder. If direct folder access is unavailable, upload its generated brand bundle instead.

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
