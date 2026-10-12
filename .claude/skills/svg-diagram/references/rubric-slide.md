# Rubric: `slide` (Slide figure)

Generated from `figtree.rubric_spec.spec_for("slide")`; regenerate the JSON with
`python -m figtree eval --specs DIR`. A 16:9 fixed canvas read from the back of the room. The canvas is the medium: the critic centres content instead of shrinking the canvas; a centred figure may leave symmetric bands up to 34 % of the side (`max_centred_margin_ratio`), and content in a small centred block is asked to be *enlarged*.

Score it: `python -m figtree score FIG.svg --rubric slide [--source SRC.md] [--json]`.
Repair it: `python -m figtree refine FIG.svg --rubric slide -o out.svg --trajectory t.json [--edits edits.json]`.

## Thresholds

| threshold | value | enforced by |
|---|---|---|
| min_font | 18 px | `text.min_font` |
| min_contrast | 4.5:1 | `text.contrast` |
| max_palette | 4 accent fills | `polish.palette_size` |
| max_words_per_label | 6 | `text.words_per_label` |
| aspect | 1.6-1.9 (w/h) | `compactness.aspect` |
| margin | 32 px (blank band limit = max(margin+8, 0.15 x side)) | `compactness.blank_margin` |
| max_stroke_widths | 2 | `polish.stroke_widths` |
| max_font_families | 1 | `polish.font_families` |
| max_corner_radius | 8 px | `polish.corner_radius` |
| fixed_canvas | True | `center_content` instead of `set_canvas` |
| max_centred_margin_ratio | 0.34 of the side (symmetric bands tolerated on a fixed canvas) | `compactness.blank_margin` |
| flow_halo | 4 px | `flow.through_block` |



## Checks (what `figtree score` can see)

`auto = yes` means the critic attaches an `auto_edit` and `refine` applies it without asking;
`request` means the issue comes back anchored to an element id for a person or a VLM to decide.

