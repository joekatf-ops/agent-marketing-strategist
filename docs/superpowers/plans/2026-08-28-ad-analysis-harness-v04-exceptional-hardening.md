# Ad Analysis Harness v0.4 Exceptional Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. The authorizing brief forbids subagents for this task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the four load-bearing v0.4 publication and contract-parity residuals, correct the frozen diagnosis wording, and produce committed release evidence for controller-held publication.

**Architecture:** Keep the existing public harness API unchanged. Make the portable intake contract the combination of the standard JSON Schema and an explicit declarative conformance artifact for identity, uniqueness, cross-reference, and date-order rules that JSON Schema cannot express portably. Keep staging descriptors open through both file-publication transactions and verify destination inode and bytes after replacement. Publish run directories only through platform-native exclusive rename calls reached through `ctypes`.

**Tech Stack:** Python 3 standard library, `unittest`, JSON Schema draft 2020-12 documents, POSIX descriptor-relative filesystem operations, Darwin `renameatx_np(..., RENAME_EXCL)` and Linux `renameat2(..., RENAME_NOREPLACE)` through `ctypes`.

**Spec:** `.superpowers/sdd/2026-08-27-ad-analysis-harness-v04/exceptional-final-hardening-brief.md`

## Global Constraints

- Work only in `/Users/joekatf/JOEKA/agent-marketing-strategist/.worktrees/v04-implementation` from base `d90874ccc322b3c8a984a274f96ac32fa4b50b71`.
- Use strict RED/GREEN TDD and record the exact command and observed result for every behavior.
- Preserve standard-library-only, non-network runtime behavior and the exact six-name public harness API.
- Preserve v0.3 migration behavior, brand isolation, controlled-write boundaries, and distinct readiness, outcome, and action vocabularies.
- Do not merge, push, modify the installed skill, authenticate connectors, or touch Meta.
- Keep failed publication paths free of unverified bytes; unsupported no-replace primitives fail closed.

---

### Task 1: Portable schema and Python parity

**Files:**
- Create: `schemas/ad-analysis-intake.conformance.json`
- Modify: `schemas/ad-analysis-intake.schema.json`
- Modify: `tests/fixtures/ad-analysis-intake-conformance.json`
- Modify: `tests/test_ad_analysis_harness.py`
- Modify: `scripts/ad_analysis_harness.py`
- Modify: `references/19-ad-analysis-harness.md`

**Interfaces:**
- Consumes: `json_schema_errors(instance, schema)` and the existing `validate_run(brand_folder, run_folder)` behavior.
- Produces: a standard-schema result plus declarative conformance rule IDs for run validity/context, brand/method context, unique source/ad identifiers, known source/ad references, and ordered performance dates. No new public Python callable is added.

- [ ] **Step 1: Expand the shared corpus and executable portable evaluator**

Add literal corpus cases for the required, allow-empty, and nullable text classes; invalid dates and run IDs; reversed ranges; duplicate IDs/references; unknown references; all Performance Diagnosis required fields; and Creative Audit partial-performance behavior. Extend the test helper to interpret only the declared rule operations in `ad-analysis-intake.conformance.json`, then assert base-schema expectations, schema-plus-conformance validity, and Python validity independently.

- [ ] **Step 2: Run the parity test to verify RED**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_shared_schema_python_conformance_corpus -v`

Expected: failures showing the base schema accepts Python-rejected text/run/reference cases and the governed conformance artifact is absent.

- [ ] **Step 3: Implement the minimum parity changes**

Define reusable `requiredText`, `singleLineText`, and `nullableText` schema classes; apply them to every matching field; keep Creative Audit optional performance shapes no stricter than Python; and make non-null ad text use the same trimmed, single-line rule in Python. Create the conformance artifact with exact machine-readable rule operations and document that portable consumers MUST apply the JSON Schema, format assertions, and the conformance rules together.

- [ ] **Step 4: Run focused GREEN and regression suites**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_shared_schema_python_conformance_corpus tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_marks_complete_creative_inputs_ready tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_marks_complete_performance_inputs_ready -v`

Expected: all selected tests pass.

- [ ] **Step 5: Commit**

Run: `git add schemas/ad-analysis-intake.schema.json schemas/ad-analysis-intake.conformance.json tests/fixtures/ad-analysis-intake-conformance.json tests/test_ad_analysis_harness.py scripts/ad_analysis_harness.py references/19-ad-analysis-harness.md docs/superpowers/plans/2026-08-28-ad-analysis-harness-v04-exceptional-hardening.md && git commit -m "fix: complete portable intake conformance"`

---

### Task 2: Brand-bundle substitution-safe publication

