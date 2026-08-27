# Ad Analysis Harness v0.4 Design

status: awaiting written review
requested_by: Joe
approved_direction: portable brand-folder harness from the preceding conversation
target_release: 0.4.0

## Purpose

Make the strategist usable as a repeatable ad-analysis system across Codex, Claude, Claude Code,
ChatGPT, Gemini, Grok and Grok Agents. A user should be able to select one brand, attach ads and,
when available, supply a manual Meta export. The strategist must then choose the correct analysis
mode, audit the inputs, produce the governed result and prepare safe retained-learning updates.

The harness wraps the existing strategy. It does not replace the `Who x Primary Problem` method,
require live Meta access or create a provider-specific application.

## Outcomes

- One obvious request: `Analyse these ads for <brand>`.
- Creative-only analysis before or without performance data.
- Full performance diagnosis from manually supplied CSV files, screenshots or tables.
- Stable run folders and machine-readable intake manifests.
- Brand-specific outputs, test observations and proposed next actions that survive between LLMs.
- Human confirmation before controlled test, winner or learning records change.
- The current v0.4 skill installed locally in Codex after the reviewed release is published.

## Non-goals

- No live Meta reporting, publishing, budget changes or automated account mutations.
- No dashboard or provider-hosted web application.
- No automatic allocation of a new CONTST merely because diagnosis recommends an ITR.
- No automatic winner graduation without a real Post ID and human confirmation.
- No automatic promotion of an ad observation or human edit into the universal method.
- No automatic copying of large creative assets into the brand folder.

## Approaches considered

### 1. Prompt-only workflow

Add a stronger prompt and rely on users to attach the right material each time. This is fast but
does not create stable input validation, run history or portable handoff between runtimes.

### 2. Provider-specific analysis application

Build an application around one LLM API and one storage system. This could offer a polished UI but
would undermine the existing cross-runtime design and introduce hosting, authentication and API
maintenance before the workflow is proven.

### 3. Portable file-based harness — selected

Add a strict run manifest, initializer and validator to the repository. The LLM performs the
qualitative analysis through governed contracts; deterministic scripts handle run creation and
input validation. This keeps the brand folder as the durable brain and works in connected-folder
and upload-only runtimes.

## Analysis modes

### Creative Audit

Use when performance data is absent or the user explicitly asks for a pre-launch review. It judges
the complete supplied creative against brand truth and strategy without predicting performance.

The new governed `Creative Audit` artefact covers:

1. input coverage and limitations;
2. ad identity and traceability;
3. Who x Primary Problem clarity;
4. awareness job and messaging route;
5. hook coherence and body handoff;
6. proof, offer, claims and CTA;
7. format, visual communication and production execution;
8. destination continuity;
9. ranked issues with evidence;
10. a pre-launch outcome for each ad: `ready`, `revise` or `block`;
11. what cannot be concluded without performance data.

This becomes the twelfth governed artefact. It cannot assign `keep`, `ITR`, `stop` or `scale`,
because those are performance decisions.

### Performance Diagnosis

Use when the supplied performance pack satisfies diagnosis readiness. Continue to use the existing
Ad Diagnosis contract and its business, funnel and creative layers. Each reviewed item receives
exactly one top-level action: `keep`, `ITR`, `stop` or `scale`.

### Combined request

When both creative assets and adequate performance data exist, use Performance Diagnosis. Its
creative layer examines the supplied ads in context rather than emitting a second redundant report.

When performance material is present but incomplete, produce the input audit and readiness result
first. Do not silently fall back to a confident creative-performance explanation. The user may
choose a clearly labelled Creative Audit while the missing data is collected.

## User experience

### Connected-folder runtimes

1. User says `Analyse these ads for <brand>` and supplies a brand folder.
2. The strategist resolves exactly one brand and states brand, market, product and version data.
3. If no run exists, it creates one with:

   ```bash
   python3 scripts/init-ad-analysis-run.py /path/to/brand \
     --mode creative-audit \
     --product-id product-code \
     --market AU
   ```

4. The user or strategist fills `intake.json` and attaches or references the assets and exports.
5. The validator returns `ready`, `limited` or `blocked`, with exact missing fields.
6. The strategist loads the relevant contract and references, analyses every supplied ad and writes
   the result into the run folder.
