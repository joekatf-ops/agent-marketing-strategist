# Grok Setup

Last verified: 2026-08-26

Grok product capabilities can differ between consumer, workspace, API, and regional surfaces. This guide does not assume that a Grok chat can install arbitrary MCP servers.

## Portable upload mode

1. Start a dedicated strategist or brand workspace when the surface supports it.
2. Upload the universal strategist knowledge bundle.
3. Upload the current brand bundle.
4. Add the operating instruction from `PROMPT.md`.
5. Require active-brand confirmation, readiness, and evidence labels before generation.
6. Replace the brand bundle after approved learning is written to the durable folder.

## Tool-connected mode

Use live Firecrawl, TrendTrack, or Foreplay only if the current Grok surface or an agent host you control exposes a documented connector or tool mechanism. Configure credentials in that host, run a read-only preflight, and tell the model exactly which tools succeeded.

If no such mechanism is exposed, perform research outside Grok, store cited evidence in the brand folder, rebuild the bundle, and upload it. Never ask Grok to behave as though a connector exists when it cannot call it.

## Learning sync

Grok conversation memory is not authoritative. Human-approved revisions must become structured learning events in the brand folder before they influence future work.

