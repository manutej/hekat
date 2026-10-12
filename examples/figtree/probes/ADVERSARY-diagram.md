# Adversary report: diagram rubrics (teaching, slide, methodology)

Probes live in `teaching/`, `slide/` and `methodology/` as `<slug>.svg` + `<slug>.json`
(`"source": "adversary-diagram"`, ids `<rubric>.<slug>`). Every SVG is standalone house style
(Times New Roman, #7BA3C9 blocks, #333333 1.2px strokes, white background rect first, every
element with an id, no scripts). Each probe was rendered with the chromium backend and
inspected; real glyph widths were measured with Liberation Serif (metric-compatible with Times).

Measured against `figtree/quality.py` at HEAD `f47ddaf` (which already detects collinear
overlap under `flow.crossings`, gates `compactness.aspect` at page scale, and caps `medium_fit`
at 7 when a veto check fires).

## Eval summary

```
$ python -m figtree eval --rubric teaching
52 probes, recall 0.542, precision 0.765, missed 22, false positives 8
$ python -m figtree eval --rubric slide
4 probes, recall 1.0, precision 0.667, missed 0, false positives 1
$ python -m figtree eval --rubric methodology
1 probes, recall 0.0, precision None, missed 1, false positives 0
```

The teaching set is seed (21) + this adversary (24) + the icon/motion adversaries' teaching
probes (7). Gaming probes list what *should* fire, so each one counts as a miss by design: of the
22 teaching misses, 17 are gaming expectations (`proposed.*` or an existing id that needs a rule
change) and 2 are genuine misses of existing checks (`overflow_inherited_font`,
`polyline_arrows`); the remaining 3 belong to seed/sibling probes. All 14 gaming probes score
>= 9.0 (13 of them a flat 10.0), i.e. the measurable critic is fooled on every one.

## Probe table

