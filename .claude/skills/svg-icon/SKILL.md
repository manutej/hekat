---
name: svg-icon
description: Design, score and repair custom icon families as editable SVG under the FigTree icon rubric and family rules (24 grid, stroke 2, currentColor, round caps, at most 12 strokes, 2 px safe margin, no text, no fills). Use when someone asks for "an icon for X", "a set of icons for these concepts", "icons that match the library", "make the icon read at 16 px", "the icon looks like a blob / a kite / a balloon", "score this icon", "a contact sheet", or when a figure needs a block icon that the library lacks. Covers the brief format for `python -m figtree icon`, the cold-eye test at 16/24/48 px, metaphor orientation, and what the icon critic cannot see (sub-pixel detail, fused strokes, mirrored metaphors, ink in one corner). Not for illustrations, logos or brand marks.
---

# SVG icons: a family from briefs

An icon is a word a reader should not have to read. It must be recognisable at 16 px inside a
block, consistent with its siblings at 48 px in a legend, and drawable with a dozen strokes.
The icon rubric measures squareness, stroke widths, element count, text, overflow and, since
the icon adversary, the family rules (safe margin, coverage, subpath count, solid fills,
invisible shapes) and the 16 px legibility proxies (minimum feature size, minimum gap, crossing
density, ink distribution). **None of it sees whether the metaphor reads** (`icon.mirrored-magnifier`
still scores 10.0). The showcase family scored 10.0 on every round-1 icon and still needed a
second round for 7 of 12, because the defects only showed at 16 px (`examples/figtree/icons/NOTES.md`).

## The family contract

| Rule | Value | Enforced by |
|---|---|---|
| grid | `viewBox="0 0 24 24"`, square canvas | `medium.square` (critical, auto) |
| stroke | `stroke-width="2"`, `stroke="currentColor"`, `fill="none"`, round caps and joins | `polish.stroke_widths` (auto), `icon.solid_fill` |
| strokes | at most 12 shapes, counting `M` subpaths inside one `<path>` | `medium.icon_elements`, `icon.subpath_count` |
| safe margin | all ink inside 2..22 | `icon.safe_margin` |
| coverage | content bbox >= 40 % of the grid (aim ~70 %; flat metaphors by their long side) | `icon.coverage`; invisible shapes do not count (`icon.invisible_shape`) |
| text | none | `medium.icon_text` (critical, request) |
| colour | <= 2 palette colours; `currentColor` so it works on light and dark | `polish.palette_size` |
| corners | `rx <= 4` | `polish.corner_radius` (auto; a pill with rx = h/2 is exempt on icons) |
| markers / data-flow | never | `flow.*` is skipped for the icon medium; a marker is still not family style |
| transforms | avoid; author on the 24 grid with absolute coordinates | the bbox parser applies the full transform list and stroke width at HEAD (`icon.scaled-group`, `icon.stroke-clipped`, `icon.rotated-into-margin` in `icon-gotchas.md`) |

Family rules live in `figtree.quality.icon_family_issues` and run inside `QualityCritic` for
the icon rubric, so `figtree score --rubric icon` and `figtree eval` see them; `IconSmith`
(`python -m figtree icon`) adds the brief's own `max_strokes` and `must_read_at`.

## Brief, draw, score, look, repair

1. **Brief** one line per icon: `name: concept | metaphor` (`assets/icon-brief.md` has the
   fill-in form). Name the metaphor as a literal object ("a document with a magnifier"), name
   the library icon it should sit beside, and say what it must *not* look like.
2. **Draw** with the smith:
   ```bash
   python -m figtree icon "grounder: find evidence in the source | document with a magnifier" \
       "critic: review in code and image | eye over code brackets" \
       -o icons/ --backend claude --rounds 3 --sheet icons/sheet.svg --report icons/report.json
   ```
   The rule backend composes up to three primitives from metaphor words (page, lens, lines,
   box, arrow, arrows-cycle, node, branches, tick, pencil, spark, frame, wave); the Claude
   backend draws from the brief on the session's own login. Acceptance in the smith is >= 9.0;
   the showcase family required >= 9.5 after the cold-eye round.
3. **Look** at the sheet at 16, 24, 48 and 96 px on light and dark, nearest-neighbour upscaled
   beside true size (`references/icon-gotchas.md` has the render command). Ask of each icon:
   is it the object? which way does it face? do any two strokes fuse? is there a smudge? is the
   ink centred or in a corner? would I confuse it with a sibling?
4. **Repair** the inner markup by hand (`assets/icon.template.svg` is the document form) or
   with an edit script; re-score with `figtree score ICON.svg --rubric icon` and re-run the
   smith for the family rules. Write what changed per round in a NOTES table.
5. **Promote** accepted icons into `figtree/icons.py:ICONS` (and `ICON_KEYWORDS` if a role
   should pick them) so `generate --icons` can place them.

## Drawing rules that survived the cold eye

- Minimum feature (`icon.min_feature_size`): every stroke's extent must be >= ~1.5 device px at
  16 px, so >= 2.25 grid units; drop "text stubs" and 0.5 px details, they render as smudge.
- Minimum gap (`icon.min_gap`): centre distance minus stroke width >= 1 device px at 16 px
  (>= 3.5 grid units centre to centre). Two menu lines 2.5 apart fuse.
- No more than two strokes through one ~2 px cell (`icon.crossing_density`; an asterisk of four
  strokes is a blob).
- Orientation carries meaning and has no check: a magnifier handle goes down-right; a mirrored
  one reads as a balloon on a string. Keep chirality consistent with the library icon the brief
  names.
- Overlay a small object (lens, tick, pencil) at the lower right of a larger one (page, box),
  and keep >= 1.5 px of clearance between them (the merge icon's arrowhead was the first to
  soften at 16 px).
- Write multi-segment strokes as `<polyline>`/`<path>` with absolute commands; the first
  family's critic icon read as 29 % coverage until its relative `l` chains were rewritten as
  polylines (relative commands parse at HEAD; curves are still bounded by their endpoints).
- Keep ink balanced (`icon.ink_distribution`): a bbox of 56 % with all meaning in a 6x5 corner
  cluster is an L with a smudge at 16 px.
- Round dots are `M12 12h.01` with round caps (2 px dots), not tiny circles.

## Using icons in figures and pages

Emit as `<symbol id="icon-NAME" viewBox="0 0 24 24" fill="none" stroke="currentColor"
stroke-width="2" stroke-linecap="round" stroke-linejoin="round">` in `<defs>` and place with
`<use href="#icon-NAME" x= y= width="16" height="16" color="#2B3A4A">`; the figure's
`color` sets the stroke, so the same symbol works on light and dark pages. A sheet is itself a
figure (`assets/sheet.template.svg`): white background, 72 px cells, name and score under each.
When several figures share a page, namespace the symbol ids (`svg-showcase`).

## References and assets

- `references/rubric-icon.md`: thresholds, checks, vetoes, anchors from the live spec, plus the family rules.
- `references/icon-gotchas.md`: the 19 icon probes and the critic bugs they exposed, as eye checks.
- `assets/icon.template.svg`: one standalone icon document in family form.
- `assets/sheet.template.svg`: a contact sheet with symbol defs, cells, names and scores.
- `assets/icon-brief.md`: the fill-in brief for a draughtsman (rule, Claude or a subagent).
