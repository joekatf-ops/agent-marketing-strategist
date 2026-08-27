# ChatGPT Setup

Last verified: 2026-08-27

ChatGPT capabilities vary by plan, workspace policy, desktop or web surface, Projects, GPTs, apps, and connectors. Use only the controls visible in the current account.

## Upload mode

1. Create a dedicated Project or GPT for strategist work.
2. Add the universal strategist knowledge bundle.
3. Add the current brand bundle to the project or conversation.
4. Use `PROMPT.md` as the operating instruction.
5. At the start of each task, require the brand readiness check and active-brand confirmation.

Replace the uploaded brand bundle after approved learning is recorded in the durable brand folder.

The reviewed universal bundle is sufficient for normal use. If the current ChatGPT surface exposes
a user-authenticated Notion connected tool, it may optionally follow
`connectors/notion-composio.md` for a read-only method freshness check. Setup is app-, plan-, admin-
and host-dependent: require a successful current-session preflight, otherwise report that freshness
was not checked and keep using the reviewed bundle. A detected change is `review-needed` only and
must not edit or promote the skill automatically.

## Connected mode

If the workspace supports an approved app, connector, plugin, or remote MCP-backed tool:

1. add Firecrawl using the provider's official remote connection and secure authentication;
2. add TrendTrack and Foreplay only when their current official connection method is available;
3. confirm tool discovery with one harmless read-only call;
4. keep a connector status record in the task output.

Codex and ChatGPT desktop capabilities may share host configuration in some supported setups, but never infer tool availability from that fact. The current ChatGPT session must successfully expose and call the tool.

## Learning sync

Chat history and project memory are not authoritative brand memory. Export approved human edits, evidence, decisions, and outputs to the brand folder, then rebuild the bundle. Never learn from unapproved drafts simply because they appear in a conversation.

## Ad analysis: connected-folder mode

Use this mode only when the current ChatGPT surface can read the strategist repository and write the
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
