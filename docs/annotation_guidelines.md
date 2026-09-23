# Annotation Guidelines — CBERS-4A Pampa Land Cover

**Version 1.0.1 — ready for the calibration round, not for production.** Annotate the six pilot
tiles (§7) on this version, independently and before any group discussion, then it gets
revised. Record which version you worked under.

> **Changed in 1.0.1 (2026-09-08):** tree plantation is **Forest**, not Agriculture. This
> reverses the rule stated in 1.0. Nothing else changed. See the note in §3b.

---

## 1. What this is and why the rules are strict

You are labelling every pixel of satellite tiles into the **7 DeepGlobe land cover classes**.
The labels fine-tune a model pretrained on DeepGlobe, which then produces a
**movement-difficulty map** of the Pampa biome for the Brazilian Army — how hard terrain is to
traverse. A boundary drawn differently by two annotators becomes noise the model averages over.

The class set is **fixed by DeepGlobe** and cannot change. Matching their 7 classes with their
meanings is the entire reason the pretrained weights transfer. **Do not invent, split or rename
classes**, and do not label to a finer scheme even where you can see finer distinctions.

This is a **prescriptive** task: one standard, applied by everyone. Where you disagree with a
rule, follow it and log it (§6) — do not quietly annotate to your own preference. Disagreement
between annotators is treated as a defect in *these guidelines* first, not as your error, which
is why reporting it matters more than resolving it yourself.

**Where our judgement and DeepGlobe's wording conflict, DeepGlobe wins.** Several rules below
are arguable both ways on movement-difficulty grounds. In those cases we follow the source
dataset's literal definition, because consistency with what the pretrained model already
learned is worth more than winning the argument.

## 2. What you receive

- **PNG tiles, 1024 x 1024 px, 2 m/px = 2,048 x 2,048 m** (419.4 ha). Roughly a 2 km square.
- **8-bit RGB only.** No near-infrared. You cannot use NIR to confirm water or judge vegetation
  vigour — work from visible colour, texture, shape and context. (The base model is RGB too, so
  this is a deliberate match, not a limitation to work around.)
- **Pansharpened** CBERS-4A WPM: 2 m panchromatic fused with 8 m colour. Expect crisp edges but
  slightly soft and occasionally odd colour, plus fusion artefacts at high-contrast boundaries
  such as bridges and shorelines. Artefacts are not a class.
- Every tile is **fully covered by imagery**. Black or empty pixels mean the tile is broken —
  stop and report it (§6).
- Tiles come from **44 scenes acquired 2020-2026**, mostly winter and spring. Brightness, sun
  angle and season vary between tiles. **Do not compare brightness across tiles.**

## 3. The 7 classes

Mask colours (`CLASS_MAP` in `Segmentation_DeepGlobe_UNet.ipynb`):

| # | Class | RGB | colour |
|---|---|---|---|
| 1 | Urban | 0, 255, 255 | cyan |
| 2 | Agriculture | 255, 255, 0 | yellow |
| 3 | Rangeland | 255, 0, 255 | magenta |
| 4 | Forest | 0, 255, 0 | green |
| 5 | Water | 0, 0, 255 | blue |
| 6 | Barren | 255, 255, 255 | white |
| 7 | Unknown | 0, 0, 0 | black |

Every pixel gets exactly one class.

**DeepGlobe's own definitions, verbatim — these are the authority:**

> **Urban land** — "Man-made, built up areas with human artifacts (can ignore roads for now
> which is hard to label)"
> **Agriculture land** — "Farms, any planned (i.e. regular) plantation, cropland, orchards,
> vineyards, nurseries, and ornamental horticultural areas; confined feeding operations."
> **Rangeland** — "Any non-forest, non-farm, green land, grass"
> **Forest land** — "Any land with x% tree crown density plus clearcuts."
> **Water** — "Rivers, oceans, lakes, wetland, ponds."
> **Barren land** — "Mountain, land, rock, dessert, beach, no vegetation"
> **Unknown** — "Clouds and others"

**The organising idea, which resolves most cases:** what puts something in Forest is **canopy
closure, not naturalness** — DeepGlobe defines Forest by crown density, saying nothing about who
planted the trees. Continuous closed woody canopy is Forest, natural or planted, **tree
plantations included**. Regular planted patterns that do *not* close into woody canopy — crops,
orchards, vineyards, nurseries — are Agriculture. Rangeland is the **residual**: green, not
forest, not farm. Barren is unvegetated. Water includes wetland.

