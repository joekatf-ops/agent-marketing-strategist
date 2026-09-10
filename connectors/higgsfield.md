# Higgsfield Connector

Verified 2026-09-10 against connected tool schemas, model records and read-only estimates.
This verification did not submit a generation. Inspect current tools before use; host prefixes
vary. The product-first brief is in `contracts/static-spec.md`. Every image is **1:1**, for both
preferred models. This is a workflow standard, not a Nano Banana capability limitation.

## Setup and read-only preflight

Connect through the host's plugin or MCP settings: https://higgsfield.ai/mcp. Setup is not restricted
to Cursor. Discover tools and call `balance` before claiming access. Resolve authentication in host
settings. Never save credentials in this repository or repeatedly retry an authentication error.

| Capability | Current tool | Behaviour |
|---|---|---|
| Account access | `balance` | Read-only |
| Catalogue | `models_list`, `models_search`, `models_get`, `models_recommend` | Read current constraints |
| Estimate | `estimate_image_cost` | Submits no generation |
| Render | `generate_image`, `generate_image_batch` | Submits jobs, may spend credits |
| Wait | `jobs_wait`, `jobs_get` | Reuse submitted job IDs |
| Display | `show_generation_by_ids` | Show actual completed results |
| Attachment upload | `media_upload_and_confirm` | Current ChatGPT user attachments only |

Do not use obsolete `models_explore` or `media_import_url`. Never use `generate_image` with
`get_cost: true` to estimate: generation submits a job. Use the dedicated estimator.

## Models and references

Respect the requested model: Nano Banana Pro is `nano_banana_pro`; ChatGPT generation is
`gpt_image_2`. Without a preference, choose an available preferred model; the current ordinary-image
tool defaults to GPT Image 2. Explicitly request `aspect_ratio: "1:1"` for both. Default to supported
`resolution: "2k"`, check current quality options and estimate the selected settings. Never advertise
a fixed credit price. Both models support other ratios; this workflow always produces square images.

The public tools accept `medias: [{"role":"image","value":"..."}]` for BOTH models. Nano Banana's
catalogue may show backend `image_references`; that is not the public tool's media role. Follow
the current tool schema if it changes.

Accepted values: uploaded media UUID, completed generation job UUID, or an authorized HTTPS image
URL imported automatically. Label product and layout references separately. Photos improve fidelity
but never guarantee it; inspect generated packaging, colour, shape and details against the reference.

`media_upload_and_confirm` handles current ChatGPT user attachments, not arbitrary local or sandbox
paths. Use a host-supported authorized upload for other files. Never invent a URL or make private
assets public to bypass an unavailable uploader. If the reference cannot be passed, return the prompt
and attachment mapping, or choose a design that avoids an exact product depiction.

## Execution

1. Derive exact copy and prompt from the brief. A normal make-an-ad request authorizes production;
   do not add a concept approval round. A plan-only request stops before generation.
2. Verify access, model, references and dedicated cost estimate. Respect spending limits. If the
   provider requires a credits/allowance choice, obtain that choice; do not guess it.
3. Submit one job per distinct prompt, explicit `aspect_ratio: "1:1"`, default `count: 1`.
   One call supports 1 to 4 samples of the same prompt, only when requested.
4. Batch distinct prompts in at most **6** ordered requests. Shape:
   `{"requests":[{"index":0,"params":{"model":"nano_banana_pro","prompt":"...",
   "aspect_ratio":"1:1","resolution":"2k","count":1}}]}`.
   Split larger requested batches while retaining stable indices.
5. Retain job IDs, actual parameters and returned adjustments. `jobs_wait` accepts
   `jobs: [{"index":0,"job_id":"..."}]`, at most 8, and `timeout_seconds` up to 15.
   Follow polling guidance. Pending is not failed. Retry failed items only, once by default.
   Never duplicate successful or pending jobs.
6. Display completed results. `show_generation_by_ids` currently supports up to 24 jobs.
   Record real result URLs or accessible local files.
7. Inspect actual width and height, spelling, product fidelity, hierarchy and implied claims.
   Correct a non-square result before marking it verified. A successful job or square prompt does
   not prove square pixels. Use `scripts/validate-image-ad.py` when local outputs are available.

Generate the complete ad or composite exact copy with available tools. Both routes need visual and
text checks. Never render missing-fact markers, fake proof objects or invented product features.

## Fallback and limits

If Higgsfield is unavailable, deliver the square brief, exact copy and ready-to-paste prompt.
Another available image tool can execute the same brief, respecting the requested provider.
State honestly whether pixels were rendered or inspected. A text-only LLM can plan but cannot
generate images. `use_unlim` is a provider payment option, not a universal free switch; follow
its current meaning and the user's choice. Publishing and budget changes are outside this adapter.
