# Release validation: 1.8.0

Date: 2026-09-17

## Change and scope

New image concepts now use guided creative choices. Approved briefs, revisions and explicitly
delegated creation retain direct production. The change is implemented in the skill entrypoint,
working core, image workflow, production contract, connector handoff and portable prompt. The image
bundle includes the complete guided procedure. All portable editions are rebuilt from source.

The workflow preserves supplied decisions, uses concrete reference roles and actual font sources,
checks real outputs and saves the final creative record. It does not import private brand assets
or depend on an independently installed image-ad skill. Research remains optional.

## Validation

- 250 unit tests passed.
- Package validation and skill frontmatter validation passed.
- Generated AGENTS.md and all three portable bundles match their sources.
- Copy lexicon check passed, and the example image-run record remains valid.
- Image bundle is 89,713 bytes, within the existing 90,000-byte limit. It retains the complete
  guided workflow and writing method while omitting duplicated planning summaries. The complete
  source references remain in the repository and knowledge bundle.
- Five independent-agent behavioural scenarios passed the documented criteria. The portable case
  was repeated after the final bundle change. See the [actual responses and limits](../evals/image-ads/forward-test-2026-09-17.md).
- The installed previous release was compared against the repository baseline before replacement;
  no locally modified tracked files were found.

An initial bundle-size check failed and was resolved by reducing duplicate export content, without
raising the limit. The whole test suite then passed. Existing instruction conflicts about automatic
creative selection and concept approvals were revised at their entry points, not merely supplemented.

No live image generation, multi-provider visual comparison or advertising-performance experiment
was part of this release validation. Visual quality still requires inspecting each actual output.
The separate image-ad test skill is not modified or required at runtime.
