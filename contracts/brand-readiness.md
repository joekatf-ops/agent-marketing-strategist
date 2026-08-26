# Output Contract: Brand Readiness
locked: 2026-08-26
version: 1.0.0

The mandatory preflight before research, concepts, hooks, copy, production, or diagnosis.

## Sections, in order

1. **Run identity** - brand slug, market, product, folder path or bundle version, requested mode
2. **Readiness verdict** - READY, READY WITH LIMITS, or BLOCKED for the requested mode
3. **Website freshness** - last change check, last full crawl, material changes, and action taken
4. **Evidence inventory** - verified brand facts, assertions, brand-customer evidence, market
   evidence, behavioural evidence, and strategist judgement
5. **Required-input check** - each input required by the requested mode, its status, and source
6. **Connector preflight** - connector, required capability, actual result, and fallback
7. **Claim and compliance gate** - approved claims, unapproved claims, market restrictions, owner
8. **Learning state** - approved-rule version, unresolved conflicts, proposed learning awaiting review
9. **Limits on this run** - what may be done, what must be labelled provisional, and what is blocked
10. **Next actions** - ordered actions that unlock or improve the requested mode

## Verdict rules

- **READY:** all mode-critical inputs are current, traceable, and approved.
- **READY WITH LIMITS:** useful work can proceed, but missing evidence lowers confidence or makes
  specified sections provisional.
- **BLOCKED:** a missing identity, product truth, claim gate, destination, or approved concept would
  make the requested output unsafe or fictional.

A new brand without reviews is not automatically blocked from research. Mark customer evidence as
pre-customer, use external sources as market evidence, and prohibit first-party customer claims.

## Status table

| Input | Required for mode | Status | Source | Freshness | Consequence | Action |
|---|---|---|---|---|---|---|

Allowed status values: VERIFIED, PRESENT BUT UNVERIFIED, STALE, MISSING, NOT REQUIRED.

## Hard rules

- Resolve exactly one active brand, market, and product.
- Run a website change check whenever the folder opens.
- Run a full crawl after seven days or before major strategy and launch work.
- Do not count a configured connector as available until a read-only preflight succeeds.
- Do not promote market evidence into brand-customer evidence.
- Do not silently repair missing facts with assumptions.

## Self-check

- [ ] One brand, market, product, and requested mode are named
- [ ] The verdict follows the mode-specific rules in `references/13-brand-folder.md`
- [ ] Website freshness and material changes are explicit
- [ ] Every evidence class is separated
- [ ] Connector availability is based on successful calls
- [ ] Each limit names its consequence
- [ ] The next action list is ordered and specific

