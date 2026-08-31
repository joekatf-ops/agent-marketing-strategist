# Copywriting standards: the sixteen

Sixteen rules for copy that reads like a person wrote it. Most of them were already enforced somewhere
in this library. This file states all sixteen in one place, says how each one is checked, and settles
the four that contradict each other or contradict the awareness model.

A rule that cannot be checked is a preference. Each one below carries its check, and the column says
where enforcement actually lives.

## Precedence, when two of them collide

Work down this list. The first rule that applies wins, and the loser gets named in the rationale.

1. **Never invent a claim.** Absolute. No other rule on this page licenses a fabricated specific.
2. **Truth beats style.** An accurate line that reads slightly worse ships. A better line that
   overstates does not.
3. **Approved wording survives editing.** Concision never removes a qualifier that a regulated claim
   depends on.
4. **Awareness governs position.** What goes first is set by the customer's state of knowledge, per
   `02-customer-state.md`. Rules about ordering yield to it.
5. **Everything else is craft**, and craft judgement is arguable. Say which way you went.

## The sixteen

### 1. Sell the end state

Sell the life the product produces, not the product. The reader is buying the version of their
situation that exists after purchase.

**Prevents:** feature inventories, spec sheets, and copy that describes the object rather than the
change.

**The check:** name the end state in one sentence without using the product's name. If you cannot, the
copy is selling an object.

**Position, not presence.** The end state must be present in every ad. It is not required to be the
first line, and at Unaware it must not be, per `24-writing-for-low-awareness.md`. See
`21-evidence-and-doctrine.md`.

### 2. Pass the stranger test

Every opening reads cold, to somebody with no prior exposure to the brand, the category or the
previous ad.

**Prevents:** setup before the claim, and openings that assume a returning viewer.

**The check:** hand the first line to somebody who knows nothing. If they need one question answered
before it lands, it fails.

Already a non-negotiable in `20-hook-quality-standard.md` and a self-check in every contract.

### 3. Cut, then cut again

First draft, then remove every word that carries no weight, then do it once more on the result. Second
pass finds what the first cannot, because the first pass is still attached to the draft.

**Prevents:** padding, throat-clearing, and copy whose length came from effort rather than argument.

**The check:** for each sentence, delete it and read the copy. If the argument survives, it stays
deleted. State the word count before and after on long copy.

**Bounded by rule 3 of precedence.** Cut words, never cut a qualifier a claim needs. A shorter line
that overstates is not a better line.

### 4. Select your reader

The copy should make the right person feel addressed and let the wrong person move on. A reader who is
not sure the ad is for them scrolls.

**Prevents:** copy pitched at everybody, which persuades nobody, and the qualification being left to
the targeting.

**The check:** can the intended reader tell inside the first line that this is about them.

**Select by situation, not by label.** "If you're someone who struggles with sleep" is a label and
`24-writing-for-low-awareness.md` bans it as spent setup. "The 4am wake-up where you do the mental
maths on how much sleep is left" is a situation, and only the right reader recognises it. Situational
recognition qualifies harder than any label and costs no words.

### 5. No em dashes

No em dashes and no en dashes, anywhere, always. Comma, colon, or two sentences.

**Prevents:** the single most reliable machine-writing tell in English.

**The check:** mechanical. `scripts/validate-package.py` scans for the characters. The only exemption
is verbatim third-party ad copy in `corpus/`, recorded as it ran.

### 6. Tone matches slot

Each slot in an ad has a different job, so each takes a different register. The hook interrupts. The
body explains. The headline compresses. The CTA instructs. One tone applied across all four means at
least three are wrong.

**Prevents:** hooks that read like body copy, which is the most common reason a good idea fails in the
first second, and CTAs that hedge.

**The check, per slot:**

| Slot | Register | Fails when |
|---|---|---|
| Video hook, first 3 seconds | Interrupting, mid-scene, spoken | It explains, or sets up |
| Primary text line one | Complete before truncation | It depends on line two |
| Primary text body | Explanatory, sentences vary | It repeats line one at length |
| Headline, ~40 characters | Compressed, one idea | It is a summary of the body |
| Description | Supporting, factual | It restates the headline |
| CTA | Instruction, one action | It hedges, or offers two actions |
| Static primary line | Legible at thumbnail | It needs the body to make sense |

