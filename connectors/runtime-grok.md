# Grok Setup

Last verified: 2026-08-27

Grok product capabilities can differ between consumer, workspace, API, and regional surfaces. This guide does not assume that a Grok chat can install arbitrary MCP servers.

## Portable upload mode

1. Start a dedicated strategist or brand workspace when the surface supports it.
2. Upload the universal strategist knowledge bundle.
3. Upload the current brand bundle.
4. Add the operating instruction from `PROMPT.md`.
5. Require active-brand confirmation, readiness, and evidence labels before generation.
6. Replace the brand bundle after approved learning is written to the durable folder.

The reviewed universal bundle is sufficient for normal use. If the current Grok surface or an
agent host exposes a user-authenticated Notion connected tool, it may optionally follow
`connectors/notion-composio.md` for a read-only method freshness check. Treat setup as
host-dependent, require a successful current-session preflight and keep using the reviewed bundle
when the connection is unavailable or incomplete. A detected change is `review-needed` only and
must not edit or promote the skill automatically.

## Tool-connected mode

Use live Firecrawl, TrendTrack, or Foreplay only if the current Grok surface or an agent host you control exposes a documented connector or tool mechanism. Configure credentials in that host, run a read-only preflight, and tell the model exactly which tools succeeded.

If no such mechanism is exposed, perform research outside Grok, store cited evidence in the brand folder, rebuild the bundle, and upload it. Never ask Grok to behave as though a connector exists when it cannot call it.

## Learning sync

Grok conversation memory is not authoritative. Human-approved revisions must become structured learning events in the brand folder before they influence future work.

## Ad analysis: connected-folder mode

Use this mode only when the current Grok surface or agent host can read the strategist repository
and write the one selected brand folder. Ask `Analyse these ads for <brand>`, then:

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
