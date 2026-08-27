# Output Contract: Brand Readiness
locked: 2026-08-27
version: 1.1.0

The mandatory preflight before research, concepts, hooks, copy, production, or diagnosis.

## Sections, in order

1. **Run identity** - brand slug, market, product, region, folder path or bundle version, requested
   mode, evidence version and approved-learning version
2. **Readiness verdict** - READY, READY WITH LIMITS, or BLOCKED for the requested mode
3. **Website freshness** - last change check, last full crawl, material changes, and action taken
4. **Evidence inventory** - verified brand facts, assertions, brand-customer evidence, market
   evidence, behavioural evidence, and strategist judgement
5. **Required-input check** - each input required by the requested mode, its status, and source
6. **Connector preflight** - connector, required capability, actual result, and fallback
7. **Claim and compliance gate** - approved claims, unapproved claims, market restrictions, owner
8. **Learning state** - approved-rule version, unresolved conflicts, proposed learning awaiting review
9. **Strategy state** - approved Who x Primary Problem coordinate, next available CONTST number,
   source classification, prior test cited for ITR, and any unresolved test-register conflict
10. **Launch and destination readiness** - production capacity, campaign and naming codes, economics,
    proposed destination, message-match owner, manual Meta operator and scaling eligibility
11. **Limits on this run** - what may be done, what must be labelled provisional, and what is blocked
12. **Next actions** - ordered actions that unlock or improve the requested mode

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
- Resolve one region and controlled brand, product and region naming codes before launch planning.
- Run a website change check whenever the folder opens.
- Run a full crawl after seven days or before major strategy and launch work.
- Do not count a configured connector as available until a read-only preflight succeeds.
- Do not promote market evidence into brand-customer evidence.
- Do not silently repair missing facts with assumptions.
- Do not allocate, reuse or skip a CONTST identifier from conversation memory.
- Treat Meta launch and diagnosis as manual workflows. Never imply live publishing, account reads or
  automated budget control.
- Block launch when the destination does not continue the execution's promise, proof and CTA, unless
  a deliberate congruent exception is recorded in a Destination Handoff.

## Self-check

- [ ] One brand, market, product, and requested mode are named
- [ ] Region, naming codes and the canonical folder or bundle versions are named where launch applies
- [ ] The verdict follows the mode-specific rules in `references/13-brand-folder.md`
- [ ] Website freshness and material changes are explicit
- [ ] Every evidence class is separated
- [ ] Connector availability is based on successful calls
- [ ] Coordinate and CONTST state are traceable to controlled records, not memory
- [ ] Launch mode identifies the manual operator, economics, destination and production constraints
- [ ] Each limit names its consequence
- [ ] The next action list is ordered and specific
