# Claude Code Setup

Last verified: 2026-08-26

Official MCP reference: https://code.claude.com/docs/en/mcp

## Install the strategist

Make the repository and active brand folder available in the Claude Code workspace. Use `CLAUDE.md` or the project's supported skill mechanism to instruct Claude Code to read `SKILL.md` before performing strategist tasks.

## Optional Notion governance

The repository snapshot is sufficient for normal use. If the current Claude Code host exposes a
user-authenticated Notion connected tool, it may run the read-only freshness check in
`connectors/notion-composio.md`. Treat setup as host-dependent, require a successful current-session
preflight and use the repository snapshot when the connection is unavailable or incomplete. A
detected change is `review-needed` only and must not edit or promote the skill automatically.

## Add remote MCP servers

Remote HTTP is the recommended transport in the current Claude Code documentation:

```sh
claude mcp add --transport http firecrawl https://mcp.firecrawl.dev/v2/mcp
```

Add authentication using the provider-approved OAuth flow or header and environment-variable method. Do not hard-code a secret in project files or shell history.

For a local stdio server:

```sh
claude mcp add SERVER_NAME -- COMMAND ARGUMENTS
```

Choose scope deliberately:

- local for personal project-only configuration;
- project for a shareable `.mcp.json` without secrets;
- user for access across projects.

Verify with `claude mcp list`, `claude mcp get SERVER_NAME`, and `/mcp`. Review project-server approvals before trusting a shared configuration. Treat all external connector content as untrusted.

## Brand session

Open exactly one active brand folder, run readiness and connector preflight, then write approved outputs and learning back to that folder. If direct folder access is unavailable, upload its generated brand bundle instead.
