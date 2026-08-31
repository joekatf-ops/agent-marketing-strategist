# Ad Analysis Harness v0.4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Release a portable ad-analysis harness that turns one selected brand, supplied creative assets and optional manual Meta data into a governed Creative Audit or Performance Diagnosis with safe proposed persistence.

**Architecture:** A provider-neutral JSON intake and two standard-library Python commands create and validate analysis runs under the active brand folder. The strategist routes creative-only requests to a new Creative Audit contract and adequate performance packs to the existing Ad Diagnosis contract; run outputs are writable, while test, winner and revision memory remain human-confirmed controlled records.

**Tech Stack:** Markdown skill package, Python 3 standard library, JSON and JSON Schema, unittest.

**Spec:** `docs/superpowers/specs/2026-08-27-ad-analysis-harness-design.md`

## Global Constraints

- Target release is exactly `0.4.0`.
- No live Meta reporting, publishing, budget changes or automated account mutations.
- Exactly one brand folder, market and product are active in a run.
- Creative Audit never assigns `keep`, `ITR`, `stop` or `scale` and never predicts performance.
- Performance Diagnosis retains the existing read-validity rules and exactly one top-level action per reviewed item.
- Raw assets, exports and analysis outputs never enter a generated brand bundle.
- A diagnosis may propose ITR but never reserves a CONTST until the human chooses to build it.
- Test-register, winner-library and approved-revision writes require explicit human confirmation.
- Scripts use the Python standard library only, perform no network calls and never follow symlinks.
- Connected and upload-only runtimes use the same versioned intake shape.
- `SKILL.md` and `AGENTS.md` operating bodies remain byte-identical.

---

### Task 1: Define v0.4 package and behavioral acceptance

**Files:**
- Modify: `tests/test_package_integrity.py`
- Modify: `tests/test_init_brand_folder.py`
- Create: `tests/test_ad_analysis_harness.py`
- Modify: `scripts/validate-package.py`

**Interfaces:**
- Consumes: existing `validate(root: pathlib.Path) -> list[str]`.
- Produces: v0.4 package drift checks and import helpers for the future `ad_analysis_harness` module.

- [ ] **Step 1: Add package-level v0.4 expectations**

Add tests that expect `VERSION` to be `0.4.0`, twelve governed artefacts and these routed files:

```python
required = {
    "contracts/creative-audit.md",
    "references/19-ad-analysis-harness.md",
    "schemas/ad-analysis-intake.schema.json",
    "examples/ad-analysis-intake.json",
    "examples/creative-audit.md",
    "examples/ad-diagnosis.md",
}
self.assertEqual(set(), {path for path in required if not (ROOT / path).is_file()})
```

Require all three entrypoints to contain the Creative Audit versus Performance Diagnosis router and
the phrases `input audit`, `no performance prediction`, `human confirmation` and `does not reserve`
in the applicable sections.

- [ ] **Step 2: Add behavioral contract assertions**

Add tests that require Creative Audit to use only `ready`, `revise` or `block`, prohibit the four
performance actions, and require Ad Diagnosis to continue using only `keep`, `ITR`, `stop` or
`scale`.

```python
creative = (ROOT / "contracts/creative-audit.md").read_text()
for outcome in ("ready", "revise", "block"):
    self.assertIn(f"`{outcome}`", creative)
for action in ("keep", "ITR", "stop", "scale"):
    self.assertNotIn(f"Top-level action: `{action}`", creative)
```

- [ ] **Step 3: Define script test helpers and RED cases**

In `tests/test_ad_analysis_harness.py`, add a fixture that initialises a temporary brand and attempts
to load:

```python
MODULE = ROOT / "scripts" / "ad_analysis_harness.py"

def load_harness():
    if not MODULE.exists():
        raise AssertionError("scripts/ad_analysis_harness.py should exist")
```

Add RED tests for run creation, no-overwrite behavior, run ID sequencing, creative readiness,
performance readiness, cross-brand rejection, symlink rejection and deterministic input-audit text.

- [ ] **Step 4: Run focused tests and retain RED evidence**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_package_integrity \
  tests.test_init_brand_folder \
  tests.test_ad_analysis_harness -v
