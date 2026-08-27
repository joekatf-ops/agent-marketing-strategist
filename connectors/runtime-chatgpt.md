# ChatGPT Setup

Last verified: 2026-08-26

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
