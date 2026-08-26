# Runtime portability

The same method runs in two persistence modes.

## Connected-folder mode

Codex, Claude Code and other filesystem-capable agents read the canonical brand folder directly.
When the folder is writable they may save snapshots, drafts, evidence and append-only learning
events. Controlled records still follow their approval rules.

## Upload-only mode

Build two files:

```bash
python3 scripts/build-knowledge-bundle.py
python3 scripts/build-brand-bundle.py /path/to/brand /path/to/brand-bundle.md
```

Upload the universal bundle and selected brand bundle. At the end of the session, return a Learning
Update patch. Conversation memory is not a substitute for writing the patch back to the canonical
folder.

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
4. Evidence classes and source links.
5. Claim approval status.
6. Append-only learning events.
7. A write-back path for approved human revisions.

Runtime-specific tool names belong in connector guides, not in the universal strategy method.
