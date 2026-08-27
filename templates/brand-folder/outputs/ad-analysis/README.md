# Ad-analysis runs

Each `ADR-YYYYMMDD-###` folder contains a portable `intake.json` and this run guidance. Fill or
update the intake before analysis. The raw assets and exports may be placed or referenced in the run folder, but they are excluded from generated brand bundles.

Generate the current input audit with:

```bash
__VALIDATION_COMMAND__
```

The audit validates supplied inputs only. It does not make a performance prediction or write
controlled strategy, winner, or revision records.

When the validator status is `ready` or `limited`, a Performance Diagnosis may write `diagnosis.md`.
Optional funnel or video gaps limit the affected claims rather than blocking the diagnosis. A
`blocked` status stops performance conclusions.

Optional handoff files are proposals only:

- `test-register-patch.yml` contains only observations, supplied results, confidence, verdict and
  next action for a matching existing test; it contains no new test ID.
- `next-brief.md` may describe an ITR but must show
  `CONTST: unreserved — human decision required`.
- `persistence-summary.md` states what was written, what remains proposed, the destination record,
  owner and required human confirmation.

Do not edit controlled test, winner or approved-revision records from this run folder. Winner
graduation requires a real Post ID and confirmation. Human copy, claim or voice changes route
through `contracts/learning-update.md`. Upload-only output is a patch, not persistence.