```

Expected: failures for missing v0.4 files, old version, missing scripts and absent analysis-output
scaffolding. Record which failures belong to Tasks 2 to 6.

- [ ] **Step 5: Add minimal v0.4 validator requirements**

Extend the validator required-file list and version check. Add semantic mutation checks that reject:

```text
Creative Audit predicts winning performance.
Performance data is optional for a keep, ITR, stop or scale decision.
Diagnosis automatically reserves the next CONTST.
```

Keep the live package RED until later tasks provide the required files.

- [ ] **Step 6: Commit**

```bash
git add tests scripts/validate-package.py
git commit -m "test: define v0.4 ad analysis acceptance"
```

### Task 2: Build the run initializer and intake schema

**Files:**
- Create: `schemas/ad-analysis-intake.schema.json`
- Create: `scripts/ad_analysis_harness.py`
- Create: `scripts/init-ad-analysis-run.py`
- Create: `templates/brand-folder/outputs/ad-analysis/README.md`
- Modify: `templates/brand-folder/outputs/README.md`
- Modify: `tests/test_ad_analysis_harness.py`
- Modify: `tests/test_init_brand_folder.py`

**Interfaces:**
- Produces: `initialise_run(brand_folder, mode, product_id, market, run_id=None, today=None) -> pathlib.Path`.
- Produces: `load_intake(run_folder: pathlib.Path) -> dict[str, object]`.
- Produces: JSON run manifests at `outputs/ad-analysis/ADR-YYYYMMDD-###/intake.json`.

- [ ] **Step 1: Write exact initializer tests**

Cover generated and explicit run IDs:

```python
run = harness.initialise_run(
    brand_folder=brand,
    mode="creative-audit",
    product_id="sleep-mask",
    market="AU",
    today=dt.date(2026, 8, 27),
)
self.assertEqual("ADR-20260827-001", run.name)
self.assertEqual("acme-sleep", json.loads((run / "intake.json").read_text())["brand_slug"])
```

Require the second run to end `002`, invalid modes and IDs to raise `ValueError`, and an existing
non-empty run to raise `FileExistsError`. Require every created run to contain only `intake.json`
and `README.md`.

- [ ] **Step 2: Run initializer tests and verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_initialises_sequential_run \
  tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_refuses_existing_or_invalid_run -v
```

Expected: FAIL because the module and initializer do not exist.

- [ ] **Step 3: Implement the shared constants and brand loader**

In `ad_analysis_harness.py`, define:

```python
MODES = {"creative-audit", "performance-diagnosis"}
RUN_ID = re.compile(r"^ADR-(?P<date>\d{8})-(?P<number>\d{3})$")

def load_brand_identity(brand_folder: pathlib.Path) -> dict[str, str]:
    """Return brand_slug and method_version from a validated local brand.yml."""
```

Reject missing manifests, symlinked brand folders, malformed or duplicate identity fields and
method versions older than `0.4.0` for controlled writes. Initial run creation may report an older
folder as migration-needed rather than silently changing it.

- [ ] **Step 4: Implement `initialise_run`**

Write the JSON skeleton with stable key order and this top-level shape:

```json
{
  "schema_version": 1,
  "run_id": "ADR-20260827-001",
  "mode": "creative-audit",
  "brand_slug": "acme-sleep",
  "method_version": "0.4.0",
  "market": "AU",
  "product_id": "sleep-mask",
  "account_timezone": "",
  "requester": "",
  "requested_at": "2026-08-27",
  "ads": [],
  "sources": [],
  "performance": null,
  "known_limitations": []
}
```

Use `json.dumps(..., indent=2, ensure_ascii=False) + "\n"`. Create no asset files and no controlled
strategy state. Copy the deterministic run instructions from the template into `README.md` and
include the exact validation command for the created run.

- [ ] **Step 5: Add the CLI wrapper**

`init-ad-analysis-run.py` accepts brand folder, `--mode`, `--product-id`, `--market` and optional
`--run-id`. It prints only the created run path on success and returns non-zero with an actionable
message on validation failure.

- [ ] **Step 6: Add schema and template instructions**

The JSON Schema must use `additionalProperties: false`, define the two modes and define reusable
source and ad objects. The new template README states that raw assets and exports may be placed or
referenced in the run folder but are excluded from brand bundles.

- [ ] **Step 7: Run focused and initializer tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_ad_analysis_harness \
  tests.test_init_brand_folder -v
```

Expected: initializer tests pass; validation cases remain RED until Task 3.

- [ ] **Step 8: Commit**

