# Foreplay Connector

Last verified: 2026-09-10 through live MCP discovery, board reads, Discovery search and REST reads.

Foreplay is the preferred connected saved-ad source. Use `references/28-saved-ad-layouts.md`
for layout selection; absent access does not block original creative.

Official sources:
- [MCP overview](https://feedback.foreplay.co/en/help/articles/0009441-what-is-the-foreplay-mcp)
- [API documentation](https://public.api.foreplay.co/docs)
- [Current API schema](https://public.api.foreplay.co/openapi.json)

## Access and authentication

MCP endpoint: `https://public.api.foreplay.co/mcp`. Prefer connected tools and current schemas.
If the host does not expose them, use an authorised MCP client or REST fallback. Do not claim
the native tool list refreshed merely because a fallback worked.

The current REST base is `https://public.api.foreplay.co`, using an `Authorization: Bearer <token>`
header. Keep credentials in existing secret storage or host configuration, never in a prompt,
repository, brand folder, command output or run record. Do not assume an environment-variable
name. A bare API key in the Authorization header returned 401 in the verified run; the documented
Bearer form succeeded. Diagnose header format before asking for another key. Do not alter an
otherwise valid OAuth configuration.

MCP discovery and saved-ad reads accepted the API key in Bearer form in this run. Lens performance
tools separately required an OAuth bearer token and returned 403 for the API-key connection.
Mark creative retrieval and performance retrieval independently. Do not retry a known API-key
Lens restriction with the same key; use the provider's OAuth connection or a supplied export.

Preflight with live tool discovery and one read-only board, swipe or brand query. Confirm the
intended account/workspace from the returned data, without publishing private account details.
Configured is not available until that query succeeds. Check usage when a larger search is needed.

## Read routes verified in this session

Discover live tool schemas or the current API schema before calling these observed routes.

| Task | MCP capability | REST equivalent |
|---|---|---|
| Find saved boards | `get_boards` | `GET /api/boards` |
| Read a selected board | `get_board_ads` | `GET /api/board/ads` |
| Read the swipe file | `get_swipefile_ads` | `GET /api/swipefile/ads` |
| Fill a reference gap | `search_discovery_ads` | Discover current route in the API schema |
| Check credits | `get_user_usage` | `GET /api/usage` |
| Discover own-account performance | `get_lenses`, then metric and insight tools | OAuth capability; do not infer from REST access |

Resolve board IDs with a board list. Fetch a bounded sample using `board_id`, `display_format`
(`image` for statics) and `limit`. Board retrieval uses returned cursors; swipe-file retrieval uses
offsets. A short filtered page does not establish library size. Report sampling limits.

For Discovery, combine the message/format query with category or brand context. A broad word such
as "grounding" can return unrelated products. Inspect relevance rather than trusting the query.
MCP field presets can reduce output, but explicitly include `foreplay_url`, `id`, `name`, `image`
and any evidence fields needed for the task. A media preset can omit the source link. Preserve a
returned source URL or ID; do not manufacture a Foreplay URL from a presumed pattern.

## Evidence and delivery

Inspect media and retain source, date and board. Saved status, automated scores, running duration
and a board name such as "best ads" do not establish measured success.

Use Lens only when relevant and authorised, and verify account, metric definitions, window and
exposure before using performance data. Connector access does not authorise publishing or changing
budgets. Keep competitor material separate from first-party product or performance evidence.

Use native Foreplay previews when the host exposes them. If the fallback transport cannot render
widgets, use accessible source media for inspection and return source links with the analysis.
Do not claim a visual review from an ad's title or transcript.

Fallbacks: supplied ads, reviewed local swipes, another ad library or an original composition.
State the specific capability gap. Reading boards does not authorise reorganising them.
