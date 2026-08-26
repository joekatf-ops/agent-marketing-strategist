# Output Contracts

The strategist has nine governed artefacts. Each task loads its contract before work begins.

| Artefact | Contract | When |
|---|---|---|
| Brand Readiness | `contracts/brand-readiness.md` | Start of each mode or when the folder changes |
| Customer Intelligence Brief | `contracts/customer-intelligence.md` | New brand, stale evidence, or research refresh |
| Concept Batch | `contracts/concept-batch.md` | Before creative production |
| Hook Batch | `contracts/hook-batch.md` | After a concept and execution are selected |
| Ad Copy | `contracts/ad-copy.md` | Primary text, headlines, descriptions, and CTA |
| Video Script | `contracts/video-script.md` | Any selected video execution |
| Static and Carousel Spec | `contracts/static-spec.md` | Any selected static or carousel execution |
| Ad Diagnosis | `contracts/ad-diagnosis.md` | Manual performance analysis and next decisions |
| Learning Update | `contracts/learning-update.md` | After an approved human revision |

## Rules that apply to all nine

1. **Resolve the brand first.** Every artefact names one brand, market, product, evidence version,
   and approved-learning version.
2. **Shape is governed.** Section order, fields, and default counts remain stable across models.
   Explicit user needs and brand constraints may alter a default count when the rationale says so.
3. **Evidence stays classed.** Brand facts, assertions, brand-customer evidence, market evidence,
   behaviour, and strategist judgement never collapse into one category.
4. **The claim gate never bends.** Regulated or high-risk claims require approved wording and
   substantiation for the active market.
5. **Thin input remains visible.** Missing evidence changes the confidence and permitted use. It is
   never padded to satisfy a count.
6. **Freshness is part of validity.** Research and strategy state the last website check, material
   changes, connector results, and important source dates.
7. **The active brand folder is canonical.** Uploads and chat memory are working copies.
8. **Learning needs approval and scope.** An edit is not automatically a brand rule.
9. **No em dashes or en dashes in delivered advertising copy.**
10. **Run the self-check.** Fix failed checks before presenting the artefact.

## Portability test

Before release, run the same evidence pack and request in at least two runtimes:

- same sections, order, required fields, counts, evidence labels, and claim decisions: pass;
- different wording within those fields: expected;
- missing sections, mixed brands, invented connector access, or different evidence status: fail.

Record the runtime, bundle version, brand-bundle version, and validation result.
