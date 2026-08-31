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

Verified aspect ratio support, which decides this more than anything else. The static contract
requires a 1:1 and 4:5 master with a 9:16 adaptation.

| Model | 4:5 | Notes |
|---|---|---|
| `marketing_studio_image` | yes | Purpose-built for product ads. 1k, 2k or 4k. One reference image. **The default.** |
| `cinematic_studio_2_5` | yes | Cinematic stills to 4K. Use when the brand's visual context calls for it |
| `gpt_image_2` | **no** | Best text rendering and typography of the set, and cannot produce the contract's master ratio |
| `soul_2` | no | Realistic UGC, fashion, portraits. Use for creator-style assets, not for the master static |
| `soul_cinematic` | no | Concept art and dramatic lighting |

The `gpt_image_2` trade-off resolves itself once you follow the contract. **Copy is composited, not
generated**, so you do not need the model to render text, which frees the choice to be made on image
quality and aspect ratio instead. That is the whole reason the rule exists.

Call `models_explore` with `action: "get"` for a model's current parameters before relying on this
table. Higgsfield's catalogue moves.

## Working with a spec

1. Produce the static spec in full, including section 6, the derived prompt.
2. If a product photograph exists, `media_import_url` it and pass the returned `media_id` in
   `medias` with role `image`. **Never pass an `https://` URL in `medias[].value`.** It expects a
   media id or a prior `job_id`.
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