**Files:**
- Modify: `tests/test_build_brand_bundle.py`
- Modify: `scripts/build-brand-bundle.py`

**Interfaces:**
- Consumes: `_publish_bundle(output: pathlib.Path, content: bytes) -> None`.
- Produces: retained staging descriptor verification through replacement and fail-closed removal of any destination not proven to be that descriptor with exactly `content` bytes.

- [ ] **Step 1: Add the syscall-boundary substitution regression**

Patch `os.replace` in the test so it unlinks the verified staging pathname, installs a regular single-link attacker file at that name, and then performs the real replacement. Assert `build_bundle` raises and that the destination is absent or contains only previously verified safe bytes, never attacker bytes.

- [ ] **Step 2: Run the regression to verify RED**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_build_brand_bundle.BrandBundleTests.test_staging_substitution_never_leaves_unverified_bundle_bytes -v`

Expected: failure because attacker bytes remain at the output after the current post-replace identity error.

- [ ] **Step 3: Retain and verify the descriptor through publication**

Open staging read/write, keep it open through `os.replace`, compare the published destination to `os.fstat(staging_descriptor)`, read the retained descriptor back, verify exact bytes and stable metadata, and remove an unexpected replacement destination before propagating failure. Preserve a verified unchanged prior destination when replacement never occurred.

- [ ] **Step 4: Run focused GREEN**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_build_brand_bundle -v`

Expected: the complete brand-bundle suite passes.

- [ ] **Step 5: Commit**

Run: `git add scripts/build-brand-bundle.py tests/test_build_brand_bundle.py && git commit -m "fix: bind brand bundle publication to staged bytes"`

---

### Task 3: Audit substitution-safe publication

**Files:**
- Modify: `tests/test_ad_analysis_harness.py`
- Modify: `scripts/validate-ad-analysis-run.py`

**Interfaces:**
- Consumes: `_write_input_audit(path: pathlib.Path, content: str, *, session=None) -> None`.
- Produces: unpredictable private staging names, a staging descriptor retained through replacement, exact inode/byte verification, and fail-closed destination cleanup on mismatch.

- [ ] **Step 1: Add the observable CLI substitution regression**

Patch validator `os.replace` so a regular single-link attacker audit replaces the verified staging pathname in the final window. Invoke `main()` with `--write-audit`; assert return code 1 and no attacker audit remains at `input-audit.md`.

- [ ] **Step 2: Run the regression to verify RED**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_validator_rejects_staging_substitution_without_publishing_unrelated_audit -v`

Expected: failure because the CLI returns success or leaves attacker bytes published.

- [ ] **Step 3: Implement retained-descriptor audit publication**

Use `secrets.token_hex` for each candidate name, write through `os.write` to an `O_RDWR|O_EXCL|O_NOFOLLOW` descriptor, retain it through final session/destination/path checks and replacement, then prove destination inode and exact encoded bytes match the descriptor. Remove an unverified destination and sync the run directory before raising.

- [ ] **Step 4: Run focused GREEN**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_validator_rejects_staging_substitution_without_publishing_unrelated_audit tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_validator_cli_prints_issues_and_writes_only_the_input_audit tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_validator_cli_refuses_a_symlinked_audit_target tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_validator_cli_refuses_a_hardlinked_audit_target -v`

Expected: all selected tests pass.

- [ ] **Step 5: Commit**

Run: `git add scripts/validate-ad-analysis-run.py tests/test_ad_analysis_harness.py && git commit -m "fix: bind audit publication to validated bytes"`

---

### Task 4: Atomic no-replace run publication

**Files:**
- Modify: `tests/test_ad_analysis_harness.py`
- Modify: `scripts/ad_analysis_harness.py`

**Interfaces:**
- Consumes: sibling staging and destination names plus the open analysis-directory descriptor.
- Produces: `_rename_directory_no_replace(directory_descriptor: int, source: str, destination: str) -> None`, using Darwin `renameatx_np` with `RENAME_EXCL` or Linux `renameat2` with `RENAME_NOREPLACE`; other platforms and absent symbols raise `OSError` without calling ordinary rename.

- [ ] **Step 1: Add real empty-directory collision and unsupported-platform regressions**

Create an empty destination inside a wrapper invoked immediately before the production publication call. Assert automatic IDs preserve the empty collision and publish the next sequence, explicit IDs raise `FileExistsError`, and a missing native primitive leaves staging cleaned without calling `os.rename`.