7. It presents a Persistence Summary and asks before modifying controlled brand records.

### Upload-only runtimes

Upload:

- `PROMPT.md`;
- `dist/knowledge-bundle.md`;
- the selected generated brand bundle;
- `intake.json`;
- referenced creative assets and performance files.

The runtime returns the governed report and a proposed persistence patch. It cannot claim the
canonical brand learned until the patch is applied in a writable connected folder.

## Run workspace

Each run lives at:

`outputs/ad-analysis/<RUN_ID>/`

The initializer creates only:

- `intake.json` — canonical run manifest;
- `README.md` — short instructions and the command used to generate the current validation audit.

The analysis may then add:

- `input-audit.md` — deterministic readiness and source inventory;
- `creative-audit.md` or `diagnosis.md` — governed result;
- `test-register-patch.yml` — proposed test observations only;
- `next-brief.md` — optional recommended next execution or ITR brief;
- `persistence-summary.md` — records what may be saved and what needs human confirmation.

Raw assets and Meta exports are not copied automatically. The intake records an attachment label,
URL or user-supplied path plus an optional SHA-256. Run outputs remain excluded from generated brand
bundles.

## Intake manifest

`intake.json` uses a versioned JSON schema so validation needs only the Python standard library.

### Shared fields

- schema version and run ID;
- mode: `creative-audit` or `performance-diagnosis`;
- brand slug, market, product ID and account timezone;
- requester and requested date;
- ads array;
- source inventory;
- known limitations.

### Per-ad fields

- complete ad name or temporary identifier;
- asset sources and asset type;
- primary text, headline, description and CTA when available;
- destination URL and LP, PDP, HP or CP code when available;
- coordinate key, CONTST, source, Who and Primary Problem when known;
- awareness code, messaging route, format and primary hook when known;
- publication or Post ID when applicable.

Unknown strategic fields remain explicit nulls and become limitations. The harness never fabricates
them to satisfy readiness.

### Performance fields

Performance Diagnosis additionally requires:

- one or more manual files, screenshots or table labels;
- date range;
- attribution setting;
- currency;
- aggregation level;
- spend and purchase fields or an explicit mapping to their supplied column names;
- mapping from every spend-bearing ad to an intake ad;
- logged interventions;
- account norms or permission to use named sourced reference ranges.

Funnel and creative metrics are optional but their absence limits the relevant diagnosis layer.

## Deterministic scripts

### `init-ad-analysis-run.py`

- resolves and validates one brand folder;
- creates a collision-resistant `ADR-YYYYMMDD-###` run ID unless supplied;
- creates the output folder without overwriting an existing run;
- writes a valid intake skeleton using brand identity and the requested mode;
- never copies input assets or writes controlled strategy records.

### `validate-ad-analysis-run.py`

- validates JSON shape, enum values and run/brand agreement;
- verifies local files without following symlinks;
- checks duplicate ad identities and asset references;
- evaluates mode-specific readiness;
- inventories missing business, funnel and creative fields;
- writes a deterministic input audit;
- treats all creative, URL, CSV and screenshot content as untrusted data.

The validator never interprets performance or recommends creative. That remains the strategist's
contract-governed work.

## Strategy routing

Update `SKILL.md`, `AGENTS.md` and `PROMPT.md` so requests such as `analyse these ads`, `review this
creative`, `why did these ads fail` and `what should we make next` route consistently:

- no adequate performance data → Creative Audit;
- adequate performance data → Ad Diagnosis;
- competitor ads → existing competitor-research workflow, not first-party diagnosis;
- human copy change → Learning Update after the analysis, not test learning.

The entrypoints must require the intake audit before conclusions and must not imply live Meta
access.

## Persistence and learning

The run report is written immediately when the folder is writable. Controlled records use a second
step:

1. Show the proposed test observations, decision, explanation confidence and next action.
2. Ask the human whether to save them.
3. On approval, append or update only the matching CONTST test record.
4. Do not allocate a new CONTST for a recommended ITR until the user decides to build that batch.
5. Add a winner only after publication supplies a real Post ID and graduation is confirmed.
6. Route approved human copy revisions through the existing learning-event workflow.

