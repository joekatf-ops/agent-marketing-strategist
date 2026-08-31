# Website evidence

Keep crawl state, normalized page snapshots and dated change reports here.

- `crawl-state.json` is the machine-readable freshness record.
- Store normalized pages under `snapshots/YYYY-MM-DD/`.
- Store change summaries under `changes/YYYY-MM-DD.md`.
- Preserve source URL, retrieval time, connector and content hash.
- Never let a changed page silently replace an approved claim, offer, price or rule.

Run a change check whenever this brand folder opens, a full refresh after seven days, and a forced
refresh before major research, concept, positioning or launch work.

