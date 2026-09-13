# Copywriting standards: the sixteen

Sixteen rules for copy that reads like a person wrote it. Most of them were already enforced somewhere
in this library. This file states all sixteen in one place, says how each one is checked, and settles
the four that contradict each other or contradict the awareness model.

A rule that cannot be checked is a preference. Each one below carries its check, and the column says
where enforcement actually lives.

## Precedence, when two of them collide

The core development method is `29-moment-to-meaning.md`: move from a problem or desire into a
recognisable moment, its consequence, personal meaning and desired experience, then establish the
product's supported role. Apply it before writing and during editing across every copy format.
These sixteen standards check the resulting execution. A depth check is mandatory; an emotional
story is not. Facts and the current task remain the constraints on both.

Apply the selling-usefulness check from `30-scientific-advertising.md`: select the likely buyer,
provide useful selling information, support it and make the next step clear. Curiosity, emotion and
stakes serve that job and are optional. Repair a weak payload rather than disguising it with a loop.
A fact can be specific and persuasive even when competitors share it; exclusivity needs separate proof.

Work down this list. The first rule that applies wins, and the loser gets named in the rationale.

1. **Never invent a claim.** Absolute. No other rule on this page licenses a fabricated specific.
2. **Truth constrains style.** Improve expression within the evidence. An accurate but off-brief
   line still needs revision; a stronger-sounding overstatement does not ship.
3. **Approved wording survives editing.** Concision never removes a qualifier that a regulated claim
   depends on.
4. **Awareness governs position when the brief specifies it.** A simple product brief does not need
   a formal awareness diagnosis. When the stage is known, ordering follows it, per
   `02-customer-state.md`. Rules about ordering yield to it.
5. **Everything else is craft**, and craft judgement is arguable. Say which way you went.

## The sixteen

### 1. Sell the end state

Identify what the person wants back or wants to experience, beyond just stopping a problem.
Connect a product detail to a defensible use or payoff. Feature-led ads remain valid; do not force
an emotional transformation or invent beliefs or results.

**Prevents:** feature inventories, spec sheets, and copy that describes the object rather than the
change.

**The check:** name the end state in one sentence without using the product's name. If you cannot, the
copy is selling an object.

Separate what the person wants from what the product is known to do. Use the moment-to-meaning
sequence to find relevance, never to promote a desired emotional or health outcome into a proven
benefit. A practical end state can carry quiet satisfaction without explicit emotion language.

**Position, not presence.** The complete ad conveys a desirable experience or practical payoff.
Recognition or desired experience can lead at Problem Aware. At Unaware, establish relevance through
a situation or desire before pitching the category. Neither pain-first nor benefit-first is universal.

### 2. Pass the stranger test

Every opening reads cold, to somebody with no prior exposure to the brand, the category or the
previous ad.

**Prevents:** setup before the claim, and openings that assume a returning viewer.

**The check:** the subject and reason to care are understandable in the opening's visual context.
An honest curiosity gap may leave its specific answer unresolved, not the ad's basic relevance.

Already a non-negotiable in `20-hook-quality-standard.md` and a self-check in every contract.

### 3. Cut, then cut again

Develop the thought before shortening it. Then make a separate editorial pass: compare candidates
against the chosen concept and rewrite the strongest. Cut words only while preserving that meaning.

**Prevents:** padding, throat-clearing, and copy whose length came from effort rather than argument.

**The check:** for each sentence, delete it and read the copy. If the argument survives, it stays
deleted. State the word count before and after on long copy.

**Bounded by rule 3 of precedence.** Cut words, never cut a qualifier a claim needs. A shorter line
that overstates is not a better line. Also preserve necessary explanation, proof, offer conditions
and the next action across the complete execution. There is no universal shortest winning length.

### 4. Select your reader

The copy should make the right person feel addressed and let the wrong person move on. A reader who is
not sure the ad is for them scrolls.

**Prevents:** copy pitched at everybody, which persuades nobody, and the qualification being left to
the targeting.

**The check:** can the intended reader recognise a relevant situation, desire, fact or offer from
the opening and its visual context. A useful product descriptor can select as clearly as a scene.

**Select by situation, not by label.** "If you're someone who struggles with sleep" is a label and
`24-writing-for-low-awareness.md` bans it as spent setup. "The 4am wake-up where you do the mental
maths on how much sleep is left" is a situation, and only the right reader recognises it. Situational
recognition can make an abstract label concrete; use it when it helps this brief.

### 5. No em dashes

No em dashes and no en dashes, anywhere, always. Comma, colon, or two sentences.

**Prevents:** the single most reliable machine-writing tell in English.

**The check:** mechanical. `scripts/validate-package.py` scans for the characters. The only exemption
is verbatim third-party ad copy in `corpus/`, recorded as it ran.