```bash
git add schemas scripts templates tests
git commit -m "feat: initialise portable ad analysis runs"
```

### Task 3: Validate analysis intake and generate the input audit

**Files:**
- Modify: `scripts/ad_analysis_harness.py`
- Create: `scripts/validate-ad-analysis-run.py`
- Modify: `tests/test_ad_analysis_harness.py`

**Interfaces:**
- Produces: immutable `ValidationResult(status, errors, limitations, inventory)`.
- Produces: `validate_run(brand_folder, run_folder) -> ValidationResult`.
- Produces: `render_input_audit(intake, result) -> str`.
- Produces: `validate-ad-analysis-run.py BRAND RUN [--write-audit]`.

- [ ] **Step 1: Write creative-readiness tests**

Use source records with IDs and kinds:

```json
{"source_id":"SRC-001","kind":"attachment","label":"ad-one.mp4","location":"attached:ad-one.mp4","sha256":null}
```

Require Creative Audit to be:

- `blocked` when no ads or an ad has no identity/asset source;
- `limited` when assets exist but copy, destination or traceability is missing;
- `ready` when every ad has the asset, copy, destination and strategic traceability fields.

- [ ] **Step 2: Write performance-readiness tests**

Require `blocked` when any of these is missing: performance sources, date range, attribution,
currency, aggregation level, ad/spend/purchase field mappings or mapping for every spend-bearing ad.

Require optional funnel and video-field gaps to produce `limited`, not `blocked`.

- [ ] **Step 3: Write security and identity tests**

Prove the validator rejects duplicate source IDs, duplicate ad IDs, unknown source references,
cross-brand intake, `..` traversal, absolute file paths without an explicit attachment label,
symlinks, URLs masquerading as files and unknown JSON keys.

- [ ] **Step 4: Run validation tests and verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ad_analysis_harness -v
```

Expected: validation tests fail because `ValidationResult`, `validate_run` and audit rendering do
not exist.

- [ ] **Step 5: Implement strict JSON shape validation**

Use standard-library type checks rather than a third-party JSON Schema package. Define stable error
paths such as:

```text
ads[0].asset_source_ids must contain at least one source ID
performance.field_mapping.purchases is required
intake brand other-brand does not match manifest brand acme-sleep
```

Do not coerce strings, numbers or enum values silently.

- [ ] **Step 6: Implement local-source safety**

For `kind: file`, resolve a relative location against the run folder, require the result to stay
inside the brand folder, require a regular non-symlink file and calculate a SHA-256 when one was not
provided. `attachment`, `url`, `screenshot` and `table` remain labelled external sources and do not
authorize file reads or network calls.

- [ ] **Step 7: Implement deterministic readiness and audit rendering**

Return sorted error and limitation tuples. Render these sections in order:

```markdown
# Ad analysis input audit
## Run identity
## Source inventory
## Ad coverage
## Performance coverage
## Readiness
## Errors
## Limitations
```

The CLI prints the status and issues. With `--write-audit`, it writes `input-audit.md` without
modifying intake or strategy records.

- [ ] **Step 8: Run focused and full tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ad_analysis_harness -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

- [ ] **Step 9: Commit**

```bash
git add scripts tests
git commit -m "feat: validate ad analysis intake"
```

### Task 4: Add Creative Audit and mode routing

**Files:**
- Create: `contracts/creative-audit.md`
- Create: `references/19-ad-analysis-harness.md`
- Modify: `SKILL.md`
- Modify: `AGENTS.md`
- Modify: `PROMPT.md`
- Modify: `OUTPUT-CONTRACT.md`
- Create: `examples/ad-analysis-intake.json`
- Create: `examples/creative-audit.md`
- Modify: `scripts/validate-package.py`
- Modify: `tests/test_package_integrity.py`

**Interfaces:**
- Consumes: a validator status and input audit from Task 3.
- Produces: the twelfth governed artefact and one shared entrypoint router.

- [ ] **Step 1: Strengthen RED tests for the router and contract**

Require every entrypoint to make these decisions:

```text
no adequate performance data -> Creative Audit
adequate performance data -> Ad Diagnosis
competitor ad -> competitor research
human edit -> Learning Update
```

Require the Creative Audit outcome field to contain exactly one of `ready`, `revise` or `block`.

- [ ] **Step 2: Run the focused package tests and verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_package_integrity.PackageIntegrityTests.test_analysis_mode_router \
  tests.test_package_integrity.PackageIntegrityTests.test_creative_audit_has_no_performance_decisions -v
```

