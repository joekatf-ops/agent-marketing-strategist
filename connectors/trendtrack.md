# TrendTrack Connector

Last verified: 2026-08-26

TrendTrack is an optional market-observation connector. Its public installation method and server address can depend on the account and runtime. Obtain the current endpoint, package, or plugin instructions from the TrendTrack account or provider. Do not invent an MCP URL.

**Credential name:** this skill does not assume a canonical TrendTrack environment-variable name.
Use the exact secret name specified by the provider or workspace administrator and keep it outside
the repository and brand folder.

## Connection procedure

1. Obtain the provider-approved connection method and credential.
2. Add it as a remote MCP server, local MCP server, or native plugin using the chosen runtime guide.
3. Store credentials outside the repository and brand folder.
4. List the discovered tools.
5. Run a read-only credit or usage check when exposed.
6. Run a small lookup before marking the connector `available`.

Common capabilities exposed by current TrendTrack integrations include usage or credit checks, ad lookup, shop search, ad search, product search, and account-level ad research. Treat discovered tool names as authoritative for the current session.

## Research use

Use TrendTrack for:

- finding relevant brands and shops;
- identifying active ads and recurring patterns;
- inspecting products, offers, formats, and landing destinations;
- generating competitor candidates for deeper first-party verification.

TrendTrack observations are **market evidence**, not facts about the active brand. Save the original URL or platform identifier, observation date, filters, and a confidence note.

## Safe fallback

If TrendTrack is unavailable or out of credits, use Foreplay, public ad libraries, search, and direct competitor-site research. Record which fallback was used. Never simulate TrendTrack findings.
