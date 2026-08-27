# Output Contracts

The strategist has eleven governed artefacts. Each task loads its contract before work begins.

| Artefact | Contract | When |
|---|---|---|
| Brand Readiness | `contracts/brand-readiness.md` | Start of each mode or when the folder changes |
| Customer Intelligence Brief | `contracts/customer-intelligence.md` | New brand, stale evidence, or research refresh |
| Concept Batch | `contracts/concept-batch.md` | Before creative production |
| Hook Batch | `contracts/hook-batch.md` | After a concept and execution are selected |
| Ad Copy | `contracts/ad-copy.md` | Primary text, headlines, descriptions, and CTA |
| Video Script | `contracts/video-script.md` | Any selected video execution |
| Static and Carousel Spec | `contracts/static-spec.md` | Any selected static or carousel execution |
| Campaign Launch Plan | `contracts/campaign-launch-plan.md` | Before a human builds or changes Meta campaigns |
| Destination Handoff | `contracts/destination-handoff.md` | Before launch, for ad-to-page message continuity |
| Ad Diagnosis | `contracts/ad-diagnosis.md` | Manual performance analysis and next decisions |
| Learning Update | `contracts/learning-update.md` | After an approved human revision |

## Rules that apply to all eleven

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
11. **Coordinate and test are separate.** The coordinate is Who x Primary Problem. Every NNT,
    INSPO or ITR batch receives a new sequential CONTST ID.
12. **Initial tests have four ads.** Every initial NNT or INSPO contains exactly UWA, PRA, SLA and
    PDA. Most Aware is handled by the conversion environment, not as a standard ad.
13. **Production is traceable.** Every hook, copy, script and static output carries CONTST, source,
    Who, Primary Problem, awareness code and job, messaging route, primary hook, media type,
    execution format, proof and claims required, destination, CTA, people, assets and location
    required, and the complete final ad name ending in `POSTIDXXX` before publication.
14. **Destinations continue the argument.** UWA and PRA default to LP. SLA and PDA default to PDP.
    Every deliberate exception records why it remains congruent, its evidence, risk, owner and approval.
15. **Launch is manual.** Creative testing is ABO with one CONTST batch per ad set, a $50 daily
    ad-set floor, approximately $100 preferred and five full days planned observation. Scaling is
    CBO and graduated winners keep the real Post ID. No artefact implies live Meta access.
16. **Diagnosis is non-causal.** Read business, funnel and creative layers in that order, state
    validity first and classify each decision using the six-decision taxonomy.

## Portability test

Before release, run the same evidence pack and request in at least two runtimes:

- same sections, order, required fields, counts, evidence labels, and claim decisions: pass;
- different wording within those fields: expected;
- missing sections, mixed brands, invented connector access, or different evidence status: fail.

Record the runtime, bundle version, brand-bundle version, and validation result.