- [ ] **Step 2: Run the regressions to verify RED**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_automatic_run_id_retries_after_a_concurrent_empty_directory_publication tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_explicit_run_id_refuses_a_concurrent_empty_directory_publication tests.test_ad_analysis_harness.AdAnalysisHarnessTests.test_run_publication_fails_closed_without_native_no_replace -v`

Expected: current ordinary rename replaces the empty destination, and the native helper is absent.

- [ ] **Step 3: Implement the native exclusive rename helper**

Load the process C library with `ctypes.CDLL(None, use_errno=True)`, declare exact argument/restype signatures, pass descriptor-relative byte names, translate nonzero returns using `ctypes.get_errno()`, and use only `FileExistsError` to retry automatic IDs. Explicit collisions become `FileExistsError`; ENOSYS, missing symbols, and unsupported platforms remain fail-closed `OSError` values.

- [ ] **Step 4: Run focused GREEN and full harness suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_ad_analysis_harness -v`

Expected: the complete harness suite passes on the current supported platform.

- [ ] **Step 5: Commit**

Run: `git add scripts/ad_analysis_harness.py tests/test_ad_analysis_harness.py && git commit -m "fix: publish analysis runs without replacement"`

---

### Task 5: Frozen report correction and final evidence

**Files:**
- Modify: `tests/test_package_integrity.py`
- Modify: `examples/ad-diagnosis.md`
- Modify: `.superpowers/sdd/2026-08-27-ad-analysis-harness-v04/progress.md`
- Create: `.superpowers/sdd/2026-08-27-ad-analysis-harness-v04/exceptional-final-hardening-report.md`
- Modify: `.superpowers/sdd/2026-08-27-ad-analysis-harness-v04/task-7-report.md`
- Modify: `.superpowers/sdd/2026-08-27-ad-analysis-harness-v04/final-fix-report.md`

**Interfaces:**
- Consumes: the frozen diagnosis intake's three `performance.account_norms` and `reference_ranges.status == "unavailable"`.
- Produces: report language that names supplied account norms and separately states external reference ranges are unavailable, plus exact committed-tree and fresh-archive release evidence.

- [ ] **Step 1: Add and run the frozen-report RED assertion**

Add a test that derives the account-norm count and reference-range state from the frozen intake, then requires the report to state both facts without claiming account norms are absent.

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_package_integrity.PackageIntegrityTests.test_frozen_diagnosis_distinguishes_account_norms_from_external_reference_ranges -v`

Expected: failure on the current `No account norms were supplied` sentence.

- [ ] **Step 2: Correct the report and run GREEN**

Replace the two false absence claims with wording that identifies the three supplied account norms and only marks external reference ranges unavailable.

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_package_integrity.PackageIntegrityTests.test_frozen_diagnosis_distinguishes_account_norms_from_external_reference_ranges tests.test_package_integrity.PackageIntegrityTests.test_frozen_diagnosis_traces_classifications_and_action_thresholds -v`

Expected: both tests pass.

- [ ] **Step 3: Commit the governed report correction**

Run: `git add examples/ad-diagnosis.md tests/test_package_integrity.py && git commit -m "docs: distinguish diagnosis benchmark sources"`

- [ ] **Step 4: Run every required release gate from committed code and a fresh archive**

Run focused suites, `python3 -m unittest discover -s tests -v`, `python3 scripts/validate-package.py .`, two universal builds with SHA-256 comparison, `.superpowers/sdd/2026-08-27-ad-analysis-harness-v04/final_release_verify.py` for a new fictional brand, brand double-build/exclusion checks, `git diff --check`, and clean tracked/untracked porcelain. Repeat the full suite, package validation, universal double-build, and fresh-brand script from `git archive HEAD` extraction.

- [ ] **Step 5: Write and commit exact handoff evidence**

Append every RED/GREEN command/result, final HEAD, total test count, both bundle hashes, archive evidence, and the unchanged live Meta/connector/cross-model limits to the exceptional report, Task 7 report, final-fix report, and progress ledger.

Run: `git add .superpowers/sdd/2026-08-27-ad-analysis-harness-v04/progress.md .superpowers/sdd/2026-08-27-ad-analysis-harness-v04/exceptional-final-hardening-report.md .superpowers/sdd/2026-08-27-ad-analysis-harness-v04/task-7-report.md .superpowers/sdd/2026-08-27-ad-analysis-harness-v04/final-fix-report.md && git commit -m "docs: record exceptional hardening evidence"`

- [ ] **Step 6: Verify final committed state**

Run the full suite, package validation, universal double-build hash comparison, fresh-brand dual-mode and brand-bundle verification, `git diff --check`, `git diff HEAD --exit-code`, and `git status --porcelain=v1 --untracked-files=all` again from final HEAD. Extract a new final archive and repeat the archive gates so report-only changes are included in the evidence.

Expected: all commands exit 0; the two universal hashes match, the two brand hashes match, and porcelain is empty.
