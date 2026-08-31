# Swipe corpus

Annotated real ads, used as the worked evidence layer of the craft stack.

| File | What it is |
|---|---|
| `entries.json` | Source of truth. One object per ad, validated against `../../schemas/swipe-entry.schema.json` |
| `REVIEW.md` | Generated. Drafted annotations awaiting human correction |
| `../../references/22-swipe-corpus.md` | Generated. The digest the agent actually loads |

## Workflow

```bash
FOREPLAY_API_KEY=... python3 scripts/sync-swipe-corpus.py --board-id <id> --board-name best_ads
python3 scripts/build-swipe-digest.py
```

The sync refreshes fetched fields only. It never discards an annotation or a review flag, and it
never drops an entry that has left the board, because either would throw away human work.

`.github/workflows/sync-swipe-corpus.yml` runs this weekly and opens a pull request. It needs
`FOREPLAY_API_KEY` as a repository secret.

## Reviewing

Every drafted annotation ships `"reviewed": false`. Correct anything wrong in `entries.json`, set
`"reviewed": true`, and rebuild the digest. Correcting a wrong reading is far cheaper than writing
one from blank, and the corrections are the asset.

## Two standing caveats

Ad longevity is behavioural evidence. It says an operator kept funding the ad, not that the ad
returned anything. Foreplay exposes no performance figures, so nothing here is a performance claim.

Awareness codes are computed from how long an ad runs before naming the product. That is a sort, not
a fact: an ad can name the product in the first second and still address an unaware buyer. The
never-named sentinel is also unreliable, and at least one entry reports a product as never named
while its own transcript names it.
