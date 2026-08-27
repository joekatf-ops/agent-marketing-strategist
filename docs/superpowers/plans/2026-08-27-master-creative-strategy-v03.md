# Master Creative Strategy v0.3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish v0.3.0 with Joe's Notion Master Creative Strategy as the universal method while preserving the v0.2 multi-brand, security, learning and runtime systems.

**Architecture:** The concise entrypoints route to focused references and governed output contracts. Mechanical package validation prevents the superseded model from re-entering active instructions. Portable brand folders store enduring coordinates, sequential test batches and graduated winners separately from human-revision learning.

**Tech Stack:** Markdown skill package, YAML and JSON brand templates, Python standard-library validators and unittest suite.

**Spec:** `docs/superpowers/specs/2026-08-27-master-creative-strategy-v03-design.md`

## Global Constraints

- Concept coordinate is exactly `Who x Primary Problem`.
- Every initial NNT or INSPO test has UWA, PRA, SLA and PDA executions.
- Most Aware is theory and conversion-environment guidance, never a standard ad.
- Every NNT, INSPO or ITR batch receives a new sequential `CONTST###`.
- Creative testing is ABO with a $50 daily ad-set floor, approximately $100 preferred and a five-full-day planned observation window.
- Scaling is CBO and graduated ads preserve their real Post ID.
- Live Meta access remains deferred; launch outputs are manual and diagnosis accepts supplied data.
- Notion access is read-only and never automatically mutates the method.
- Brand facts and learning never transfer automatically between brands.
- No secret may enter a generated brand bundle.

---

### Task 1: v0.3 acceptance and drift detection

**Files:**
- Modify: `tests/test_package_integrity.py`
- Modify: `tests/test_init_brand_folder.py`
- Modify: `tests/test_build_brand_bundle.py`
- Modify: `scripts/validate-package.py`

**Interfaces:**
- Consumes: the existing `validate(root) -> list[str]` package boundary.
- Produces: semantic v0.3 validation errors, new brand-template expectations and safe-bundle expectations.

- [ ] **Step 1: Replace superseded v0.2 expectations with v0.3 behavior tests**

Add tests that expect the package to declare 0.3.0, use Who x Primary Problem, require four initial awareness ads, exclude MWA from standard ad contracts, use the locked naming shapes, include new governance files and produce the new brand state files.

- [ ] **Step 2: Add mutation tests for strategy drift**

Use a temporary package to prove `validate()` rejects:

```python
errors = validator.validate(root)
self.assertIn("SKILL.md contains superseded concept model", errors)
```

and prove a standard-ad contract containing `| MWA |` is rejected.