### 6. Tone matches slot

Each slot has a job. The hook earns relevant attention, the body explains, the headline makes the
key idea legible and the CTA instructs. Adapt the register where useful, without forcing tonal
changes. A direct explanation or offer may be the most useful opening.

**Prevents:** hooks that read like body copy, which is the most common reason a good idea fails in the
first second, and CTAs that hedge.

**The check, per slot:**

| Slot | Register | Fails when |
|---|---|---|
| Video hook, first 3 seconds | Relevant action or information, speakable | It wastes setup or attracts unrelated attention |
| Primary text line one | Complete before truncation | It depends on line two |
| Primary text body | Explanatory, sentences vary | It repeats line one at length |
| Headline, length fits placement | Clear, one dominant idea | Compression removes the reason to care |
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

Match the requested task. Concept exploration needs different arguments. Five headline options,
rewrites or a controlled wording test can deliberately keep one concept while improving its
expression. New punctuation alone is not a new strategic idea, but wording can matter.

**Prevents:** cosmetic changes presented as new concepts, or an approved concept lost during rewriting.

**The check:** can you identify what changed: concept, entry, expression or another test variable?
Keep the requested count and concept. Revise weak options rather than misclassifying useful
same-concept alternatives as duplicates or filling the set with unrelated benefits.

Already mandatory in `contracts/hook-batch.md` and `contracts/ad-copy.md`, and scored as
`distinctness` in the eval. This library says "route" where the rule says "angle".

### 9. One idea each

One central argument per ad. Facts, examples, benefits and objections may reinforce it. They do not
become separate ads merely because the argument uses several details or a conjunction.

**Prevents:** the reader arbitrating between two competing claims, which they resolve by scrolling.

**The check:** state the central argument plainly, then identify how each supporting part helps it.

### 10. Never invent claims

No invented statistic, review count, testimonial, study, comparison, scarcity claim, timeframe or
competitor fact. Ever, for any reason, including that the copy is better with one.

**Prevents:** the failure that survives every other quality gate and cannot be fixed after publication.

**The check:** every specific traces to supplied product facts or relevant evidence. Mark essential
gaps in a brief only, never in finished image copy. **A marker names a gap
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

A supported quantity, duration, price, count or temperature can make a description more concrete.
This is a writing preference, not a universal performance claim. "Three weeks" beats "quickly". "The 4am wake-up" beats "poor sleep".

**Prevents:** inflated adjectives, which readers discount automatically because every competitor uses
them.

**The check:** circle every adjective doing persuasive work and try to replace it with a figure.

**When no figure exists, do not reach for the adjective.** The order of preference is: a real figure,
then a concrete situation with no number in it. Mark an essential missing figure in the brief only. The
vague adjective is last and usually worse than all three. Rule 10 outranks this rule absolutely: the
absence of a number is never a reason to produce one.

### 14. Front-load the point

The most important thing comes first, at every scale: first line of the ad, first clause of the
sentence, first frame of the video.

**Prevents:** buried leads, and copy that dies at truncation with the argument still ahead of it.

**The check:** preview the actual placement. An 80-character cut is a useful stress test, not a
universal character limit. Put the relevant point early and preserve the meaning and material terms.

**The point is not always the product.** At Unaware the point is the situation, and
`24-writing-for-low-awareness.md` holds the product name back deliberately. Front-loading orders by
the reader's interest, not by the brand's.

### 15. Sound unmistakably brand

When a brand voice is supplied, make the copy identifiable without the logo. Without one, choose
a suitable provisional voice; do not block creation or invent an established brand rule.

**Prevents:** competent copy that any competitor could have run, which builds nothing across
impressions.

**The check:** compare against the supplied brand voice, product facts and visual identity.
The competitor-name swap can reveal generic phrasing, but is not a pass/fail specificity test.
Shared category facts can sell honestly. Do not invent an exclusive feature to sound distinctive.

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

1. **Develop and write.** Use the moment-to-meaning sequence to find the relevant experience and
   supported product bridge. Awareness sets the order when specified; choose one idea, a defensible
   end state and a recognisable reader situation or practical payoff.
2. **Deepen and cut.** Replace generic pain labels with useful concrete detail. Check why the moment
   matters; do not merely add an emotion word. Apply rules 3, 7, 13 and 16, removing repeated agitation,
   padding and any scene that does not advance the argument.
3. **Verify.** Rules 10, 11 and 5. Every asserted fact traces, essential missing claims stay in the
   brief, hypotheses are labelled in the rationale, the product bridge is defensible and the
   characters are clean. No invented customer testimony or emotional result.

Pass two is where the work is. Pass three is where the risk is.
