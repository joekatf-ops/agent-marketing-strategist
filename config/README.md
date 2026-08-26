# config

Everything brand-specific lives here. Nothing brand-specific lives anywhere else.

## Setup

```bash
cp brand.example.yml brand.yml
```

Fill in `brand.yml`, or run `agent-brand-context` once for the brand and let it generate both
the Brand Context Pack and this file.

`brand.yml` is gitignored. Never commit a real one.

## Why it works this way

The same agent runs on our brands and on client brands. If brand values were baked into the
instructions, every brand would need a fork, and every fork would drift. Injecting them means
one agent, one version, many brands.

## Secrets

Never put API keys, tokens or passwords in this file. Reference an environment variable
instead:

```yaml
tools:
  meta_access_token: "${META_ACCESS_TOKEN}"
```
