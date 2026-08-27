# Grok Agents Setup

Last verified: 2026-08-26

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