- [ ] **Step 3: Write the Creative Audit contract**

Use the eleven ordered sections from the spec. Its fixed outcome row is:

```markdown
| Ad | Outcome | Blocking or revision issue | Evidence | Exact change | Owner |
|---|---|---|---|---|---|
```

State explicitly that absent metrics prohibit claims about winning, conversion, CAC or scaling.

- [ ] **Step 4: Write the harness reference**

Document mode selection, intake workflow, attachment handling, the run folder, readiness states,
output filenames and Persistence Summary. Keep schema field detail in the JSON Schema rather than
duplicating it.

- [ ] **Step 5: Update all three entrypoints**

Add one `Analyse supplied ads` route to the mode table and a concise `Ad-analysis routing` section.
Keep `SKILL.md` and `AGENTS.md` identical after frontmatter removal. In upload mode, require
`intake.json`, the universal bundle, the selected brand bundle and referenced attachments.

- [ ] **Step 6: Create one complete frozen Creative Audit example**

Use a new fictional brand and at least two ads: one ready and one revise. Every fact must map to the
frozen intake. Include no performance metrics and no `keep`, `ITR`, `stop` or `scale` decision.

- [ ] **Step 7: Extend semantic validation**

Make package validation reject positive performance predictions in the Creative Audit contract or
example and reject entrypoint text that allows Creative Audit to assign performance actions.

- [ ] **Step 8: Run focused and full tests**

- [ ] **Step 9: Commit**

```bash
git add contracts references SKILL.md AGENTS.md PROMPT.md OUTPUT-CONTRACT.md examples scripts tests
git commit -m "feat: add governed creative audit mode"
```

### Task 5: Integrate Performance Diagnosis and safe persistence handoff

**Files:**
- Modify: `contracts/ad-diagnosis.md`
- Modify: `references/09-testing-and-diagnosis.md`
- Modify: `references/14-learning-system.md`
- Modify: `references/19-ad-analysis-harness.md`
- Create: `examples/ad-diagnosis.md`
- Modify: `templates/brand-folder/outputs/ad-analysis/README.md`
- Modify: `tests/test_package_integrity.py`
- Modify: `tests/test_ad_analysis_harness.py`

**Interfaces:**
- Consumes: ready or limited Performance Diagnosis intake.
- Produces: `diagnosis.md`, optional `test-register-patch.yml`, optional `next-brief.md` and `persistence-summary.md`.
- Does not produce: direct controlled-register mutation.

- [ ] **Step 1: Add persistence-boundary tests**

Require the diagnosis contract and harness reference to say:

```text
recommend ITR != reserve CONTST
proposed test observation != approved revision learning
winner graduation requires real Post ID and confirmation
upload-only output is a patch, not persistence
```

Add a package mutation test that rejects `Diagnosis automatically increments next_test_number`.

- [ ] **Step 2: Add a frozen Performance Diagnosis test pack**

The example must cover five full days, every spend-bearing ad, at least one missing optional creative
metric, one Direction or Too early classification where justified, cautious explanation language and
exactly one governed action for every reviewed item.

- [ ] **Step 3: Run focused tests and verify RED**

- [ ] **Step 4: Update Ad Diagnosis input and output rules**

Require the run ID, intake path, validator status and input-audit path in Section 1. Add the
Persistence Summary after the eleven governed diagnosis sections without changing the fixed
top-level action field.

- [ ] **Step 5: Define proposed persistence files**

`test-register-patch.yml` may contain only matching existing test observations, supplied results,
confidence, verdict and next action. It must not contain a new test ID. `next-brief.md` may describe
an ITR but must display `CONTST: unreserved, human decision required`.

- [ ] **Step 6: Clarify learning separation**

Performance observations remain in test memory. Approved changes to copy, claims or voice continue
through `contracts/learning-update.md`. A diagnosis report never promotes either class automatically.

- [ ] **Step 7: Run harness, package and full tests**

- [ ] **Step 8: Commit**

```bash
git add contracts references examples templates tests
git commit -m "feat: connect diagnosis to safe retained learning"
```

### Task 6: Complete runtime portability and release packaging

