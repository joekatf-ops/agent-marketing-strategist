# Saved-ad layouts

Use this with saved ads or a request to match a layout. References constrain visual choices;
they do not establish sales performance or become prerequisites for original creative.

## Find the right reference

Start from the message and facts already resolved in the image workflow. Keep angle, awareness,
format and layout separate: one angle can use several formats, and a layout can serve different
awareness levels after the argument changes. Do not let an attractive reference change an angle
the user has chosen.

Use this order, adjusted to the request:
1. The exact ad or board the user selected.
2. Relevant own-brand creative with supplied performance evidence, when available.
3. The user's saved brand and general inspiration boards through Foreplay.
4. Foreplay Discovery or another available ad library to fill a specific gap.
5. An original layout based on the product facts.

Use `connectors/foreplay.md` for current access. Start with a small bounded sample, such as 6 to 12
static candidates for a four-concept batch. This is a working limit, not a required count. Fetch
more only if the set lacks a suitable layout. Follow returned pagination; a short filtered page
does not prove a board is exhausted. Do not fetch the same ads again through both API and MCP.

Search by communication job and format as well as category: a notes list, product annotation,
single objection, comparison grid or three-step demonstration may transfer across industries.
Exclude duplicates and irrelevant matches. Do not choose a reference solely because it ran a long
time, was saved often, looks polished or sits on a board named "best ads".

## Inspect, then choose

Retrieve and visually inspect the actual creative. Titles, transcripts, automated tags and
thumbnails with unreadable text cannot establish a detailed layout. Use the provider's returned
media and source URLs. When inspection is impossible, record that limit and use an original
layout unless exact adaptation is essential.

Choose one primary composition per concept. Add references only for distinct roles such as
lighting, product identity or logo. Avoid an undifferentiated pile of ads.

Use `contracts/reference-analysis.md` to record:
- Source ID, board when relevant, source link, inspected media, observation date and access limits.
- Format, reading order, headline location, product or subject scale, contrast, whitespace,
  alignment, type hierarchy, text density and proof objects actually visible.
- Why this structure suits the selected message and available product assets.
- What to retain, replace, remove and add. Use the active brand's identity and supported facts.
- The corresponding square and vertical compositions, including elements that must remain visible.

Prefer a reference whose copy length, product depiction and available evidence fit the brief.
A testimonial or statistics layout is unsuitable without the necessary proof. A news-style visual
does not give permission to imply independent reporting, medical authority or an actual news event.

## Generate and compare

Where supported, pass the inspected reference image to the model as composition guidance and
the real product photos as identity guidance. If the model cannot receive the layout image, use
an explicit description of the inspected layout and record this weaker transfer route.

Match visual relationships, not foreign brand assets: headline prominence, balance between image
and copy, sequence, spacing and product scale. Reflow those relationships for 9:16 while keeping
the same message and brand type treatment as 1:1. Preserve accurate product pixels when exact
hardware or construction matters and compositing tools are available.

Review the reference and output side by side at comparable display size, then review the two
output ratios at phone width. A spelling pass cannot catch an undersized subject, empty lower
canvas, dense supporting text or a change of typography. Correct the specific deviation and
record material departures from the reference.

## Keep the library useful

Retain source ID/URL, format, message job, inspection date, selected layout features, output
filenames and review outcome. Cache media when allowed; retain provenance. Never store credentials.

Separate four states: saved for inspiration, visually reviewed, approved for adaptation, and
supported by measured performance. Customer research informs the message; saved ads inform
execution. Neither substitutes for the other's evidence. Performance needs the actual metric,
source, date window, spend or exposure and limitations. Do not turn competitor longevity or
model-generated scores into ROAS, profitability or causal evidence.

Keep cross-brand layout patterns in the general library and brand facts, claims and performance
in their own brand records. Writing or reorganising external boards is a separate action from
reading them; preserve existing board contents unless the user asks for library management.