### 1. Urban
- **Is:** cities, towns, villages, industrial and commercial sites, airports and runways, paved
  areas, large isolated structures, solar farms, dams. Streets and small green spaces *inside*
  the built fabric are Urban.
- **Is not:** roads outside a built-up area (§5 — not labelled at all), a mining pit (§5).

### 2. Agriculture
- **Is:** row crops, soybean, rice paddies when not standing in water, ploughed and fallow
  fields, orchards, vineyards, nurseries, mosaics of small fields, centre-pivot circles.
  Anything planted in a regular, planned pattern that does not close into woody canopy.
- **Is not:** grazing land with no cultivation pattern (Rangeland), any closed tree canopy
  **including tree plantations** (Forest, §3b), paddies currently under water (Water, §5).
- The largest class in this dataset.

### 3. Rangeland
The residual green class: *"any non-forest, non-farm, green land, grass"*.
- **Is:** natural grassland (*campo*), grazed grassland, shrubland, grass with scattered
  isolated trees. **A lone tree or a few scattered trees over grass is Rangeland, not Forest.**
- **Is not:** cultivated or planted land (Agriculture), continuous natural canopy (Forest),
  unvegetated ground (Barren), marsh and wetland (**Water** — see §5).

### 4. Forest
Woody cover with continuous, closed canopy — whether it grew naturally or was planted.
- **Is:** native forest, woodland, riparian and floodable forest, mangrove, wooded coastal
  scrub, clearcuts within forest, and **tree plantations (eucalyptus, pine)** — see §3b.
- **Is not:** orchards, vineyards and nurseries (Agriculture — discrete crowns with ground
  visible between them, worked as a crop), isolated or scattered trees over grass (Rangeland),
  shrubland with no canopy (Rangeland).

### 5. Water
- **Is:** lagoons, rivers, streams, canals, reservoirs, farm ponds, aquaculture ponds, ocean,
  **marsh and wetland**, **rice paddies while standing in water**, and **mining pools and
  tailings ponds**.
- DeepGlobe lists wetland under Water explicitly, which is why marsh is here and not in
  Rangeland.

### 6. Barren
- **Is:** beaches, dunes, sand sheets and *areais*, shorelines, tidal flats, exposed bedrock,
  rock pavement, scarps and cliffs, boulder fields, bare eroded ground with no field geometry,
  and **the exposed ground of a mining site**.
- **Is not:** bare ploughed fields (Agriculture — field geometry is the evidence), bare ground
  inside a built-up area (Urban).
- **The scarcest class and the easiest to overlook.** Check deliberately for unvegetated ground
  rather than concluding a tile has none. Barren has **no minimum size** (§4).

### 7. Unknown — surface not observable
DeepGlobe's definition is *"clouds and others"*. Reserve it for pixels where **you cannot see
the ground**, never for pixels where you cannot decide what it is.
- **Use for:** cloud, shadow dense enough to hide the surface, thick haze, image corruption.
- **Do not use for:** a hard boundary, a difficult patch, or a genuine tie between classes you
  *can* see. **Ties get a forced pick plus a log entry** (§6), never Unknown.

**Why this is strict.** Unknown is a **normal training class** here — verified in
`Segmentation_DeepGlobe_UNet.ipynb`: 7-way softmax, `bce_dice_loss` over all 7, no ignore index.
So the model learns to predict it. Label ambiguous *terrain* Unknown and the model outputs
Unknown on ambiguous terrain, which becomes a **hole in the movement-difficulty map**. It also
consumes the same model capacity as Forest, and every Unknown pixel is area removed from the
without-Unknown metric. Used correctly, for genuine cloud, it is right and cheap.

Tiles were selected for low cloud, so Unknown should be rare. Frequent use is a signal to
raise (§6), not a workflow.

### 3b. Deciding between confusable pairs

Each row gives the visual cue that decides it.