| id | kind | what a cold reader sees | what the critic did | proposed check / rule change | severity |
|---|---|---|---|---|---|
| teaching.edge_hugging_arrow | gaming | Reader->Printer arrow drawn along Parser's top border; the head lands on Printer's corner, so one line touches three boxes | silent, 10.0 | `flow.through_block`: test segments against block boxes inflated by a halo (>= 4px, or the marker height) and count a segment collinear with a block edge as a hit | critical (occlusion veto) |
| teaching.arrow_exits_through_source | gaming | Reader->Parser starts on Reader's far border and slices through Reader; Output->Logger likewise through Output | silent, 10.0 | `flow.through_block`: do not drop a block from the obstacles because an endpoint touches it; clip the first/last segment at the port and test the remainder (or require the endpoint on the facing side) | critical (occlusion veto) |
| teaching.wide_glyph_overflow | gaming | WORKFLOW MANAGER / DOWNSTREAM MODEL (16 caps, 14px) spill ~40px past their 112px blocks | silent, 10.0 (estimate = exactly 112px) | `text.overflow`: replace the 0.5em/char estimate with a per-glyph width table (caps ~0.7em, i/l/t ~0.3em, digits 0.5em) or measure with a metric-compatible font; measured 156.5px and 153.6px | critical |
| teaching.backwards_semantics | gaming | Report->Analysis->Raw data, Dashboard->Charts->Sensors with all heads pointing right | silent, forward_ratio 1.0 | `proposed.flow.semantic_direction`: a role lexicon (raw/input/source/sensor = source; report/output/result/dashboard = sink); a sink with outgoing data arrows or a source with incoming ones becomes a judge request | critical (judge) |
| teaching.legend_inside_drawing | gaming | the legend box occupies row 2 of the grid, level with Deploy, and reads as a fourth stage | silent, 10.0 | `proposed.layout.legend_in_drawing`: a legend-like group (`data-role=legend`, or >= 2 swatch+label pairs) whose bbox lies inside the convex hull of the block grid rather than in a margin | warning |
| teaching.text_as_paths | gaming | all six labels are 8px-tall stroked path glyphs; no `<text>` exists | silent, 10.0 (every text check passes vacuously) | `proposed.text.outlined_glyphs`: a block with no text descendant/overlapping label, or a cluster of >= 3 small paths (< 12px tall) inside a block -> "label is not addressable text"; feed the cluster height into `text.min_font` | critical |
| teaching.invisible_coverage | gaming | two blocks in 7% of a 640x320 canvas; a white-on-white rect and an opacity-0 text stretch the bbox to a neat 24px margin | silent, 10.0 | `compactness.blank_margin`: build the content bbox from visible elements only (opacity 0, display none, fill none & stroke none, fill == background); add `proposed.polish.invisible_elements` | warning (compactness anchor 1-2) |
| teaching.prose_transcription | gaming | six boxes each holding one full sentence over two tspans, chained boustrophedon: the prose with borders | silent, 10.0 (<= 8 words per label) | `proposed.text.sentence_label` (textual_overload veto): label ends with '.', starts with an article/conjunction/adverb, or total label words / blocks > 6 | veto |
| teaching.duplicate_labels | gaming | two 'Filter' and two 'Merge' blocks; same component twice or two different ones? | silent, 10.0 | `proposed.text.duplicate_labels`: identical case-folded block labels | warning |
| teaching.decorative_clipart | gaming | three overlapping grey ellipses as a 'cloud' with no label and no connector | silent, 10.0 (only rect rx is a clip-art signal) | `proposed.polish.decoration` (clip_art veto): shapes with no text inside and no flow endpoint; >= 2 mutually overlapping ellipses/circles | veto |
| teaching.misleading_grouping | gaming | container titled 'Training' holds Deploy and Monitor while Train sits outside | silent, 10.0 | `proposed.topology.container_label_mismatch`: judge question; measurable proxy: the container label's token appears in an outside block label and in none of its children | critical (judge) |
| teaching.arrow_through_text | gaming | annotation 'on a miss' centred on the Cache->Origin shaft, struck through | silent, 10.0 | `proposed.flow.through_text`: treat text bboxes as flow obstacles (segment vs text bbox) | critical (occlusion) |
| teaching.up_arrows_jog_right | gaming | both columns read Input->Compute->Result bottom-up; each arrow has an 8px rightward jog before a 24px climb | silent, forward_ratio 1.0 | `flow.reading_order`: classify each arrow by its dominant axis (|dx| vs |dy|) and the sign on that axis, not "right OR down" | warning |
| methodology.embedded_title | gaming | 'Figure 2: Overview of the autoencoder pipeline.' inside the canvas | silent, 10.0 (veto has no check) | `proposed.medium.embedded_title`: text matching `^(Figure|Fig\.|Table)\s*\d`, or large low-contrast/rotated text (watermark) | veto |
| teaching.semantic_diagonal | false_positive | fan-in with a `data-diagonal="semantic"` diagonal across empty canvas | `flow.through_block` fired for Docs and Index; overall 8.67 | `segment_hits_box` returns True for every diagonal against every box; implement a real segment/box intersection (Liang-Barsky) | critical FP |
| teaching.narrow_tower | false_positive | six-step strictly vertical process at page scale (192x528) | `compactness.aspect` fired; overall 9.75 | skip the aspect rule when every flow is vertical (tower) or horizontal (banner), or widen teaching to 1/2.4..2.4 | warning FP |
| teaching.tspan_multiline | false_positive | house-style two-line labels, x/y on `<text>` and tspans | silent, 10.0 | regression guard for the tspan bbox (longest line, not the joined string) | - |
| teaching.tspan_no_text_y | false_positive | identical rendering, but the coordinates live only on the tspans (editor export) | `text.overlap` x many + `compactness.overflow`; overall 7.5 | `element_bbox`: when `<text>` has no x/y take them from the first tspan; use the union of per-tspan bboxes | critical FP |
| teaching.narrow_glyph_fit | false_positive | 'Initialisation' (71px real) in an 88px block, 'Illustration' (61px) in 76px | `text.overflow` fired; overall 9.17 | same glyph-width table as wide_glyph_overflow (the two probes bracket the estimator) | critical FP |
| slide.breathing_room | false_positive | five-block pipeline centred on 16:9 with symmetric 96px (27%) bands for the deck's title and footer | `compactness.blank_margin` x2, "enlarge the content to fill the canvas"; overall 9.67 | fixed canvas: tolerate symmetric (centred) margins up to ~1/3 of the side; flag only asymmetric bands | warning FP |
| teaching.through_block_nested | defect | arrow through a block inside a `translate()` group | fired | regression guard for offset resolution | - |
| teaching.overflow_inherited_font | defect | 'Preprocessing' inherits 24px from its group; 135px in a 112px block | MISSED, 10.0 (bbox computed at the 12px default) | `element_bbox` must use the resolved font-size (inherited + `style=`), which `load_program` already computes for `text.min_font` | critical miss |
| teaching.inherited_style_defects | defect | #999999 fill inherited from a group on a blue block; two labels overlapped via group transforms | both fired | regression guard for inherited fill and transforms | - |
| teaching.polyline_arrows | defect | Fetch->Render through Cache drawn as `<polyline>` (draw.io / Inkscape output) | MISSED `flow.through_block`; `flow.reading_order` fired falsely (empty routes count as backward) | `load_program`: parse `points` for polyline/polygon flows; exclude flows with no points from forward_ratio | critical miss + warning FP |
| teaching.crossing_midline | defect | one proper X crossing with no shared endpoints | fired | regression guard; the seed `defect.crossing` is a T-junction + collinear overlap, not an X | - |
| teaching.collinear_arrows | defect | Fetch->Store and Parse->Index share a vertical shaft: an H shape with two heads, endpoints ambiguous | `flow.crossings` fired as "1 arrow crossing(s)", 0.7 penalty, overall 9.38 | give collinear overlap its own id/message (`proposed.flow.collinear_overlap`) and critical severity; the figure is unreadable yet scores 9.38 | critical (under-penalised) |
| slide.small_font_in_group | defect | 14px labels, one inherited from a group, one via `style=` | fired (also `blank_margin`, expected on a bare slide) | regression guard for inheritance and style resolution at the slide minimum | - |
| teaching.use_icons_clean | clean | house-style Z pipeline with a `<use>` icon in every block and a free-standing loop icon | silent, 10.0 | `<use>` instances and `<symbol>` contents are correctly ignored as blocks/text | - |