### 7. Kill empty hedges

Remove qualifiers that drain the claim without adding accuracy.

**Prevents:** "may potentially help support", which asserts nothing and reads as legal cover that
provides none.

**The check:** delete the hedge. If the line now says something untrue, the claim is the problem, not
the hedge, and it goes back to the claim gate. If the line says the same thing more directly, the
hedge was filler.

**Register hedges are different and they stay.** A hedge inside quoted or first-person copy signals a
real speaker, which is the mechanism behind the confession opening. `21-evidence-and-doctrine.md`
carries the full resolution. Hedge lists are in `config/copy-lexicon.yml`.

### 8. Angles, not synonyms

Multiple options must differ in the route into the argument, not in wording. New adjectives, new
punctuation and new camera angles do not create a new option.

**Prevents:** a batch of six that is really one idea written six ways, which tests nothing.

**The check:** state each option's route in a few words. Two options with the same route are one
option. Cut to the number that genuinely differ rather than padding to a count.

Already mandatory in `contracts/hook-batch.md` and `contracts/ad-copy.md`, and scored as
`distinctness` in the eval. This library says "route" where the rule says "angle".

### 9. One idea each

One dominant idea per ad, one per line. If it needs two, it is two ads.

**Prevents:** the reader arbitrating between two competing claims, which they resolve by scrolling.

**The check:** state the ad's idea in one sentence with no "and". Hard rule 7.

### 10. Never invent claims

No invented statistic, review count, testimonial, study, comparison, scarcity claim, timeframe or
competitor fact. Ever, for any reason, including that the copy is better with one.

**Prevents:** the failure that survives every other quality gate and cannot be fixed after publication.

**The check:** every specific traces to the claim library or carries a marker. **A marker names a gap
and never wraps a guess.** `[STAT: needs a real figure]` is correct. An invented figure tagged for
removal is still an invented figure: it reached the page, it reads as real, and somebody will ship it.

Hard rule 1, the claim gate in `10-voice-and-claims.md`, and `placeholder_discipline` in the eval,
which scores 0 for any invented specific.

### 11. Truth beats style

When the accurate version reads worse, ship the accurate version. Then keep working on the accurate
version, because it usually can be made better within the truth.

**Prevents:** a compelling line justified by its performance, which is how brands acquire claims they
cannot defend.

**The check:** for each claim, could the brand repeat this at scale, in writing, to a regulator. A
compelling route never excuses an inaccurate claim.

### 12. Benefit, not mechanism

Lead with what the reader gets, not with how the product works.

**Prevents:** machinery presented to somebody who has not yet agreed they want what it produces.

**Read this one with the resolution in `21-evidence-and-doctrine.md`,** because taken flat it
contradicts the awareness model, which makes mechanism the correct Solution Aware lead. The operative
form:

- A mechanism may lead, when the reader has already conceded the benefit.
- A mechanism may never appear without the payoff it produces, at any awareness level.

**The check:** every mechanism clause is followed by the "so that" it produces, stated or plainly
implied. "Cold-pressed in small batches" is machinery. Add "so it still tastes like the fruit" and it
is an argument.

### 13. Numbers beat adjectives

A quantity, a duration, a price, a count or a temperature outperforms any adjective describing the
same thing. "Three weeks" beats "quickly". "The 4am wake-up" beats "poor sleep".

**Prevents:** inflated adjectives, which readers discount automatically because every competitor uses
them.

**The check:** circle every adjective doing persuasive work and try to replace it with a figure.

**When no figure exists, do not reach for the adjective.** The order of preference is: a real figure,
then a marked placeholder naming the figure needed, then a concrete situation with no number in it. The
vague adjective is last and usually worse than all three. Rule 10 outranks this rule absolutely: the
absence of a number is never a reason to produce one.

### 14. Front-load the point