- [ ] **Step 3: Run the focused tests and verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_package_integrity tests.test_init_brand_folder tests.test_build_brand_bundle -v
```

Expected: failures for v0.2 version, missing v0.3 files, old concept model, old awareness handling and missing semantic validator behavior.

- [ ] **Step 4: Implement the minimal validator rules**

Add focused checks to `validate-package.py` for entrypoint model drift, standard-ad MWA rows, v0.3 required files and version. Do not ban awareness theory from customer-state references.

- [ ] **Step 5: Run focused tests**

Expected: validator mutation tests pass; package-level tests remain red until later tasks supply the files and instructions.

- [ ] **Step 6: Commit**

```bash
git add tests scripts/validate-package.py
git commit -m "test: define v0.3 strategy acceptance"
```

### Task 2: canonical method and entrypoints

**Files:**
- Modify: `SKILL.md`
- Modify: `AGENTS.md`
- Modify: `PROMPT.md`
- Modify: `references/05-copy-craft.md`
- Replace: `references/06-concept-model.md`
- Modify: `references/08-formats.md`
- Modify: `references/11-research-tools.md`
- Modify: `references/16-hook-formats.md`
- Create: `references/18-master-creative-strategy.md`

**Interfaces:**
- Consumes: evidence, claims, brand folder and connector references retained from v0.2.
- Produces: one shared operating body and the canonical coordinate/execution/source hierarchy.

- [ ] **Step 1: Run the current acceptance tests and retain the expected RED evidence**

- [ ] **Step 2: Rewrite the concise entrypoint body**

Route concept, launch, destination and method-governance asks to their focused references and contracts. Keep `SKILL.md` and `AGENTS.md` operating bodies identical.

- [ ] **Step 3: Replace the concept model**

Define coordinate, batch, execution variables, source rules, four awareness jobs, hook selection, delivery copy and the evidence-led operating loop without the old equation or fixed 50/50 source mix.

- [ ] **Step 4: Normalize supporting terminology**

Change concept-level persona/outcome/angle language to Who/Primary Problem/messaging route where load-bearing. Preserve outcome, persona and angle only when discussing general customer theory or historical migration.

- [ ] **Step 5: Add the reviewed Notion snapshot and precedence rules**

Record page ID, last-edited time, review date, locked status, source hierarchy and no-automatic-mutation rule.

- [ ] **Step 6: Run package validation and focused tests**

- [ ] **Step 7: Commit**

```bash
git add SKILL.md AGENTS.md PROMPT.md references
git commit -m "feat: adopt the canonical Who by Problem method"
```

### Task 3: contracts, testing, naming and launch lifecycle

**Files:**
- Modify: `contracts/brand-readiness.md`
- Modify: `contracts/customer-intelligence.md`
- Replace: `contracts/concept-batch.md`
- Modify: `contracts/hook-batch.md`
- Modify: `contracts/ad-copy.md`
- Modify: `contracts/video-script.md`
- Modify: `contracts/static-spec.md`
- Modify: `contracts/ad-diagnosis.md`
- Create: `contracts/campaign-launch-plan.md`
- Create: `contracts/destination-handoff.md`
- Replace: `references/07-naming.md`
- Replace: `references/09-testing-and-diagnosis.md`
- Modify: `OUTPUT-CONTRACT.md`

**Interfaces:**
- Consumes: coordinate and source definitions from `references/06-concept-model.md`.
- Produces: stable output shapes for research, four-ad test planning, production, manual launch, destination continuity and diagnosis.

- [ ] **Step 1: Update customer intelligence output**

Require prioritised Who definitions, primary Problems, pairing evidence, constraints and test questions while retaining the existing evidence system.

- [ ] **Step 2: Replace the concept-batch contract**

The card identifies coordinate and batch separately. Every initial batch specifies UWA, PRA, SLA and PDA, each with messaging route, format, proof, destination and job.

- [ ] **Step 3: Add traceability fields to production contracts**

Every hook, copy, script and static output carries CONTST, source, Who, Problem, awareness, route, primary hook, media type, format, proof, destination, CTA, production needs and full ad name.

- [ ] **Step 4: Add manual launch and destination contracts**

Campaign Launch Plan governs ABO structure, budgets, names, four ads, five days and preflight. Destination Handoff governs ad-to-page message continuity and records deliberate destination exceptions.

- [ ] **Step 5: Replace naming and testing references**

Lock campaign, ad-set and full ad names. Lock ABO/CBO stages, $50/$100 guidance, five-day review, read validity, three measurement layers, six decisions, Post ID graduation and non-causal interpretation.

- [ ] **Step 6: Run focused and full tests**

- [ ] **Step 7: Commit**

```bash
git add contracts references/07-naming.md references/09-testing-and-diagnosis.md OUTPUT-CONTRACT.md
git commit -m "feat: govern four-ad testing and scaling"
```

### Task 4: portable coordinate, test and winner memory

**Files:**
- Modify: `templates/brand-folder/brand.yml`
- Modify: `templates/brand-folder/README.md`
- Replace: `templates/brand-folder/strategy/concept-register.yml`
- Create: `templates/brand-folder/strategy/test-register.yml`
- Create: `templates/brand-folder/strategy/winner-library.yml`
- Modify: `templates/brand-folder/strategy/hypothesis-backlog.yml`
- Modify: `templates/brand-folder/products/economics.yml`
- Modify: `references/13-brand-folder.md`
- Modify: `references/14-learning-system.md`
- Modify: `scripts/build-brand-bundle.py` only if the existing `strategy/` allowlist does not safely include the new files.

**Interfaces:**
- Consumes: initialized portable brand folders.
- Produces: coordinate history, sequential test batches, safe winner history and v0.3 readiness fields.

- [ ] **Step 1: Update the template manifest**

Add method version, locked CONTST prefix, next test number, naming code maps and testing defaults. Remove configurable concept prefix semantics.

- [ ] **Step 2: Define the three registers**

Concept register stores enduring coordinate keys. Test register stores each batch and four ads. Winner library stores Post ID graduation and scale history.

- [ ] **Step 3: Separate test learning from revision learning**

Document that test observations live in test records while approved human edits remain in the append-only learning ledger.

- [ ] **Step 4: Run initializer and bundle tests**

Verify a new folder contains all registers and a generated bundle includes the safe summaries without raw evidence, raw revisions or credentials.

- [ ] **Step 5: Commit**

```bash
git add templates references/13-brand-folder.md references/14-learning-system.md scripts/build-brand-bundle.py tests
git commit -m "feat: retain coordinate test and winner history"
```

### Task 5: Composio Notion governance and runtime portability

**Files:**
- Create: `connectors/notion-composio.md`
- Modify: `connectors/README.md`
- Modify: `references/15-connectors.md`
- Modify: `references/17-runtime-portability.md`
- Modify: `connectors/runtime-codex.md`
- Modify: `connectors/runtime-claude.md`
- Modify: `connectors/runtime-claude-code.md`
- Modify: `connectors/runtime-chatgpt.md`
- Modify: `connectors/runtime-gemini.md`
- Modify: `connectors/runtime-grok.md`
- Modify: `connectors/runtime-grok-agents.md`

**Interfaces:**
- Consumes: a user-authenticated Composio Notion connection when present.
- Produces: read-only method freshness checks and explicit unavailable fallbacks across runtimes.

- [ ] **Step 1: Add the read-only connector guide**

Document search, metadata, markdown, recursive blocks, completeness validation and account-link fallback. Use page ID `3c02deb4f6ba80b3be07c725f8b6807b`. Do not include credentials.

- [ ] **Step 2: Add capability and precedence guidance**

Configured does not mean live. Notion changes create a review-needed finding and never self-edit the skill.

- [ ] **Step 3: Update runtime guides minimally**

Explain that the repository snapshot is sufficient for normal use and Composio is optional for method-governance checks.

- [ ] **Step 4: Run bundle and package validation tests**

- [ ] **Step 5: Commit**

```bash
git add connectors references/15-connectors.md references/17-runtime-portability.md
git commit -m "docs: add read-only Notion governance"
```

### Task 6: examples, documentation and release packaging

**Files:**
- Create: `examples/campaign-launch-plan.md`
- Create: `examples/destination-handoff.md`
- Replace: `examples/brand-readiness.md`
- Replace: `examples/hook-batch.md`
- Modify: `examples/learning-update.md` only where legacy terminology is load-bearing.
- Modify: `README.md`
- Modify: `VERSION`
- Modify: `config/brand.example.yml`
- Modify: `scripts/build-knowledge-bundle.py` only if a new routed folder is required.

**Interfaces:**
- Consumes: every v0.3 contract and reference.
- Produces: frozen examples and an uploadable v0.3 universal bundle for filesystem-free LLMs.

- [ ] **Step 1: Write frozen examples from one fictional brand**

Use complete, internally consistent evidence IDs, CONTST names, four ads, destinations and Post ID placeholders. Do not use Cadian facts in universal examples.

- [ ] **Step 2: Update public documentation and legacy adapter**

Declare 0.3.0, describe the coordinate/test distinction, eleven artefacts, manual launch workflow and migration warning for v0.2 brand folders.

- [ ] **Step 3: Build the universal bundle**

```bash
python3 scripts/build-knowledge-bundle.py
```

- [ ] **Step 4: Run the complete automated gate**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/validate-package.py .
git diff --check
```