## Observations beyond the table

- **Score saturation.** Thirteen of fourteen gaming figures score a flat 10.0: with no source or
  plan, `semantic_coverage` and `hallucination_control` are unassessed, so a figure that is
  geometrically tidy and semantically wrong is indistinguishable from a good one. The veto cap on
  `medium_fit` only applies when a *measurable* check fires, so none of the judge-only vetoes
  (clip art, textual overload, embedded title, decoration) ever reach it.
- **Endpoint exclusion is the dominant through-block hole.** Three probes (`edge_hugging_arrow`,
  `arrow_exits_through_source`, `arrow_through_text`) defeat occlusion detection by touching a
  boundary, by sharing an endpoint, or by not being a block at all. A halo plus clipping at the
  port fixes the first two in one place.
- **The 0.5em estimator is wrong in both directions.** Measured widths: caps run 0.65-0.72em
  (`WORKFLOW MANAGER` 156px vs 112 estimated), narrow lower-case runs 0.36-0.45em
  (`Initialisation` 71px vs 98). A 95-entry width table for the house font removes both the
  gaming and the false positive; `overflow_inherited_font` additionally needs the resolved size.
- **Snake layouts trip `flow.reading_order`.** The first draft of the clean probe was a 2x3 snake
  (row 2 reads right-to-left back to the start) and fired reading_order at forward_ratio 0.5; a
  ring or snake laid out as a closed cycle always has about half its arrows against reading
  order, so the 0.6 threshold should be evaluated per row/column or on the dominant axis.
- **Polylines are invisible.** `is_flow` accepts polylines but `load_program` never fills their
  points, so every flow check (through-block, crossings, diagonal, short shaft, detour) is blind
  to them and reading_order counts them as backward.
- **File naming.** The task text said `<id>.svg`; the sibling adversaries use `<slug>.svg`, so
  this set follows the directory convention (the `id` field in the JSON is authoritative).