| Looks like it could be | Decide by | Answer |
|---|---|---|
| **Regular tree array** — plantation rows | **Canopy closure.** Crowns touching, ground hidden, uniform height and age. | **Forest.** DeepGlobe defines Forest by tree crown density, which a plantation block satisfies. See the note below. |
| **Natural woodland** | Irregular canopy, mixed crown sizes, boundaries following terrain or watercourses. | **Forest.** |
| **Grazed grassland vs cropland** | **Surface pattern.** Parallel or curved cultivation lines, tillage marks, uniform tone within a straight-edged parcel -> cultivated. Smooth or mottled texture, irregular boundaries following terrain -> grazing. | Cultivated = **Agriculture**; grazed = **Rangeland**. |
| **Bare ploughed field vs bare ground** | **Field geometry.** A straight-edged rectangle inside a farmed mosaic is a field, whatever its colour. | Field = **Agriculture**; no field geometry = **Barren**. |
| **Rice paddy** | **Is it under water right now?** | Standing water = **Water**; dry or cropped = **Agriculture**. Label the date you see. |
| **Marsh / wetland** | Vegetated but waterlogged, mottled, often with visible standing water between vegetation. | **Water** — DeepGlobe puts wetland under Water. |
| **Scattered trees vs forest** | **Canopy continuity.** Individual crowns with grass visible between them -> Rangeland. Crowns touching, ground hidden -> Forest. | |
| **Sparse vegetation on sand** | Which dominates the surface. | Sand dominant = **Barren**; vegetation dominant = **Rangeland**. |
| **Mining site** | **Label by surface, not as one unit.** | Pit floor, benches, spoil, haul roads = **Barren**; pools and tailings = **Water**; plant and buildings = **Urban**. |
| **Construction site vs bare ground** | Structures present. | With buildings/roads = **Urban**; without = **Barren**. |
| **Shoreline** | Sand or flat at the water's edge is still land. | **Barren** to the waterline, **Water** beyond. |

**Note on tree plantations — a deliberately arbitrary call.** Eucalyptus and pine blocks satisfy
*both* DeepGlobe definitions: they have high tree crown density (Forest) and they are a planned
regular plantation (Agriculture). Movement difficulty does not settle it either — trunks obstruct
like forest, but the corridors between planted rows are easier to cross than natural forest.
Inspection of DeepGlobe training masks did not turn up a clear plantation example to confirm how
their annotators actually handled it, so no empirical answer was available.

We call it **Forest**, on the ground that DeepGlobe's Forest definition is a *measurable*
property of the image — crown density — while its Agriculture wording turns on intent, which is
not visible in a 2 m pixel. This also keeps the label consistent with the MapBiomas stratum the
tiles were sampled from, where plantation sits inside Forest. It is a convention chosen for
consistency, not a discovered fact. **Apply it uniformly** — an arbitrary rule applied
consistently costs far less than a defensible rule applied three different ways.

## 4. Geometry and precision

**The unit of work is one whole tile.** One mask per 1024 x 1024 tile; a tile is finished or it
is not.

**Sweep the tile systematically.** Work across it in a grid at high zoom, covering every part
once, rather than scanning the whole tile at low zoom and then zooming to whatever caught your
eye. Scarce classes are detected far better when attention is forced over small regions in turn.
This matters most for Barren.

**Minimum mapping unit: 400 m² (a 20 x 20 m patch, 100 px).** Do not label features smaller than
this; absorb them into the surrounding class.
- **Barren is exempt** — no minimum. It is the scarcest class and every instance matters.
- This is deliberately generous. DeepGlobe states its own labels are *"far from perfect due to
  the cost for annotating multi-class segmentation mask"*, so labelling finer than the data the
  pretrained features came from buys nothing.

**Boundary tracing.** Trace the edge you can see, at 100% zoom or closer. Where an edge is
gradational over several pixels, **put the line in the middle of the transition**.
- There is no pixel-count tolerance to hit. What matters is avoiding **systematic bias** — random
  scatter between annotators largely cancels under majority vote, whereas one annotator
  consistently tracing tighter than another does not.
- Boundary error only really costs accuracy on *small* polygons, which is the other reason the
  minimum mapping unit above is generous.

**No gaps, no overlaps.** Every pixel gets exactly one class, out to the tile border.

## 5. Edge cases — decided in advance, do not re-litigate

