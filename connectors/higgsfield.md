# Higgsfield Connector

Last verified: 2026-08-31, against a live authenticated session.

Higgsfield generates the image and video assets specified by `contracts/static-spec.md` and
`contracts/video-script.md`. It executes a spec. It does not decide anything: the spec is the source
of truth and the generation prompt is derived from it, per section 6 of the static contract.

## Setup

Installed as a Cursor plugin, then authenticated. Authentication is interactive and only works in the
Cursor desktop application, not from a cloud agent session. Connect it in desktop Cursor first; the
credential then travels to other sessions.

Two boot-time facts, both of which will otherwise waste your time:

- A newly installed plugin may attach mid-session, but authentication established after a session
  started does not always reach that session. A fresh session resolves it.
- `namespaceStatus: needsAuth` means exactly that. It is not a transient error and retrying will not
  clear it.

## Required capabilities

Do not treat a configured connector as an available one. Confirm with a read-only call before
claiming access:

| Capability | Tool | Cost |
|---|---|---|
| Credit and plan state | `balance` | free |
| Model catalogue and constraints | `models_explore` | free |
| Cost of a generation before running it | `generate_image` with `get_cost: true` | free, submits nothing |
| Image generation | `generate_image`, `generate_image_batch` | credits |
| Reference upload from a URL | `media_import_url` | credits |
| Video generation | `generate_video`, `generate_video_batch` | credits |
| Background removal, upscale, outpaint, reframe | `remove_background`, `upscale_image`, `outpaint_image`, `reframe` | credits |

`balance` is the preflight. If it returns credits and a plan, the connector is live.

## Model selection for a static ad

`models_explore` with `action: "recommend"` returns five models and omits the two strongest for this
job. Use `action: "list"` with `type: "image"` to see the full catalogue, which is roughly twenty
models. A recommendation here is not the same as an inventory.

The working set for DTC static ads. `nano_banana_pro` and `gpt_image_2` are the preferred pair here,
both tagged for text rendering and both capable of 4K:

| Model | Ratios | Text rendering | Reference role |
|---|---|---|---|
| `nano_banana_pro` | 1:1, 4:5, 5:4, 3:2, 2:3, 4:3, 3:4, 9:16, 16:9, 21:9 | Yes, and 4K | `image_references` |
| `gpt_image_2` | 1:1, 4:3, 3:4, 3:2, 2:3, 9:16, 16:9, 21:9. **No 4:5** | Yes, and 4K | `image` |
| `nano_banana_2` | as `nano_banana_pro`, plus `auto` | Yes | `image_references`, `mask` |
| `ms_image`, shown as DTC Ads | wide set, no 4:5 | Brand-kit aware | `image`, up to 14 |
| `marketing_studio_image` | includes 4:5 and `auto` | Not tagged for text | `image` |

Two gotchas that will cost you a failed call:

**The reference media role differs between families.** `nano_banana_*` and `seedream` take
`image_references`. `gpt_image_2`, `ms_image` and `marketing_studio_image` take `image`. Passing the
wrong role fails or is silently coerced.

**`ms_image` requires a style first.** It errors without `style_id`, and the documented workflow is to
call `show_marketing_studio` with `type: "image_style"` and have the user pick, because style is the
dominant creative driver and defaulting silently produces something nobody asked for. It also accepts
`brand_kit_id` and up to four `product_ids`, which makes it the most brand-aware option once a kit
exists.

**On aspect ratio.** `nano_banana_pro` supports 4:5, so the ratio does not force a choice between
text quality and feed real estate. `gpt_image_2` is the exception: it has no 4:5, so a `gpt_image_2`
master is 1:1. If you want 4:5 from a 1:1 generation, `flux_2_pro_outpaint` expands per side in
pixels, and negative values crop instead.

1:1 is a sound working default and it is what most of this catalogue does best. Worth knowing that it
is not free: the single CTR comparison this package records puts 4:5 ahead of 1:1 by 12 to 18 percent
on feed image, single-source and directional
(`references/12-meta-platform.md`). On `gpt_image_2` that is the cost of the model. On
`nano_banana_pro` it is a choice, since 4:5 is available at the same resolution and quality tier.

Copy is still composited rather than generated, per the contract. Good text rendering lowers the risk
of a generated headline but does not remove the need to verify it character by character, and
compositing removes the risk entirely.

## Working with a spec

1. Produce the static spec in full, including section 6, the derived prompt.
2. If a product photograph exists, `media_import_url` it and pass the returned `media_id` in
   `medias`, with the role that model's family expects: `image_references` for `nano_banana_*` and
   `seedream`, `image` for `gpt_image_2` and the marketing models. **Never pass an `https://` URL in
   `medias[].value`.** It expects a media id or a prior `job_id`.
3. Preflight the cost with `get_cost: true`.
4. Generate. Use `count` 2 to 4 only for variants of one identical prompt. For different prompts, use
   `generate_image_batch`, which is headless and takes up to 12.
5. Composite the copy from section 4 of the spec over the result.
6. Record the outcome against the spec's claim check, imagery included.

Reserve the safe-zone margins in the prompt rather than cropping afterwards, per
`references/12-meta-platform.md`. A generated image that fills the frame edge to edge loses copy
behind platform chrome.

## The claim gate applies to pixels

An image model produces whatever composition it is asked for, including compositions Meta rejects.
`contracts/static-spec.md` carries the full list. The ones that matter most here:

- No before and after, and no side-by-side body comparison, in health, wellness, beauty or weight
  management
- No generated person implied to be a real customer, and no generated result implied to be a real
  outcome
- No generated proof object: a fabricated award badge, press logo, review screenshot or certification
  mark is invented proof
- No depiction of a claim the brand cannot make in words
- A generated product must match the product as it actually is

Record each generated asset's policy risk alongside the copy claims, naming the prohibition it was
checked against.

## Fallback

Higgsfield unavailable, unauthenticated or out of credits does not block creative work. Produce the
spec and the derived prompt and hand them over. The prompt is portable to any image model, and the
spec is complete enough for a human designer, which is its stated purpose.

State that generation was not performed. Never describe an asset as produced when it was not, and
never present a prompt as though it were a rendered result.

## Security

Never request, store or include a Higgsfield key in the repository or a generated brand bundle.
Authentication belongs in the host's connector configuration.

`sandbox_exec` runs shell commands in a remote Higgsfield sandbox. Nothing in this package needs it,
and it is not part of any documented workflow here.

`use_unlim` spends the account's free-trial allowance rather than credits. Pass it only when the user
explicitly asks for their free generations, never as an unrequested saving on their behalf.

## Beyond static ads

Available and unused by any current contract, listed so the capability is known rather than
rediscovered: `generate_video` and `motion_control` for video, `video_analysis_create` for
scene-by-scene analysis of a supplied ad, `virality_predictor`, `dubbing` and `reframe` for
localisation and placement adaptation, and `tiktok_publish` for publishing.

Publishing deserves an explicit note. This package's launch invariants are manual only: never publish
an ad or change a budget automatically. A connector exposing a publish tool does not change that
rule.