| check id | dimension | severity | description | signal | auto |
|---|---|---|---|---|---|
| `compactness.blank_margin` | compactness | warning | a blank band wider than the medium's margin on any side | content bbox vs canvas | yes |
| `compactness.overflow` | compactness | critical | content outside the canvas | content bbox vs canvas | yes |
| `compactness.aspect` | compactness | warning | canvas aspect outside the medium's range (banner or tower) | width/height | request |
| `compactness.detour` | compactness | warning | a connector far longer than its displacement | path length / Manhattan distance | request |
| `flow.crossings` | flow_readability | warning | arrow crossings | orthogonal segment intersections | request |
| `flow.diagonal` | flow_readability | warning | diagonal routing without a semantic flag | segment orientation | request |
| `flow.through_block` | flow_readability | critical | an arrow passing through a block | segment vs block interiors | request |
| `flow.short_shaft` | flow_readability | warning | a marker-ended arrow with a shaft under 20px | final segment length | request |
| `flow.reading_order` | flow_readability | warning | most arrows run against reading order | share of right/down arrows | request |
| `flow.no_connectors` | flow_readability | warning | several blocks and no connectors | block and flow counts | request |
| `text.min_font` | text_quality | warning | font below the medium's minimum | resolved font-size | yes |
| `text.words_per_label` | text_quality | warning | a label longer than the medium allows | word count | request |
| `text.contrast` | text_quality | critical | text/background contrast below the threshold | WCAG ratio vs host fill | yes |
| `text.gradient_host` | text_quality | warning | text over a gradient or pattern fill | host fill is url() | request |
| `text.overflow` | text_quality | critical | a label wider than its block | estimated text width vs host block | request |
| `text.overlap` | text_quality | critical | two labels overlapping | text bbox intersection | request |
| `polish.font_families` | visual_polish | warning | more font families than allowed | distinct font-family values | yes |
| `polish.palette_size` | visual_polish | warning | more accent colours than allowed | distinct saturated fills | request |
| `polish.neon` | visual_polish | warning | a neon fill or stroke | saturation > 0.9 and max channel > 240 | yes |
| `polish.gradient_fill` | visual_polish | warning | a gradient or pattern fill | fill url() | yes |
| `polish.filter` | visual_polish | warning | a filter effect | filter attribute | yes |
| `polish.corner_radius` | visual_polish | warning | oversized corner radius | rx | yes |
| `polish.stroke_widths` | visual_polish | warning | more stroke widths than allowed | distinct stroke-width values | request |
| `medium.black_background` | medium_fit | critical | black background | full-canvas rect fill | yes |
| `coverage.plan_terms` | semantic_coverage | warning | planned components not labelled | plan terms vs labels | request |
| `hallucination.label_source` | hallucination_control | warning | a label with no basis in the source | label words vs source text | request |
| `topology.ungrouped` | topology_accuracy | warning | many blocks without grouping | block count vs containers | request |
| `topology.empty_container` | topology_accuracy | warning | an empty container | container children | yes |
| `content.none` | semantic_coverage | critical | nothing drawn | shape count | request |
| `medium.no_canvas` | medium_fit | critical | no canvas size | width/height/viewBox | request |
| `flow.collinear_overlap` | flow_readability | critical | two arrows sharing a collinear shaft (two heads, ambiguous endpoints) | collinear segment overlap > 8px | request |
| `flow.through_text` | flow_readability | critical | an arrow striking through a label | segment vs text bbox interior | request |
| `flow.semantic_direction` | flow_readability | critical | a sink that only emits or a source that only receives data (judge request) | role lexicon vs arrow endpoints | request |
| `text.sentence_label` | text_quality | critical | a label that is a sentence (trailing full stop or sentence opener) | label text | request |
| `text.duplicate_labels` | text_quality | warning | two blocks with the same label | case-folded hosted labels | request |
| `text.outlined_glyphs` | text_quality | critical | a block label drawn as path glyphs, not addressable text | small stroked paths inside a block with no text | request |
| `medium.embedded_title` | medium_fit | critical | a figure caption or title inside the drawing | text matching 'Figure N' / 'Table N' | request |
| `polish.invisible_elements` | visual_polish | warning | elements that draw nothing but stretch the content box | opacity 0, display none, no fill and no stroke, background-coloured | yes |
| `polish.decoration` | visual_polish | critical | overlapping ellipses with no label or connector (clip art) | unlabelled round shapes that intersect | request |
| `topology.container_label_mismatch` | topology_accuracy | critical | a container whose title names a block outside it (judge request) | container title stem vs child/outside labels | request |
| `layout.legend_in_drawing` | topology_accuracy | warning | a legend inside the block grid | legend bbox inside the union of blocks | request |
| `motion.pulse_direction` | flow_readability | critical | a token travelling from arrowhead to tail | offset-distance keyframes, animation-direction, path vs reversed flow | request |
| `motion.reveal_order` | flow_readability | warning | a target revealed before its source | reveal delays along data flows | request |
| `motion.control_tempo` | flow_readability | warning | a control token faster or as dark as data tokens | travel duration and fill luminance per token | request |
| `motion.reduced_motion` | medium_fit | critical | no (or an incomplete) prefers-reduced-motion block | @media (prefers-reduced-motion: reduce) rules | request |
| `motion.decorative` | visual_polish | warning | motion that encodes nothing | paths that are no flow, infinite/alternate on non-tokens, animated properties beyond opacity/dashoffset | request |

## Scoring

10 per dimension; a critical defect caps the dimension at 5; each further defect subtracts its penalty; floor 1; dimensions without evidence are not assessed; overall = weighted mean of assessed dimensions. Concretely: a dimension starts at 10; a critical defect sets it to 5 and
each further critical subtracts `max(0, penalty - 2)`; each warning subtracts its penalty; floor 1.
When any check behind a veto fires, `medium_fit` is capped at 7 (minus 1 per additional veto).
Dimensions with weight 0, or without evidence (`semantic_coverage` and `hallucination_control`
without `--source`), are reported as `n/a` and excluded from the overall.

## Vetoes (after PaperBananaBench)

A veto disqualifies the figure whatever else is good. A veto with no measurable check is a judge
question only: the measurable critic will score the figure 10.0 and you must catch it by eye.