| Situation | Decision |
|---|---|
| **Roads outside a built-up area** | **Not labelled at all** — absorb into the surrounding class. DeepGlobe excluded roads deliberately ("can ignore roads for now which is hard to label"), covering them in a separate challenge, so the pretrained model never learned them. A dirt track through grassland is **Rangeland**. |
| **Roads inside a town** | **Urban** — part of the built fabric. |
| **A lone tree, or a few scattered trees, over grass** | **Rangeland.** Forest is a canopy-density class; one tree is not a density. |
| **Tree plantation (eucalyptus, pine)** | **Forest** — see the note in §3b. |
| **Orchard / vineyard / nursery** | **Agriculture.** |
| **Flooded rice paddy** | **Water** while under water; **Agriculture** when dry or cropped. Label the date you see. |
| **Marsh / wetland** | **Water.** |
| **Reservoir behind a dam** | **Water**; the dam structure **Urban**. |
| **Quarry / open pit / sand extraction** | **By surface:** pit floor, benches, spoil, haul roads -> **Barren**; pools and tailings -> **Water**; plant and buildings -> **Urban**. Do not outline the site as one class. |
| **Natural rock outcrop** | **Barren**, even if a track crosses it. |
| **Bare ploughed field** | **Agriculture** — field geometry is the evidence. |
| **Bare eroded soil in grassland, no field geometry** | **Barren** if unvegetated; **Rangeland** if vegetation persists. |
| **Urban park / green space inside a city** | **Urban** if embedded in the fabric; **Forest** or **Rangeland** only for a large distinct natural area at the city edge. |
| **Aquaculture ponds** | **Water.** |
| **Sand bar mid-river** | **Barren.** |
| **Beach with sparse vegetation** | **Barren** if sand dominates; **Rangeland** if herbaceous cover dominates. |
| **Airport runway / solar plant** | **Urban.** |
| **Cloud or dense haze** | **Unknown** only if the surface is genuinely invisible. |
| **Shadow** | Label the **underlying surface**. Shadow is not a class and not Unknown. |
| **Genuine tie between two visible classes** | **Pick one and log it** (§6). Never Unknown. |
| **Tile edge cuts a feature** | Label the visible part normally; do not infer beyond the tile. |
| **Classes interleaved below the minimum unit** | Label the **dominant** class across the patch. |

## 6. How we work together

**Annotate independently. Do not look at anyone else's labels for a tile you are also labelling,
and do not discuss specific tiles while annotation is open.** Some tiles are deliberately
assigned to more than one of you so agreement can be measured; that measurement is worthless if
you coordinated. Evidence from remote-sensing annotation experiments is that independent
annotation aggregated by **majority vote outperforms sequential review** of each other's work.

**Do discuss the guidelines.** Between rounds we walk through every disagreement and revise this
document. That is the mechanism for resolving conflict, not per-tile negotiation.

**Seniority does not apply.** Experience has been measured not to improve accuracy in this kind
of task, and up-weighting experienced annotators' votes made results *worse*. Nobody's label
overrides anybody's, including mine.

**Two separate channels, and the split matters.**

- **Your issue log — private, seen only by the coordinator.** Anything tied to a specific tile:
  a rule that does not cover what you are looking at, a tile you suspect is broken, every use of
  **Unknown** with a one-line reason, and any case where you nearly used Unknown but guessed
  instead. Name the tile.
- **The clarifications document — shared, everyone reads it.** The coordinator turns issues into
  general rules and appends them here, phrased without tile identifiers.

You do **not** see each other's issue logs. Guideline knowledge has to be shared or we cannot be
consistent; tile-specific observations must not be, or the agreement measurement is contaminated.

**Never wait on a clarification.** Hit something uncovered, decide, log it, keep going.
Clarifications publish between rounds. If one lands that changes a tile you finished, say so —
at this scale re-annotating is cheap, which is why §1 asks for the version stamp.

**Do not consult external sources for a specific tile** — no Google Earth, no other imagery
dates, no existing land cover maps. The model will only ever see this one image, so labels must
be derivable from it.

**You will not be shown any pre-existing land cover map.** One exists at much coarser resolution
and is deliberately withheld — anchoring your work to coarse labels would defeat the purpose of
annotating at 2 m. It is used only for after-the-fact quality checks.

## 7. Calibration round — do this before production

Six tiles, chosen from **outside** the production set so their labels are disposable, each
stressing one contested rule. All three annotators label all six, independently.

