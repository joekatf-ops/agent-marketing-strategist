# Legacy configuration adapter

Version 0.2 uses one portable brand folder per brand. Create it with:

```bash
python3 scripts/init-brand-folder.py /path/to/brands/example-brand \
  --name "Example Brand" \
  --slug example-brand
```

`config/brand.example.yml` remains only for older v0.1 installations that need to point the
strategist to a brand folder during migration. New installations should not copy it to
`config/brand.yml`.

The portable folder keeps identity, product truth, approved claims, context, website snapshots,
research, outputs and retained learning in separate controlled records. This lets one universal
skill serve many brands without mixing their memory.

Never put API keys, access tokens or passwords in either configuration. Store connector secrets in
the selected runtime's secure environment or credential store.
