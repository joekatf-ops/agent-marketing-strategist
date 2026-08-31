# Ad analysis input audit

## Run identity

- Run ID: "ADR-20260827-015"
- Brand: "quiet-arc"
- Mode: "performance-diagnosis"
- Method version: "1.0.0"
- Market: "AU"
- Product: "folding-reading-lamp"

## Source inventory

- "SRC-QA-PD-META" | kind="file" | label="Quiet Arc Meta ad-level export, 20-24 August 2026" | location="ad-diagnosis-performance.csv" | sha256="336d4fe2be9ff8bd67338e34e297de30662c02c653f97a65c0029564824f0482"
- "SRC-QA-PD-PDA" | kind="attachment" | label="quiet-arc-pda-static.png" | location="attached:quiet-arc-pda-static.png" | sha256=null
- "SRC-QA-PD-PRA" | kind="attachment" | label="quiet-arc-pra-static.png" | location="attached:quiet-arc-pra-static.png" | sha256=null
- "SRC-QA-PD-SLA" | kind="attachment" | label="quiet-arc-sla-comparison.mp4" | location="attached:quiet-arc-sla-comparison.mp4" | sha256=null
- "SRC-QA-PD-UWA" | kind="attachment" | label="quiet-arc-uwa-vsl.mp4" | location="attached:quiet-arc-uwa-vsl.mp4" | sha256=null

## Ad coverage

- Intake ads: 4
- ads[0]: "CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_UWA_VSL_LP_991001000000001"
- ads[1]: "CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PRA_STATIC_LP_991002000000002"
- ads[2]: "CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_SLA_COMPARISON_PDP_991003000000003"
- ads[3]: "CONTST042_NNT_NIGHTREADERS_SHAREDROOMGLARE_PDA_STATIC_PDP_991004000000004"

## Performance coverage

- Performance input: supplied

## Readiness

Input readiness: `limited`

This input-readiness label is distinct from the later Creative Audit per-ad outcomes `ready`, `revise` and `block`.

## Errors

- None

## Limitations

- First-frame retention was not supplied for video ads; opening-frame claims are limited.