| tile | what it tests |
|---|---|
| `CBERS_4A_WPM_20210827_211_150_L4_37_52` | Agriculture/Rangeland mix (70/30) |
| `CBERS_4A_WPM_20250708_214_151_L4_35_23` | Agriculture/Rangeland mix (25/74) |
| `CBERS_4A_WPM_20230704_206_151_L4_17_42` | **all plantation** — the arbitrary call in §3b |
| `CBERS_4A_WPM_20230830_207_151_L4_44_22` | **rice** — the flooded-paddy rule |
| `CBERS_4A_WPM_20210711_208_155_L4_43_13` | **all wetland** — the wetland-is-Water rule |
| `CBERS_4A_WPM_20230704_206_152_L4_37_45` | **all Barren** — the scarce class |

Their purpose is to **break these guidelines, not to produce data.**

**The order is deliberate and must not be rearranged:**

1. **Read these guidelines independently.** No group discussion yet.
2. **Annotate all six tiles independently.** No discussion of specific tiles, no looking at
   anyone else's work. **Record how long each tile takes.**
3. **Measure** — per-class IoU between annotators, systematic vs random disagreement, and
   time per tile (§8).
4. **Then discuss**, together, going through every disagreement, and revise this document.
5. **Production annotation** on the revised version.

Independence is required only for step 3 to mean anything. Once the measurement is taken,
aligned interpretation is exactly what production wants — so the discussion belongs after the
measurement, never before it. Discussing first would give the alignment benefit while
destroying both the defect signal and the agreement baseline, for the same total effort.

**One round, not two.** A second full round is not planned, because the production set already
contains a second measurement: the 20 test tiles are annotated by all three, so if the revised
guidelines are still defective it surfaces about 20 annotations into production rather than
requiring another round to discover. Instead, define the trigger: **if a specific class pair is
still below the agreement floor after revision, re-test that one rule on one or two tiles** —
not a full repeat.

**Pilot labels are quarantined, not merged into the dataset.** They are produced under this
version while production runs on the revised one, the tiles were chosen to be pathologically
hard rather than representative, and they sit outside the production selection — folding them
in would break the "first 0.8N test + first 0.2N train" contract and collide with future picks
if the dataset ever grows. Keep them for the record and for computing the agreement baseline.

**Time per tile is the round's most valuable output.** It decides whether the production
allocation is feasible at all, and nothing else in the plan can tell us.

There is no separate qualification test; this round serves that purpose. If one annotator's
agreement sits far from the other two, it surfaces here rather than after a third of the
dataset.

## 8. What will be measured

- **Per-class IoU between annotators** on multiply-annotated tiles. The target will be **set
  from what the pilot shows is achievable**, not asserted in advance — a target tighter than the
  imagery supports would send us rewriting rules that were fine.
- **Systematic vs random disagreement.** A consistent bias (one annotator always tracing tighter,
  or always calling faint lines Agriculture) matters far more than scatter, because majority vote
  cancels scatter and cannot cancel bias.
- **Barren recall** — the scarcest class, so misses concentrate quickly.
- **Time per tile**, from the pilot onward.

There are **no ground-truth jobs and no honeypots**, so the overlapped tiles are the *only*
quality signal we have. That makes them more important than they would otherwise be, and it
means agreement is measured after the fact rather than monitored continuously.

CVAT scores against ground truth but has **no native inter-annotator agreement calculation**, so
annotator-vs-annotator IoU is computed separately from the exported masks.

## 9. Export note for whoever wires up the masks

DeepGlobe's own instruction is to **binarize each R/G/B channel at threshold 128** when reading
masks, because compression shifts the encoded colours. If CVAT exports with any compression or
antialiasing, exact-match colour lookup will silently fail. Re-binarize at 128 in the conversion,
and test the full round trip — CVAT export -> RGB mask PNG -> `rgb_mask_to_label` — on a single
tile **before** anyone annotates a real one.

## 10. Still open, for the pilot to settle

1. **Minimum mapping unit (400 m²)** and the **boundary-tracing guidance** — both need a real
   tile traced before we know if they are workable.
2. **The Agriculture/Rangeland cue** ("cultivation lines vs smooth texture") is the rule
   governing the most pixels. It is also the most likely to fail *systematically* rather than
   randomly, since it is a judgement threshold rather than a visual fact.
3. **Time per tile**, which determines whether the production allocation is feasible.