**Files:**
- Modify: `connectors/runtime-codex.md`
- Modify: `connectors/runtime-claude.md`
- Modify: `connectors/runtime-claude-code.md`
- Modify: `connectors/runtime-chatgpt.md`
- Modify: `connectors/runtime-gemini.md`
- Modify: `connectors/runtime-grok.md`
- Modify: `connectors/runtime-grok-agents.md`
- Modify: `references/17-runtime-portability.md`
- Modify: `README.md`
- Modify: `VERSION`
- Modify: `scripts/build-knowledge-bundle.py` only if current globs omit a routed file.
- Modify: `tests/test_package_integrity.py`
- Modify: `tests/test_build_brand_bundle.py`

**Interfaces:**
- Consumes: the complete v0.4 harness.
- Produces: documented connected-folder and upload-only workflows plus a reproducible universal bundle.

- [ ] **Step 1: Add release and portability RED tests**

Require version `0.4.0`, twelve artefacts, both commands, all seven runtime guides and universal
bundle inclusion of the new contract, reference and schema guidance. Prove brand bundles do not
include `outputs/ad-analysis/`, raw assets, CSV files or analysis run JSON.

- [ ] **Step 2: Run focused tests and verify RED**

- [ ] **Step 3: Update every runtime guide**

Connected runtimes create/validate a run and write the governed report. Upload runtimes attach
`intake.json`, the two bundles and all referenced files, then return persistence patches. No guide
claims a connector is active without preflight.

- [ ] **Step 4: Update public documentation**

README must show the simple request, both analysis modes, required inputs, run commands, output
locations, persistence boundary and v0.3-to-v0.4 migration. Existing v0.3 brand folders add only the
analysis-output directory and change `method_version` after review; no evidence or strategy history
is rewritten.

- [ ] **Step 5: Build the universal bundle**

Run:

```bash
python3 scripts/build-knowledge-bundle.py
```

Confirm it includes the new universal contract/reference but no temporary analysis run.

- [ ] **Step 6: Run the complete automated gate**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/validate-package.py .
git diff --check
```

- [ ] **Step 7: Commit**

```bash
git add connectors references/17-runtime-portability.md README.md VERSION scripts tests
git commit -m "feat: release portable ad analysis harness v0.4"
```

### Task 7: Independent behavioral verification, local installation and publication

**Files:**
- Modify: only files required by observed forward-test failures.
- External fast-forward after publication: `/Users/joekatf/.codex/skills/agent-marketing-strategist`.

**Interfaces:**
- Consumes: the committed v0.4 release candidate.
- Produces: independent GO evidence, published GitHub `main` and a matching installed Codex checkout.

- [ ] **Step 1: Run isolated forward scenarios**

Use a temporary fictional brand and verify:

1. assets without metrics route to Creative Audit and contain no performance prediction;
2. incomplete performance intake blocks with exact missing fields;
3. fewer than five full days returns Too early;
4. a complete pack analyses every spend-bearing ad with exactly one action each;
5. an ITR recommendation leaves CONTST unreserved;
6. an upload-only simulation returns patches without claiming persistence.

- [ ] **Step 2: Run independent whole-branch review**

Check spec compliance, routing drift, brand isolation, path and symlink safety, secret handling,
bundle exclusion, controlled writes, cross-runtime instructions and installed-skill migration.
Fix only reproduced defects through failing tests.

- [ ] **Step 3: Run the exact committed-tree release gate**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/validate-package.py .
python3 scripts/build-knowledge-bundle.py
git diff --check
git status --porcelain=v1 --untracked-files=all
```

Initialise one fresh brand, create and validate both run modes, build two identical brand bundles
and confirm neither contains analysis outputs, raw files, cross-brand state or credentials.

- [ ] **Step 4: Merge and push**

Fetch `origin`, confirm `origin/main` is an ancestor of the reviewed branch, fast-forward `main`,
rerun the release gate on `main` and push without force.

- [ ] **Step 5: Refresh the installed Codex skill**

After GitHub publication, request filesystem/network approval and run:

```bash
git -C /Users/joekatf/.codex/skills/agent-marketing-strategist pull --ff-only origin main
```

Verify the installed `VERSION`, commit, `SKILL.md` and routed files match published `main`. Do not
overwrite local changes; a dirty installed checkout is a stop condition.

- [ ] **Step 6: Report release evidence**

Report GitHub commit, version, test total, validation, bundle determinism, forward-test verdict,
installed-skill commit and the explicit residual limit that live Meta/runtime authentication was not
performed.
