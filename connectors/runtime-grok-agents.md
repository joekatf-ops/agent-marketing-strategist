# Grok Agents Setup

Last verified: 2026-08-27

Use this pattern for a Grok-powered agent built through an xAI API or another agent host. The exact tool and knowledge configuration depends on that host, so verify its current documentation before implementation.

## Agent composition

Provide the agent with:

- the universal strategist instruction from `SKILL.md` and `PROMPT.md`;
- retrieval over the current brand bundle or normalized brand-folder content;
- explicit tools for Firecrawl, TrendTrack, and Foreplay only when configured;
- a controlled write path that proposes, validates, and records learning events;
- output validation against the relevant contract before returning work.

Inject one `brand_id` per run. Reject tasks that mix brands or omit the active brand. Namespace retrieval and learning writes by `brand_id`.

## Tool adapter contract

Each connector adapter should expose:

- a capability name and description;
- input and output schemas;
- source URL or external identifier;
- retrieval timestamp;
- authentication outside prompts and stored knowledge;
- typed errors for unavailable, unauthorized, rate-limited, and empty results.

Before research, run a harmless read-only call and pass the resulting availability map to the agent. Do not silently substitute invented data when a tool fails.

## Optional Notion governance

The reviewed repository snapshot or injected universal bundle is sufficient for normal use. If the
agent host exposes a user-authenticated Notion tool, it may optionally implement the read-only
freshness workflow in `connectors/notion-composio.md` through the same adapter contract. Treat this
as host-dependent, require a successful per-run preflight and use the reviewed snapshot when access
is unavailable or incomplete. A detected change is `review-needed` only and must never trigger an
automatic skill edit or method promotion.

## Learning boundary

The agent may draft a proposed learning event, but only an approved human revision or explicit approval can promote it into durable brand memory. Keep raw observations, proposed rules, approved rules, and deprecated rules separate.

## Upload fallback

If the host cannot provide secure tools or retrieval, inject the universal knowledge bundle and current brand bundle into the run. Export approved changes to the real brand folder and rebuild the bundle before the next run.

## Ad analysis: connected-folder mode

Use this mode only when the agent host can read the strategist repository and write the one selected
brand folder. Ask `Analyse these ads for <brand>`, then:

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
