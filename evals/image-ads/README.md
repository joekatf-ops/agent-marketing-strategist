# Image-ad behavioral evaluation

Cases use fictional evaluation inputs unless explicitly supplied as live assets.
The portable cases in `cases.json` can be run in any LLM, from `PROMPT.md` alone or the image
bundle. Give the model only the selected user request, context and capabilities. Keep the evaluation
criteria out of its input. Save the actual response, model/runtime, date and package version.

Evaluate observable behavior: correct guided/direct routing, retained selections, supported facts,
appropriate format, requested ratios, no unnecessary research intake, no fabricated visual inspection
and honest rendering status. New concepts now begin with a creative choice unless delegated or
already specified. Historical v1.1 expectations below describe that release, not the current default.
Check actual pixels when a generator is used. Different wording is expected.

`guided-cases.json` covers v1.8 routing and selection continuity. Supply only each case's `input`
and the named skill entrypoint, with generation and external writes disabled. Evaluate the actual
response against `expected` afterwards, without providing those criteria to the test agent.

The existing `evals/run.py` remains the Anthropic hook-writing runner. It is not a multi-provider
image test. Image cases can be executed manually in other hosts without an API-specific harness.

## Evidence in v1.1

`forward-test-2026-09-10.md` records an independent Codex subagent pass using the working skill in
a text-only environment. Two raw requests were supplied without target answers. Two further requests used only PROMPT.md,
covering optional customer-question input and an owner-corrected product offer. The evaluator
produced usable square briefs without asking for research, photos or a belief map, and did not claim
generation or inspection of an inaccessible reference. This is a bounded instruction-following check,
not a provider comparison or proof of advertising performance.

Automated tests measure PNG/JPEG/WebP headers, reject non-square results, detect fabricated completion
records, preserve visual reference annotations during sync and keep unreviewed swipe annotations
out of teaching. A header check cannot prove complete decodability, text accuracy or product fidelity;
actual visual inspection remains required.

Paid live rendering, broad cross-LLM evaluation and advertising outcomes were not tested in this
implementation. Run the same cases in the desired host and model before claiming those capabilities
have been validated end to end.
