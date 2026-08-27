# Claude Setup

Last verified: 2026-08-27

Claude surfaces differ across the web app, desktop app, Projects, and organization plans. Use the capabilities visible in the current account rather than assuming Claude Code configuration applies.

## Upload mode

1. Create a dedicated project for the strategist or current brand.
2. Add the universal strategist knowledge bundle to project knowledge or instructions.
3. Generate and upload the current brand bundle.
4. Put the operating instruction from `PROMPT.md` in the project instructions.
5. Replace the brand bundle whenever the durable brand folder changes.

This is the default portable mode and works without live connectors.

The reviewed universal bundle is sufficient for normal use. If the current Claude surface exposes
a user-authenticated Notion connected tool, it may optionally follow
`connectors/notion-composio.md` for a read-only method freshness check. Setup is surface- and
host-dependent: require a successful current-session preflight, otherwise report that freshness was
not checked and keep using the reviewed bundle. A detected change is `review-needed` only and must
not edit or promote the skill automatically.

## Connector mode

If the Claude surface exposes connectors, integrations, or MCP setup:

1. add Firecrawl using its official OAuth or API-key instructions;
2. add TrendTrack and Foreplay only from provider-approved setup details;
3. complete authentication in Claude's secure flow;
4. start a session by asking Claude to list and preflight the tools.

If arbitrary MCP servers are not available in the current Claude plan or surface, use Claude Code or upload mode. Do not tell the strategist that connectors are active merely because they are configured elsewhere.

## Learning sync

Claude project knowledge is not the system of record. Export approved copy, revisions, decisions, and evidence to the durable brand folder, record learning events there, rebuild the brand bundle, and replace the uploaded version.

## Ad analysis: connected-folder mode

Use this mode only when the current Claude surface can read the strategist repository and write the
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
