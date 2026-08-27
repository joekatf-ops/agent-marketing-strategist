# Runtime portability

The same method and versioned `intake.json` run in two persistence modes across Codex, Claude,
Claude Code, ChatGPT, Gemini, Grok and Grok Agents. Runtime names and saved configuration do not
prove filesystem, attachment or connector access.

## Connected-folder mode

Use this mode only after the current session successfully reads the strategist repository and the
one selected brand folder. When the folder is writable, the runtime may save snapshots, drafts,
evidence, append-only learning events and governed ad-analysis run files. Controlled records still
follow their approval and confirmation rules.

For ad analysis, create a stable run and then fill the generated intake:

```bash
python3 scripts/init-ad-analysis-run.py /path/to/brand \
  --mode creative-audit \
  --product-id product-code \
  --market AU
```

Use `--mode performance-diagnosis` only when the supplied performance pack is adequate. Validate
the completed intake and write its audit:

```bash
python3 scripts/validate-ad-analysis-run.py /path/to/brand \
  /path/to/brand/outputs/ad-analysis/ADR-YYYYMMDD-001 --write-audit
```

Consume `input-audit.md` before conclusions. Write the governed report to
`outputs/ad-analysis/<RUN_ID>/creative-audit.md` or
`outputs/ad-analysis/<RUN_ID>/diagnosis.md` and end with a Persistence Summary. Run-folder writes do
not authorise a test-register, winner-library or approved-revision update and do not perform any
live Meta mutation.

## Upload-only mode

Build the universal and selected-brand bundles:

```bash
python3 scripts/build-knowledge-bundle.py
python3 scripts/build-brand-bundle.py /path/to/brand /path/to/brand-bundle.md
```

For ad analysis in upload-only mode, use the following files.

The exact upload pack is:

1. `PROMPT.md`;
2. `intake.json`;
3. `dist/knowledge-bundle.md`;
4. the selected generated brand bundle;
5. every referenced attachment or source file whose content the runtime must inspect.

URL and table labels do not become uploaded files or prove connector access. An attachment label or
source inventory entry is not proof that content can be opened. Preflight every required input in
the current session and state any limitation. Return the input audit,
governed report and proposed persistence patches to the canonical folder owner. Conversation or
project memory is not persistence, and the runtime must not claim the run folder or controlled
records changed. The upload-only output is a patch, not persistence.

## Optional method-governance check

The reviewed repository snapshot or universal knowledge bundle is sufficient for normal use. A
runtime may optionally run the read-only Notion freshness workflow in
`connectors/notion-composio.md` when its host exposes a user-authenticated connected tool. Do not
assume native Composio or Notion availability from the runtime name or from saved configuration;
require a successful read-only preflight in the current session.

If the connection is unavailable, unauthorised or incomplete, state that freshness was not checked
and continue from the reviewed snapshot. A detected Notion change is `review-needed` only and must
never automatically edit or promote the skill.

## First-class setup guides

- `connectors/runtime-codex.md`
- `connectors/runtime-claude.md`
- `connectors/runtime-claude-code.md`
- `connectors/runtime-chatgpt.md`
- `connectors/runtime-gemini.md`
- `connectors/runtime-grok.md`
- `connectors/runtime-grok-agents.md`

## Runtime invariants

Every setup must preserve:

1. One selected brand per run.
2. No secrets in the skill or brand bundle.
3. Connector preflight before use.
4. Attachment preflight before claiming a referenced file is readable.
5. Evidence classes and source links.
6. Claim approval status.
7. Append-only learning events.
8. A write-back path for approved human revisions.
9. Reports in the writable run folder but patches only in upload-only mode.
10. Exclusion of raw assets, CSV exports and `outputs/ad-analysis/` from brand bundles.
11. Read-only, human-reviewed governance for any universal-method freshness check.

Runtime-specific tool names belong in connector guides, not in the universal strategy method.