- [ ] **Step 5: Commit**

```bash
git add examples README.md VERSION config tests
git commit -m "feat: release portable strategist v0.3"
```

### Task 7: behavioral verification, review and publication

**Files:**
- Modify: only files required by observed forward-test failures.

**Interfaces:**
- Consumes: completed v0.3 package and one isolated fictional brand folder.
- Produces: independent evidence that the skill follows the canonical method across realistic requests.

- [ ] **Step 1: Re-run the three baseline scenarios with v0.3**

Expected: Who x Problem coordinate, four awareness ads, no standard MWA ad, new CONTST for ITR, locked names, ABO, $50/$100 and five days.

- [ ] **Step 2: Run an independent package review**

Check strategy compliance, cross-file drift, security, brand isolation and portability. Fix only evidenced defects through failing tests.

- [ ] **Step 3: Build a temporary brand folder and both bundles**

Verify no template tokens, no credentials, correct safe registers and deterministic output.

- [ ] **Step 4: Run the final release gate on the exact committed tree**

Run all tests, validator, universal bundle, temporary brand bundle, `git diff --check` and clean-status checks.

- [ ] **Step 5: Merge to main and push**

The user has already selected merge and GitHub publication. Fast-forward or merge the verified branch into `main`, re-run the gate on `main`, then push `main` to `origin` without force.