The most important thing comes first, at every scale: first line of the ad, first clause of the
sentence, first frame of the video.

**Prevents:** buried leads, and copy that dies at truncation with the argument still ahead of it.

**The check:** truncate at 80 characters. What survives should be a complete and compelling
proposition. If it is not, the copy is not long, it is buried.

**The point is not always the product.** At Unaware the point is the situation, and
`24-writing-for-low-awareness.md` holds the product name back deliberately. Front-loading orders by
the reader's interest, not by the brand's.

### 15. Sound unmistakably brand

The copy should be identifiable as this brand with the logo removed.

**Prevents:** competent copy that any competitor could have run, which builds nothing across
impressions.

**The check:** swap in a competitor's name. If the ad still works unchanged, there is no brand in it.
This is the same test as `specificity` in the eval, applied to voice instead of proof.

Voice comes from `context/voice.md` and `learning/approved-rules.yml` in the connected brand folder.
Without a brand folder this rule cannot be fully met, and the honest response is to say so rather than
to invent a voice. Note it as a gap.

### 16. No AI lexicon

Two tiers, because a blanket word ban is wrong and a blanket permission is worse.

**Tier one, banned outright.** Constructions that never do useful work in an ad. "In today's world",
"it's not just X, it's Y", "unlock the power of", "elevate your", "delve into", "when it comes to",
"revolutionise". No brand voice earns these.

**Tier two, flagged and justified.** Words a language model overuses that also have honest literal
uses: seamless, robust, harness, transform, effortless, curated, elevate as a physical verb. "Seamless"
is a lie in a brand promise and a fact in a garment description. Use one, say why in the rationale.

**Prevents:** copy that reads as generated, which readers now detect and discount.

**The check:** `scripts/check-copy-lexicon.py` scans frozen examples against
`config/copy-lexicon.yml`. Tier one is an error, tier two is a report. The lists are data, so they can
be extended without touching code.

Beyond vocabulary, the structural tells: rule-of-three lists used as filler, stacked rhetorical
questions, sentences opening "Whether you're", and paragraphs of uniform sentence length. Judge the
line rather than the pattern, per `21-evidence-and-doctrine.md`.

## Where each rule is enforced

| # | Rule | Enforcement |
|---|---|---|
| 1 | Sell the end state | Contract self-check, `end_state` in the eval |
| 2 | Pass the stranger test | `20-hook-quality-standard.md` non-negotiable, hard rule 8, eval |
| 3 | Cut, then cut again | Contract self-check, `concision` in the eval |
| 4 | Select your reader | Contract self-check, `reader_selection` in the eval |
| 5 | No em dashes | Mechanical, `validate-package.py`, hard rule 12 |
| 6 | Tone matches slot | Contract self-check against the slot table above |
| 7 | Kill empty hedges | `config/copy-lexicon.yml`, `no_hedging` in the eval |
| 8 | Angles, not synonyms | Contract requirement, `distinctness` in the eval |
| 9 | One idea each | Hard rule 7, `no_chaos` in the eval |
| 10 | Never invent claims | Hard rule 1, claim gate, `placeholder_discipline` in the eval |
| 11 | Truth beats style | Claim gate, hard rules 3 and 4 |
| 12 | Benefit, not mechanism | So What test, contract self-check |
| 13 | Numbers beat adjectives | `specificity` in the eval, contract formatting rules |
| 14 | Front-load the point | Truncation requirement, `front_loaded` in the eval |
| 15 | Sound unmistakably brand | Brand folder voice rules, brand filter |
| 16 | No AI lexicon | Mechanical over examples, `no_ai_lexicon` in the eval |

## Running them

Do not run sixteen checks in sequence on every line. Three passes:

1. **Write.** Awareness sets the order, one idea, end state present, reader selected.
2. **Cut.** Rules 3, 7, 13 and 16 together. This is the pass that makes copy sound human, and it is
   the one most often skipped.
3. **Verify.** Rules 10, 11 and 5. Every specific traces or is marked, every claim is defensible, the
   characters are clean.

Pass two is where the work is. Pass three is where the risk is.
