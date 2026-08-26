# Output Contracts

This agent produces six kinds of artefact. Each has its own contract in `contracts/`, because
a research brief and an ad headline have nothing structurally in common and one loose contract
would hold neither.

| Artefact | Contract | When |
|---|---|---|
| Customer Intelligence Brief | `contracts/customer-intelligence.md` | Start of any engagement with a brand, and refreshed quarterly |
| Concept Batch | `contracts/concept-batch.md` | Before any creative production |
| Ad Copy | `contracts/ad-copy.md` | Primary text, headlines, descriptions, CTA |
| Video Script | `contracts/video-script.md` | Any video execution |
| Static and Carousel Spec | `contracts/static-spec.md` | Any image or carousel execution |
| Ad Diagnosis | `contracts/ad-diagnosis.md` | Reading performance and deciding what next |

## Rules that apply to all six

1. **Shape is locked. Substance is not.** Section order, counts and formatting do not change
   between runs, brands or models. The content changes because the brand and evidence change.
2. **Evidence or nothing.** Every claim traces to the Brand Context Pack, the intelligence
   brief, a cited source, or is explicitly tagged as strategist judgement.
3. **The claim gate never bends.** In a regulated category, no claim ships without an approved
   wording entry.
4. **Thin input gets named.** Every contract has a section for what is under-evidenced. It is
   filled honestly, not left empty by default.
5. **No em dashes. Anywhere.**
6. **Run the self-check before presenting.** Every line passes, or it gets fixed. A failed line
   is never shipped with a caveat attached.

## The drift test

Before this agent is marked Live, run the same brief twice in two different tools, for example
Claude Code and ChatGPT. Diff the outputs.

- Same sections, same order, same counts: pass
- Different wording inside sections: expected
- Different sections, missing sections, different format: the contract is too loose

Record the result in the README changelog.
