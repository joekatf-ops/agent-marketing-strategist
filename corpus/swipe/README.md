# Swipe corpus

Real ads recorded as reference data for layout and reference analysis. Since 1.9.0 nothing in this
package teaches from the corpus: the hook teaching digest and its review queue were retired when ad
copy moved to the DTC Ad Copywriting playbook
(/Users/joekatf/JOEKA OS/AI/AI Playbooks/Playbooks/write-dtc-ad-copy/write-dtc-ad-copy.md). Opening
annotations that already exist in `entries.json` are kept as data only.

| File | What it is |
|---|---|
| `entries.json` | Source of truth. One object per ad, validated against `../../schemas/swipe-entry.schema.json` |
| `ATTRIBUTION.md` | What is recorded, why, and how a brand can have entries removed |

## Workflow

```bash
FOREPLAY_API_KEY=... python3 scripts/sync-swipe-corpus.py --board-id <id> --board-name best_ads
```

The sync refreshes fetched fields only. It never discards an annotation or a review flag, and it
never drops an entry that has left the board, because either would throw away human work.

`.github/workflows/sync-swipe-corpus.yml` runs this weekly and opens a pull request. It needs
`FOREPLAY_API_KEY` as a repository secret.

## Two standing caveats

Ad longevity is behavioural evidence. It says an operator kept funding the ad, not that the ad
returned anything. Foreplay exposes no performance figures, so nothing here is a performance claim.

Awareness codes are computed from how long an ad runs before naming the product. That is a sort, not
a fact: an ad can name the product in the first second and still address an unaware buyer. The
never-named sentinel is also unreliable, and at least one entry reports a product as never named
while its own transcript names it.

## Image references

Use the optional media and visual_analysis fields in the entry schema. An inspected record names
the actual source and inspection date, separates observations from interpretations, and may record
an optional awareness reading and adaptation plan. An uninspected record has no visual observations.
Use contracts/reference-analysis.md for the working analysis. The sync preserves these local fields,
including when no text annotation exists. Do not turn a video-style guess into an image teaching note.
