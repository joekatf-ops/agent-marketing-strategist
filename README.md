# agent-marketing-strategist

The marketing strategist. Researches the customer, builds the concepts, writes the copy and
scripts, and reads what happened.

**Status:** In Build
**Function:** Create
**Version:** see `VERSION`

---

## What it does

Most creative agents start at the wrong end. They write a hook, then look for a reason.

This one starts with evidence. It mines competitor ads and customer reviews, works out how the
market actually talks, calls where the market sits on awareness and sophistication, and only
then builds concepts. Everything it writes afterwards traces back to something someone actually
said.

Then it reads what happened and decides what to make next.

## What you get back

Six artefacts, each governed by a locked contract in `contracts/`.

| Artefact | What it is |
|---|---|
| Customer Intelligence Brief | Personas, Voice of Customer bank, objection ranking, competitor message map, white space |
| Concept Batch | Three concepts, each with a hypothesis, its evidence, and four awareness executions |
| Ad Copy | Two primary texts, two headlines, two descriptions, CTA, with lead types named |
| Video Script | Beat-by-beat table, three-part opening, shot list, captions |
| Static and Carousel Spec | Layout, copy, visual direction, ready to build |
| Ad Diagnosis | Read validity first, then a ranked change list where every row carries a number |

## The concept model

**Concept = Persona x Outcome x Angle.** Change any one and it is a new concept. Nothing else
is a concept axis.

- **Persona** is behavioural, never demographic
- **Outcome** is one problem escaped or desire achieved
- **Angle** is a one-sentence strategic argument that never restates the outcome
- **Angle type**, exactly one of: How it works, The reframe, Vs the old way, Proof you can see

Format, hook, length, creator and awareness are execution variables, not concept axes.

Every concept ships four awareness executions: unaware, problem aware, solution aware, product
aware. Each makes a complete standalone argument, because Meta does not sequence ads for you.

## What you need before you run it

| Requirement | Why |
|---|---|
| A Brand Context Pack | Voice, palette, product, proof, price, guarantee, claim ceiling |
| `config/brand.yml` | Economics, naming codes, production limits, test thresholds |
| Competitor URLs and seed terms | The research pass has to start somewhere |
| Competitor ad research capability | Foreplay, Trendtrack or the Meta Ad Library |
| Review and community mining capability | Any scraper that reaches reviews, Reddit, comments |

If a required input is missing, the agent names it and stops. It does not guess.

## Install

**Claude Code or Cowork**
```bash
git clone https://github.com/joekatf-ops/agent-marketing-strategist.git ~/.claude/skills/agent-marketing-strategist
```

**Claude Desktop**
Add the cloned folder as a project folder, or upload `SKILL.md` and `references/` into a Project.

**Codex, Cursor, Zed, Aider**
```bash
git clone https://github.com/joekatf-ops/agent-marketing-strategist.git
```
`AGENTS.md` is picked up automatically from the workspace root.

**ChatGPT, Gemini, Grok**
Paste `PROMPT.md` as the system prompt or Custom GPT instructions, then upload
`dist/knowledge-bundle.md` as a knowledge file. Rebuild the bundle with
`python3 scripts/build-knowledge-bundle.py` after any change to `references/` or `contracts/`.

## Configure

```bash
cp config/brand.example.yml config/brand.yml
```

Fill it in, or run `agent-brand-context` once for the brand and let it generate both the Brand
Context Pack and this file. `config/brand.yml` is gitignored. Never commit a real one.

Everything brand-specific lives in that file. If a brand name, theme, account ID or house
naming convention appears anywhere else in this repo, that is a bug.

## How to run it

Point it at the brand and say what you want:

- "Research the market for [product]" gives a Customer Intelligence Brief
- "Build me three concepts" gives a Concept Batch
- "Write the copy for CONTST001_PRA_VID" gives Ad Copy
- "Script the unaware execution" gives a Video Script
- "Why is this ad not working?" plus data gives an Ad Diagnosis

It pauses twice: after the intelligence pass, and after the concept batch. Everything else runs
end to end.

## Consistency

Governed by `OUTPUT-CONTRACT.md` and the six contracts in `contracts/`. Section order, counts
and format are locked. The same brief run twice produces the same shape, in any tool.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-08-26 | Built. Absorbs the former ads-creative and copywriting agents. Twelve reference files, six output contracts, three install surfaces. |
