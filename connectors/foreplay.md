# Foreplay Connector

Last verified: 2026-08-26

Foreplay is an optional creative-intelligence connector. Connection details can depend on the workspace, provider distribution, and runtime. Use the current official instructions supplied to the account. Do not guess an endpoint, package name, or authentication scheme.

**Credential name:** this skill does not assume a canonical Foreplay environment-variable name.
Use the exact secret name specified by the provider or workspace administrator and keep it outside
the repository and brand folder.

## Connection procedure

1. Obtain the approved Foreplay connection instructions and credential.
2. Add the connector using the relevant runtime guide.
3. Keep all credentials in secret storage.
4. List the discovered tools and confirm the allowed workspace.
5. Run one read-only brand, ad, or swipe-file query.
6. Mark it `available` only when the query succeeds.

Capabilities seen in current integrations can include brand discovery, domain or page-ID lookup, ad retrieval, swipe-file access, and lens research. Always use the tool descriptions returned by the live connector.

## Research use

Use Foreplay to:

- build a relevant competitor and inspiration set;
- inspect repeated hook, visual, offer, and format patterns;
- retrieve saved ads and team swipe-file evidence;
- compare patterns across brands without copying execution.

Record the source brand, ad identifier or URL, observed date, pattern, and what was inferred. Foreplay material remains **market evidence** until independently validated for the active brand.

## Safe fallback

If Foreplay is unavailable, use TrendTrack, public ad libraries, direct site research, and the existing brand-folder swipe evidence. State the source limitations. Never claim access to private swipe files that were not retrieved.