| veto | description | detected by |
|---|---|---|
| textual_overload | full sentences or more than 15 words in a box; literal copying of the source | `text.words_per_label`, `text.sentence_label` |
| occlusion | overlapping elements or labels | `text.overlap`, `flow.through_block`, `flow.through_text`, `flow.collinear_overlap` |
| chaotic_routing | crossings and detours that defeat reading order | `flow.crossings`, `compactness.detour`, `flow.reading_order` |
| illegible_type | fonts below the medium's minimum or low contrast | `text.min_font`, `text.contrast`, `text.outlined_glyphs` |
| black_background | dark page background | `medium.black_background` |
| neon_or_gradient | jarring colour, gradients, filters | `polish.neon`, `polish.gradient_fill`, `polish.filter` |
| hallucination | elements with no basis in the source | `hallucination.label_source` |
| embedded_title_or_watermark | figure title or watermark inside the drawing (paper figures) | `medium.embedded_title` |
| clip_art | decorative, cartoonish or photorealistic elements | `polish.corner_radius`, `polish.decoration` |
| misleading_data | a chart that misstates the data: truncated bar axis, bars not to scale, dual axis, legend that names the wrong series | `chart.bar_axis_zero`, `chart.bar_scale`, `chart.dual_axis`, `chart.legend_swatch_colour` |
| motion_misleads | animation that runs against the flow or is lost to reduced-motion users | `motion.pulse_direction`, `motion.reduced_motion` |

## Dimensions and judge questions

| dimension | weight | judge question (image space) |
|---|---|---|
| semantic_coverage | 1 | Does the figure show the components and stages the source names, and the relationships between them? |
| hallucination_control | 1 | Is every visible element justified by the source? Flag invented modules, labels, branches or decoration. |
| topology_accuracy | 1 | Do grouping, hierarchy and containment match the structure of the method? |
| flow_readability | 1 | Can a cold reader follow the flow: arrow direction, endpoints, crossings, reading order, spacing? |
| text_quality | 1 | Are labels correct, legible at the intended size, well placed, consistent in font, not overflowing? |
| visual_polish | 1 | Is the palette restrained, strokes consistent, whitespace balanced, contrast adequate, no artifacts? |
| medium_fit | 1 | Does the figure follow the conventions of its medium (paper, teaching, slide, chart, tile, icon)? |
| compactness | 1 | Is the canvas used economically: margins, spacing, connector length, density balance? |

## Anchors (1-10)

| dimension | 1-2 | 3-4 | 5-6 | 7-8 | 9-10 |
|---|---|---|---|---|---|
| semantic_coverage | wrong topic or generic; almost no source-specific content | domain recognisable, most key components missing | main idea present, important mechanisms omitted or distorted | most concepts and relationships present, minor omissions | complete, source-specific coverage of stages and relationships |
| hallucination_control | mostly fabricated | major unsupported components alter the method | core idea recognisable, several invented details | minor embellishments or one wrong label | every important element is source-grounded |
| topology_accuracy | no coherent topology | severe structural mismatch | recognisable organisation with grouping errors | mostly correct, minor grouping or proportion issues | precise, publication-grade topology |
| flow_readability | flow unreadable; arrows missing, chaotic or misleading | major confusion from wrong arrows, crossings, overlaps, order | flow inferable but routing or spacing slows reading | clear flow with minor arrow or spacing imperfections | very clear, economical flow, no ambiguity |
| text_quality | illegible, garbled or mostly missing text | severe text errors or glyph deformation | readable with noticeable spelling, placement or blur defects | mostly correct and clean, minor local defects | accurate, sharp, well placed, typographically consistent |
| visual_polish | visually broken or unprofessional | messy composition, harsh or inconsistent styling | acceptable but visibly rough or unbalanced | polished with minor imperfections | highly polished and balanced |
| medium_fit | unsuitable for the medium | amateurish or wrong register for the medium | borderline; substantial cleanup needed | suitable with minor editing | fully aligned with the medium's conventions |
| compactness | content occupies a small fraction of the canvas | large blank margins or gaps; stretched connectors | usable but uneven density or oversized spacing | compact, mostly even, minor wasted space | economical, evenly distributed, no wasted area |

## Medium notes

- `fixed_canvas`: a blank band wider than max(32+8, 15 % of the side) asks for `center_content` when the content is off-centre; a centred figure may keep symmetric bands up to 34 % of the side (deck title/footer bands no longer fire: probe `slide.breathing_room` is silent).
- Labels of at most 6 words at >= 18 px; palette of at most 4 accents.
