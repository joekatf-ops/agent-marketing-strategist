# Output Contract: Customer Intelligence Brief
locked: 2026-08-26
version: 1.0.0

Produced by the intelligence pass. Every downstream output reads it. If this is thin,
everything after it is guesswork.

## Artefact
Markdown document. `customer-intelligence-{{brand.slug}}-YYYYMMDD.md`

## Sections, in order

1. **Evidence base** - what was harvested, from where, how much, with links. Table: source,
   type, volume, date pulled. Also lists what could not be harvested and why.
2. **Business guardrails** - target CAC, AOV, contribution margin, break-even CAC, test budget.
   Straight from config. If a value is missing, the row says MISSING and the brief flags it.
3. **Market sophistication** - the stage, 1 to 5, with the count of distinct promises across
   the competitor set and the reasoning. One paragraph plus the evidence table.
4. **Awareness distribution** - where the bulk of the market sits, with the language evidence
   that shows it. One paragraph plus at least three verbatim quotes.
5. **Competitor message map** - table: brand, dominant promise, named mechanism, dominant
   format, longest-running ad and its run length, link.
6. **Personas** - 2 to 4, behavioural only. Each: name, the situation that activates the need,
   what they already do and believe, what they distrust, purchase criteria. No demographics
   unless they diagnose the behaviour.
7. **Outcomes by persona** - each persona's 2 to 4 problems or desired outcomes, ranked by how
   often the language appears in the evidence.
8. **Voice of Customer bank** - the six-part structure: situation, problem language, desired
   outcome, failed alternatives, objections, proof language. Minimum 8 verbatim quotes per
   part, each with a source link.
9. **Objection ranking** - the objection families present, ranked by frequency, each with the
   necessary belief it maps to and 2 or more verbatim examples.
10. **Claim ceiling** - what can and cannot be said in this category and market, and which
    claims already have approved wording.
11. **White space** - what nobody in the competitor set is saying that the evidence supports.
    2 to 5 items, each with the evidence that supports it.
12. **What is thin** - explicit list of anything under-evidenced, and what would fix it.

## Counts

- Personas: 2 to 4
- Outcomes per persona: 2 to 4
- Verbatim quotes in the VoC bank: 8 or more per part
- Competitors in the message map: 5 or more, or a stated reason why fewer
- White space items: 2 to 5

## Formatting rules

- Every quote is verbatim, uncorrected, with a source link
- Every claim carries a source or the tag `[UNSOURCED, strategist judgement]`
- Tables for anything comparative, prose only where reasoning is being shown
- No em dashes

## Never

- A persona defined by age or gender alone
- A quote that was cleaned up, paraphrased or invented
- A sophistication or awareness call without the count or the language behind it
- Filling section 8 to hit the quote count with near-duplicates

## Self-check before presenting

- [ ] Section order matches exactly
- [ ] Every persona is behavioural, not demographic
- [ ] Every quote has a source link and is verbatim
- [ ] Sophistication stage has a promise count behind it
- [ ] Awareness call has at least three quotes behind it
- [ ] Section 12 is honest, not empty by default
- [ ] No brand value used that did not come from config or the Brand Context Pack
