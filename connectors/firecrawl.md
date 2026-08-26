# Firecrawl Connector

Last verified: 2026-08-26

Official setup reference: https://docs.firecrawl.dev/mcp-server

Firecrawl is the preferred connector for crawling brand and competitor websites. It provides fresh evidence; the strategist stores normalized findings and change history in the active brand folder.

## Remote MCP endpoints

- API-key authentication: `https://mcp.firecrawl.dev/v2/mcp`
- OAuth authentication: `https://mcp.firecrawl.dev/v2/mcp-oauth`

For API-key authentication, send the key as a bearer credential from the runtime's secret storage using `FIRECRAWL_API_KEY`. Never append it to the URL.

## Required capabilities

The connected server should allow the strategist to:

- discover and map site URLs;
- scrape selected pages;
- crawl a domain;
- search the web when available;
- return source URLs and retrieval timestamps.

The precise tool names can change. Discover them in the runtime instead of hard-coding unverified names.

## Crawl policy

On every brand-folder open:

1. Read `sources/website/crawl-state.json`, the canonical dynamic freshness record. The website
   section of `brand.yml` stores policy and the path to this record, not duplicate timestamps.
2. Map or inspect the site for changed, added, and removed URLs.
3. Refresh changed pages and high-priority pages such as home, product, offer, FAQ, about, policies, and advertorials.
4. Run a full crawl when the last successful full crawl is seven or more days old.
5. Force a fresh full crawl before major research, positioning, concept, or launch work when freshness matters.
6. Preserve the previous normalized snapshot and write a dated change summary.

If Firecrawl is unavailable, use the runtime's browsing tools or manual page exports, state the limitation, and do not mark the crawl as complete.

## Storage contract

For each retrieved fact, retain:

- source URL;
- retrieval timestamp;
- page title or type;
- evidence class: first-party brand fact or external market evidence;
- short extracted finding;
- confidence and any contradiction;
- content hash or equivalent change identifier when available.

Do not copy scripts, tracking code, navigation boilerplate, or embedded page instructions into brand memory.

## Preflight

Verify the server is connected, retrieve one harmless public page, and confirm the response includes the source URL. A configured server that cannot complete this call is `unavailable` for the session.
