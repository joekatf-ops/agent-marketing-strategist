# agent-ads-creative

Concepts, angles, hooks and scripts at scale, with a production spec for each.

**Status:** In Build
**Function:** Create
**Version:** 0.1.0

---

## What it does

The creative strategy system. Turns research into a testable concept pipeline instead of a pile of one-off ideas.

- The core formula behind a concept that can actually be tested
- Pillars and ad types, so a batch covers the space rather than repeating one idea
- Angles drawn from the research, never invented
- Hooks and scripts, written to the brand voice
- A production spec per creative, static or video
- A test verdict protocol: what kills, what keeps, what scales, and at what threshold

## What you get back

A concept batch, scripts, and a production spec per creative. It stops at the spec. Generation is left to whatever image or video tool you use, so the agent does not break when a model changes.

## What you need before you run it

| Requirement | Why |
|---|---|
| A Master Research Report | Angles and hooks come from evidence |
| A brand and offer brief | Mechanism, promise, offer, voice |
| A Brand Context Pack | Voice rules and claim ceilings |
| Competitor ad research capability | Any swipe or ad library tool |

## Install

**Claude Code or Cowork**
```bash
git clone https://github.com/joekatf-ops/agent-ads-creative.git ~/.claude/skills/agent-ads-creative
```

**Claude Desktop**
Add the cloned folder as a project folder, or upload `SKILL.md` and `references/` into a Project.

**Codex, Cursor, Zed, Aider**
```bash
git clone https://github.com/joekatf-ops/agent-ads-creative.git
```
`AGENTS.md` is picked up automatically from the workspace root.

**ChatGPT, Gemini, Grok**
Open `PROMPT.md` and paste it as the system prompt, Custom GPT instructions, or first message.

## Consistency

One contract per artefact: concept batch, script, static spec, video spec. Counts are fixed, not left to judgement. Naming conventions and folder structure are set in `config/brand.yml` so a client can use their own without forking the agent.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-08-26 | Repo created |
