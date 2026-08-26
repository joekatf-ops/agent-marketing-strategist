# Multi-Brand Learning System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build version 0.2 of the marketing strategist as a portable, multi-brand, continuously learning skill.

**Architecture:** Keep one concise skill entrypoint that routes to focused references and output
contracts. Store all mutable brand evidence and learning in an external brand folder. Use small
standard-library Python scripts for deterministic folder creation, learning capture, bundle
generation and integrity checks.

**Tech Stack:** Markdown, YAML templates, JSON Schema, JSON Lines, Python 3 standard library,
unittest.

**Spec:** `docs/specs/v0.2-multi-brand-learning.md`

## Global Constraints

- No brand-specific fact may live in the universal skill.
- No secret may live in the repository or a brand folder.
- No learning crosses brands automatically.
- Permanent rules require the approved promotion policy.
- Live Meta reporting and publishing are out of scope.
- All generated copy retains the existing evidence and claim gates.
- No em dashes or en dashes in skill output.

---

### Task 1: Package integrity tests

**Files:**
- Create: `tests/test_package_integrity.py`
- Create: `scripts/validate-package.py`

**Interfaces:**
- Consumes: repository root path.
- Produces: `validate(root: pathlib.Path) -> list[str]` and a zero or non-zero CLI exit.

- [ ] Write tests that require every routed reference, contract and example to exist, require
  `SKILL.md` and `AGENTS.md` to retain the same operating sections, and catch unfinished template
  markers in frozen examples.
- [ ] Run the test and verify failure because `validate-package.py` does not exist.
- [ ] Implement the validator with the Python standard library.
- [ ] Run the test and verify it passes.

### Task 2: Brand folder initializer

**Files:**
- Create: `tests/test_init_brand_folder.py`
- Create: `scripts/init-brand-folder.py`
- Create: `templates/brand-folder/brand.yml`
- Create: `templates/brand-folder/context/brand-core.md`
- Create: `templates/brand-folder/context/voice.md`
- Create: `templates/brand-folder/products/catalog.yml`
- Create: `templates/brand-folder/products/claims.yml`
- Create: `templates/brand-folder/connectors/capabilities.yml`

**Interfaces:**
- Consumes: destination path, brand name and slug.
- Produces: `initialise(destination, name, slug) -> pathlib.Path` and a complete portable folder.

- [ ] Write tests for complete folder creation, placeholder substitution and refusal to overwrite
  a non-empty destination.
- [ ] Run the tests and verify failure because the initializer does not exist.
- [ ] Implement the templates and initializer without external packages.
- [ ] Run the tests and verify they pass.

### Task 3: Learning event capture

**Files:**
- Create: `tests/test_record_learning.py`
- Create: `scripts/record-learning.py`
- Create: `schemas/learning-event.schema.json`

**Interfaces:**
- Consumes: a learning event JSON object and brand folder.
- Produces: `validate_event(event) -> list[str]` and `append_event(folder, event) -> str`.

- [ ] Write tests for a valid event, missing required fields, cross-brand mismatch and append-only
  storage.
- [ ] Run the tests and verify failure because the recorder does not exist.
- [ ] Implement validation, identifier creation and JSON Lines append.
- [ ] Run the tests and verify they pass.

### Task 4: Uploadable brand bundle

**Files:**
- Create: `tests/test_build_brand_bundle.py`
- Create: `scripts/build-brand-bundle.py`

**Interfaces:**
- Consumes: a brand folder.
- Produces: `build_bundle(folder, output) -> pathlib.Path` containing approved context, synthesis
  and learning while excluding secrets and raw bulk evidence.

- [ ] Write tests for deterministic ordering, secret exclusion and required section inclusion.
- [ ] Run the tests and verify failure because the builder does not exist.
- [ ] Implement the bundle builder.
- [ ] Run the tests and verify they pass.

### Task 5: Skill router and operating references

**Files:**
- Modify: `SKILL.md`
- Modify: `AGENTS.md`
- Modify: `PROMPT.md`
- Create: `references/13-brand-folder.md`
- Create: `references/14-learning-system.md`
- Create: `references/15-connectors.md`
- Create: `references/16-hook-formats.md`
- Create: `references/17-runtime-portability.md`

**Interfaces:**
- Consumes: task mode and connected brand folder.
- Produces: deterministic reference routing, preflight, research refresh, creation and learning
  workflow.

- [ ] Add package-integrity expectations for all new routes and verify failure.
- [ ] Implement the concise router and focused references.
- [ ] Run package integrity and verify all routes resolve.

### Task 6: Connector and runtime guides

**Files:**
- Create: `connectors/README.md`
- Create: `connectors/firecrawl.md`
- Create: `connectors/trendtrack.md`
- Create: `connectors/foreplay.md`
- Create: `connectors/runtime-codex.md`
- Create: `connectors/runtime-claude.md`
- Create: `connectors/runtime-claude-code.md`
- Create: `connectors/runtime-chatgpt.md`
- Create: `connectors/runtime-gemini.md`
- Create: `connectors/runtime-grok.md`
- Create: `connectors/runtime-grok-agents.md`

**Interfaces:**
- Consumes: capability and runtime.
- Produces: setup, secret, preflight, fallback and write-back instructions.

- [ ] Add package-integrity expectations for the connector matrix and verify failure.
- [ ] Write capability-first and runtime-specific guides without embedding credentials.
- [ ] Run package integrity and verify every documented guide exists.

### Task 7: Output contracts and frozen examples

**Files:**
- Create: `contracts/brand-readiness.md`
- Create: `contracts/hook-batch.md`
- Create: `contracts/learning-update.md`
- Modify: `contracts/ad-copy.md`
- Modify: `contracts/concept-batch.md`
- Modify: `contracts/customer-intelligence.md`
- Modify: `contracts/ad-diagnosis.md`
- Create: `examples/hook-batch.md`
- Create: `examples/learning-update.md`
- Create: `examples/brand-readiness.md`

**Interfaces:**
- Consumes: brand evidence, selected concept and approved revisions.
- Produces: six hook packages, two leads across three copy lengths, readiness status and proposed
  learning promotions.

- [ ] Add integrity checks for contract counts and frozen examples, then verify failure.
- [ ] Implement the contracts and examples.
- [ ] Run package integrity and verify the examples contain no unfinished placeholders.

### Task 8: Research, configuration and documentation integration

**Files:**
- Modify: `references/11-research-tools.md`
- Modify: `references/06-concept-model.md`
- Modify: `config/brand.example.yml`
- Modify: `README.md`
- Modify: `OUTPUT-CONTRACT.md`
- Modify: `scripts/build-knowledge-bundle.py`
- Modify: `VERSION`

**Interfaces:**
- Consumes: existing package plus v0.2 components.
- Produces: a coherent installable release with website freshness, market-evidence labelling,
  portfolio awareness and upload-mode support.

- [ ] Add tests for the v0.2 version, bundle inclusion and removal of the rigid four-execution
  requirement, then verify failure.
- [ ] Integrate the research and configuration changes and update release documentation.
- [ ] Run all tests and both bundle builders.
- [ ] Run package validation and inspect the repository diff.

