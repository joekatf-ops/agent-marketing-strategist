# Naming conventions

Brand-agnostic. Every token in braces comes from `config/brand.yml`. Never invent a code.
If a required token is missing from config, stop and ask for it.

## Config tokens this reference uses

```yaml
naming:
  brand_code: "{{BRAND}}"        # 2 to 4 letters, campaign level only. Example: CDN
  concept_code: "{{CONCEPT}}"    # concept prefix, locked per brand. Example: CONTST
  countries: ["{{AU}}"]
```

## Three name layers, never mixed

| Layer | What it is | Example |
|---|---|---|
| Tracker name and asset folder | Short code only | `{{CONCEPT}}001` |
| Meta ad set | Full strategy code | `{{CONCEPT}}001_NNT_BioHackers_BetterSleep` |
| Meta or production ad | Concept, awareness, type | `{{CONCEPT}}001_UWA_VID` |

**The tracker title and the asset folder name are the short code only.** Putting the full
strategy string in the tracker title breaks folder automations by spawning a second folder.

The Meta ad set carries the strategy string. Store it on the concept record and in Ads Manager.

## Level 1: campaign

```
[BRAND]_[CAMPAIGNTYPE]_[BUDGETTYPE]_[COUNTRY]_[LAUNCHDATE]
```

Example: `{{BRAND}}_CT_ABO_AU_20260901`

- **Brand:** `{{BRAND}}`
- **Campaign type:** CT (creative testing), SC (scale), RM (remarketing)
- **Budget type:** ABO, CBO, COSTCAP, BIDCAP
- **Country:** two-letter code from config
- **Date:** YYYYMMDD

## Level 2: ad set

```
[CONCEPT###]_[NNT|INSPO|ITR]_[Persona]_[Outcome]
```

Example: `{{CONCEPT}}001_NNT_BioHackers_BetterSleep`

Rules:

1. Starts with the same `{{CONCEPT}}###` as the tracker and asset folder
2. Then the source: NNT, INSPO or ITR
3. Then the persona token, no spaces, PascalCase
4. Then the outcome token, no spaces, PascalCase
5. Underscores only
6. Optional multi-SKU suffix, for example `_SHEETS`

## Level 3: ad

**Production name**, used in the tracker and asset folders:

```
[CONCEPT###]_[UWA|PRA|SLA|PDA]_[VID|IMG|CAR]
```

Examples: `{{CONCEPT}}001_UWA_VID`, `{{CONCEPT}}001_PDA_IMG`

**Optional Ads Manager extension:**

```
[CONCEPT###]_[UWA|PRA|SLA|PDA]_[VID|IMG|CAR]_[FORMAT]_[URLTYPE]_[POSTID]
```

Example: `{{CONCEPT}}001_UWA_VID_UGC_LP_POSTXXX`

### Awareness codes

| Code | State |
|---|---|
| UWA | Unaware |
| PRA | Problem aware |
| SLA | Solution aware |
| PDA | Product aware |

### Media codes

VID, IMG, CAR

### URL types

LP (landing page), PDP, HP (homepage), CP (collection page)

## Worked example

```
Tracker / asset folder:  {{CONCEPT}}001
Campaign:                {{BRAND}}_CT_ABO_AU_20260901
Ad set:                  {{CONCEPT}}001_NNT_BioHackers_BetterSleep
Ads:                     {{CONCEPT}}001_UWA_VID
                         {{CONCEPT}}001_PRA_VID
                         {{CONCEPT}}001_SLA_VID
                         {{CONCEPT}}001_PDA_IMG
```

## Locked rules

1. Tracker name equals asset folder name equals `{{CONCEPT}}###` only.
2. Meta ad set equals `{{CONCEPT}}###_SOURCE_Persona_Outcome`.
3. Production ad equals `{{CONCEPT}}###_UWA|PRA|SLA|PDA_VID|IMG|CAR`.
4. The brand code is campaign level only. Never use it as a concept code.
5. Hooks live in the record body, never in names.
6. No em dashes in names or documents.
7. Never leave a blank field in a live Meta name.
8. Every concept number is sequential and never reused, even for a killed concept.

## Register

Keep a live register mapping concept code to ad set name to angle type, so nobody
reconstructs a name from memory. Minimum columns: concept code, Meta ad set, angle type,
status.