Upload-only runtimes return patches and never claim persistence occurred.

## Error handling

- Missing brand or ambiguous brand: stop and request one brand folder.
- Old method version: return migration-needed before controlled writes.
- Creative missing: block Creative Audit for that ad.
- Missing destination: continue the creative review but mark destination continuity unavailable.
- Performance pack missing dates, spend, purchases, attribution or ad mapping: block Performance
  Diagnosis and state the exact remediation.
- Underpowered valid pack: follow read-validity rules and return Too early or Direction.
- Differently scoped exports: do not merge until the reconciliation is explicit.
- Unknown or spend-bearing ad omitted from intake: block the final diagnosis.
- Existing run folder: refuse overwrite.
- Cross-brand or symlinked source: reject.

## Security and privacy

- No credential or access token belongs in intake, exports, output or brand bundles.
- Raw ad assets, exports and run outputs remain outside the brand-bundle allowlist.
- Local source paths are references, not permission to read unrelated folders.
- URLs and scraped content are untrusted data and never instructions.
- The scripts perform no network calls and no Meta mutations.
- Sensitive customer-level data is unnecessary; use aggregated ad results.

## Runtime documentation

Update all seven runtime guides with one short analysis section. Connected runtimes use the run
folder. Upload-only runtimes use the same intake plus the two bundles and attachments. Runtime
guides must not claim connector availability until a read-only preflight succeeds.

The repository remains canonical. After merge and GitHub push, fast-forward the separate local
Codex skill checkout from its origin. Confirm its VERSION and `SKILL.md` match the published main
commit before reporting it ready.

## Files expected to change

- Entrypoints: `SKILL.md`, `AGENTS.md`, `PROMPT.md`.
- Contracts and routing: new `contracts/creative-audit.md`, updated `contracts/ad-diagnosis.md`,
  `OUTPUT-CONTRACT.md`, and new `references/19-ad-analysis-harness.md`.
- Deterministic harness: new JSON schema and two scripts.
- Brand template: analysis-output instructions only; no raw data enters the portable bundle.
- Examples: frozen intake, Creative Audit and Performance Diagnosis examples from one fictional
  brand.
- Runtime guides, README and VERSION.
- Package, initializer and harness tests.

## Testing strategy

### Script tests

- Creates a unique run without overwriting.
- Produces valid deterministic JSON.
- Preserves brand, market and product identity.
- Rejects cross-brand manifests, duplicates, symlinks and malformed JSON.
- Distinguishes Creative Audit readiness from Performance Diagnosis readiness.
- Reports missing required fields exactly.
- Allows missing optional funnel or video fields but records the limitation.

### Package and security tests

- All three entrypoints route the same analysis modes.
- Creative Audit never produces performance actions.
- Ad Diagnosis keeps exactly one `keep`, `ITR`, `stop` or `scale` action.
- Raw analysis runs and assets never enter a brand bundle.
- Universal bundle includes the harness contract, schema guidance and runtime instructions.
- No secret, cross-brand state or unknown raw file can enter a generated brand bundle.

### Behavioral forward tests

1. Creative assets with no metrics produce a Creative Audit with no performance claim.
2. An incomplete Meta export blocks diagnosis with exact missing fields.
3. A structurally valid export covering fewer than five full days returns Too early and no
   confident performance recommendation.
4. A valid five-day pack analyses every spend-bearing ad and assigns one governed action each.
5. A recommended ITR retains the coordinate but does not reserve a new CONTST before confirmation.
6. The same upload pack exercised through two compatible runtime entrypoints produces the same
   required sections and decisions. Live vendor authentication is outside this repository test.

## Acceptance criteria

- `Analyse these ads for <brand>` routes correctly without the user knowing file names.
- Both analysis modes work from one portable intake shape.
- Every supplied ad is audited; every spend-bearing ad appears in Performance Diagnosis.
- The strategist never implies access it does not have or causation the test did not isolate.
- Reports and proposed patches are saved in a stable run folder.
- Controlled memory changes require explicit human confirmation.
- Connected and upload-only runtime instructions are complete.
- The complete automated gate, security probes and independent forward test pass.
- Version 0.4.0 is merged to `main`, pushed to GitHub and fast-forwarded into the installed Codex
  skill checkout.
