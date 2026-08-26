# Claude Code Setup

Last verified: 2026-08-26

Official MCP reference: https://code.claude.com/docs/en/mcp

## Install the strategist

Make the repository and active brand folder available in the Claude Code workspace. Use `CLAUDE.md` or the project's supported skill mechanism to instruct Claude Code to read `SKILL.md` before performing strategist tasks.

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

