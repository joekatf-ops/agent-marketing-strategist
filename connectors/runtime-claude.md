# Claude Setup

Last verified: 2026-08-26

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
