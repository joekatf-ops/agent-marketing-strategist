# FICTIONAL FIXTURE: Acme Trailworks

**This brand does not exist.** Acme Trailworks, the Ridgeline Merino Crew, its prices, its reviews,
its test history and every number in this folder are invented fixture data. Nothing here is evidence
about any real company, and nothing here may be copied into a real brand's folder or a real ad.

It exists so the brand-attach pipeline can be demonstrated and tested end to end without a real
brand's commercial data entering this repository, in the same spirit as the frozen output examples
in `examples/`. Hard rule 5 stands: brand facts come from the connected brand folder and never from
another brand, and this folder is another brand.

The `Acme` name is the marker. Anything named Acme in this repository is fixture data.

## What it is for

Three jobs, in order of how much they matter.

1. **A complete folder to read.** Every other brand folder starts as about thirty empty files, so
   there was nothing that showed what a filled one looks like. Compare this against
   `templates/brand-folder/` to see what the strategist is actually reading for.
2. **A target for the checker.** `scripts/check-brand-folder.py examples/brand-folder --for all`
   reports `ready` for copy and images, which is what makes the checker's negative results
   trustworthy: a checker that has never returned `ready` has not been shown to work.
3. **An isolation test.** Acme Trailworks sells a hiking sock. It is deliberately in a category
   with no overlap with sleep, supplements or skincare, so a claim, price or voice rule leaking
   from another brand into Acme's output, or the reverse, is obvious on sight rather than
   arguable.

## What it deliberately does not have

`copy` reports `ready`. Nothing else does, and each gap is here on purpose, because a fixture where
every check passes cannot show a check failing.

| Deliverable | State | What is missing, and why it is missing |
|---|---|---|
| copy | ready | nothing |
| image | nearly | no real product photograph, and there cannot be one |
| launch | nearly | no unit economics, no brand code. The launch path is the one that spends money, so it should be the one that reports incomplete |
| research | nearly | no classified evidence ledger |

The image row is the interesting one and it is not a defect. Acme Trailworks has no real product
photograph because the sock does not exist, so `--for image` can never reach `ready` for this brand.
That is the visual claim gate behaving correctly: a generated image may light, place and crop a real
product, and inventing the product is the thing it may not do. Any image made from this folder is a
fixture illustration and must be labelled as one, never presented as a product shot.

## Using it

    python3 scripts/check-brand-folder.py examples/brand-folder --for all
    python3 scripts/build-brand-bundle.py examples/brand-folder /tmp/acme-bundle.md

The bundle is the upload path: the generated file is what you paste into a chat surface that cannot
read a folder. Building it from this fixture is how that path stays tested.

One scope note. `context/voice.md` lists rejected examples, and a rejected example necessarily
quotes a banned phrase in order to reject it. `scripts/check-copy-lexicon.py` defaults to the
top-level `examples/*.md` files and does not descend into this folder, which is why that is not a
failure. Pointing the checker at this directory by hand will flag the rejected examples, and it is
supposed to. The same reasoning is why the checker is not run across the whole repository:
`config/copy-lexicon.yml` records it.
