# Ad-analysis runs

Each `ADR-YYYYMMDD-###` folder contains a portable `intake.json` and this run guidance. Fill or
update the intake before analysis. The raw assets and exports may be placed or referenced in the run folder, but they are excluded from generated brand bundles.

Generate the current input audit with:

```bash
__VALIDATION_COMMAND__
```

The audit validates supplied inputs only. It does not make a performance prediction or write
controlled strategy, winner, or revision records.
