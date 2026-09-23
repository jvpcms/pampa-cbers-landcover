# Pampa CBERS-4A Land Cover

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22922625.svg)](https://doi.org/10.5281/zenodo.22922625)
[![Licence: CC BY-SA 4.0](https://img.shields.io/badge/Licence-CC%20BY--SA%204.0-lightgrey.svg)](LICENSE)

Pixel-level land cover annotations for **100 CBERS-4A WPM tiles** over the Pampa biome in
Rio Grande do Sul, Brazil, at **2 m/px**, in the **7-class DeepGlobe taxonomy**.

Built to fine-tune a DeepGlobe-pretrained segmentation model onto Brazilian imagery. There
is no freely licensed pixel-level land cover annotation for Brazil at metric resolution:
the national mapping (MapBiomas) is produced at 30 m, and the free metric-resolution
orbital imagery (CBERS-4A) ships without labels. This dataset fills that gap for one
biome.

| | |
|---|---|
| Tiles | 100 (80 train / 20 test) |
| Tile size | 1024 × 1024 px = 2048 × 2048 m = 419,4 ha |
| Resolution | 2 m/px (effective ~5 m, see known issues) |
| Source scenes | 34 CBERS-4A WPM L4, acquired 2020–2026 |
| Classes | 7 (DeepGlobe: Urban, Agriculture, Rangeland, Forest, Water, Barren, Unknown) |
| Region | Pampa biome, Rio Grande do Sul, Brazil |
| Annotators | 1 |
| CRS | EPSG:32721 (35 tiles) and EPSG:32722 (65 tiles) |

**Read [`docs/known_issues.md`](docs/known_issues.md) before using this.** In particular,
one tile renders bright orange although it is open water — that is a rendering artefact,
not bad imagery and not a mislabel.

---

## Layout

```
manifest.csv                        100 rows, one per tile, 24 columns
labelmap.txt                        CVAT label map: class name -> RGB
docs/
  annotation_guidelines.md          the rules the annotator worked under (v1.0.1)
  known_issues.md                   measured caveats — read this
scripts/
  verify.py                         integrity check, see Verifying below
data/
  SHA256SUMS                        sha256 of all 600 data files, paths relative to data/
  train/                            80 tiles
    images/<tile_id>.png            8-bit RGB composite, what the annotator saw
    images/<tile_id>.wld            world file for the PNG
    images/<tile_id>.png.aux.xml    GDAL sidecar: CRS + geotransform for the PNG
    rasters/<tile_id>.tif           4-band Int16 GeoTIFF, R/G/B/NIR, raw DN, georeferenced
    masks/<tile_id>.png             class mask, RGB-coded per labelmap.txt
    instances/<tile_id>.png         instance mask (CVAT SegmentationObject)
  test/                             20 tiles, same structure
```

`tile_id` is `<scene_id>_<i>_<j>`, where `i`, `j` are the tile's column and row in its
scene's grid. `scene_id` encodes sensor, acquisition date, orbit and point, e.g.
`CBERS_4A_WPM_20230704_206_152_L4` is orbit 206, point 152, acquired 2023-07-04.

**The GeoTIFF is the archive, the PNG is one rendering of it.** The GeoTIFFs keep the raw
Int16 DN and the NIR band. If the 8-bit RGB rendering does not suit you, re-render from
the rasters rather than working around the PNGs.

## Classes

| Index | Class | RGB | Share of annotated px |
|---|---|---|---|
| 1 | Urban | `0,255,255` | 4,56 % |
| 2 | Agriculture | `255,255,0` | 22,70 % |
| 3 | Rangeland | `255,0,255` | 31,17 % |
| 4 | Forest | `0,255,0` | 15,66 % |
| 5 | Water | `0,0,255` | 21,26 % |
| 6 | Barren | `255,255,255` | 3,78 % |
| 7 | Unknown | `0,0,0` | 0,88 % |

Per split:

| Class | train | test |
|---|---|---|
| Urban | 3,83 % | 7,45 % |
| Agriculture | 23,17 % | 20,80 % |
| Rangeland | 31,77 % | 28,79 % |
| Forest | 15,67 % | 15,60 % |
| Water | 20,99 % | 22,36 % |
| Barren | 4,29 % | 1,76 % |
| Unknown | 0,28 % | 3,25 % |

**All six cover classes are present in both splits.** That is by construction, not luck —
see *Sampling* below.

`Unknown` is not a land cover. It marks unannotated regions and cloud, and it should be
excluded from scoring. The convention used in the source project is to drop any 256 px
sub-tile whose `Unknown` fraction reaches 5 %, and to exclude the remaining `Unknown`
pixels from the metric.

Class definitions are DeepGlobe's, quoted verbatim in `docs/annotation_guidelines.md`.
Where the annotator's judgement about terrain trafficability conflicted with DeepGlobe's
wording, DeepGlobe won, because the point of matching their taxonomy is that pretrained
weights transfer.

## Splits

80 train / 20 test, fixed, at the level of the 1024 px tile. `split_use` in
`manifest.csv` is authoritative.

The split is **not** a random partition of the 100 tiles. The full candidate grid was
partitioned first, then sampled independently on each side, with:

- a **2000 m edge-to-edge exclusion buffer** around every test-eligible tile, removing
  its neighbours from the training pool. Geographically adjacent tiles share texture,
  illumination and land use, and a test tile next to a train tile gives an optimistic
  estimate. The buffer is a geometric distance test, not a tile-index or centroid test,
  because tile grids are built per scene in independent origins and do not align across
  scenes.
- a guarantee that **every stratum appears on both sides**, checked once at partition
  time.
- test-eligible size capped **per stratum** at `min(20 % of the pool, 200)`, so that a
  global cut cannot drain a rare class out of the test side.

Do not re-split this dataset randomly. Doing so puts adjacent tiles on both sides and
inflates your numbers.

## Verifying

```
sha256sum -c SHA256SUMS          # from inside data/
python scripts/verify.py         # needs numpy, rasterio, pillow
```

`verify.py` checks the file inventory against the manifest, that masks are 1024 × 1024 and
use only palette colours, that class and instance masks agree on which pixels are
annotated, and that every PNG reproduces from its GeoTIFF plus the manifest parameters.
Expected output on an intact copy:

```
[1] inventory: 100 tiles, 0 problem(s)
[2] masks: 0 off-palette, 0 wrong shape
[3] class/instance agreement: 0 mismatched
[4] reproduction: 60/100 bit-exact, max delta 1 DN
OK
```

The 40 non-exact tiles are known and bounded at 1 DN — see known issue 4. Any delta above
1, or any nonzero count in steps 1 to 3, means the copy is damaged.

**Do not convert this repository to Git LFS.** Zenodo's GitHub integration archives the
repository tarball, and an LFS-tracked file appears in that tarball as a pointer, not as
data. The files here are small enough (largest 4,7 MB) that plain Git is correct.

---

## How it was built

### Scene selection

Every orbit/point combination intersecting the biome was enumerated, and one scene chosen
per combination. Criteria: **cloud cover ≤ 10 %** from the INPE STAC catalogue, and a
fixed **winter seasonal window** to control phenology and sun angle. **Year was left
free** — fixing it as well drops eligible coverage from 41 of 42 combinations to 28, given
the 31-day revisit. 44 scenes were selected; the 100 tiles come from 34 of them.

Scenes were not hand-picked as "representative", deliberately: choosing which scenes
represent a biome is itself a subjective judgement that would reintroduce at the scene
level the bias that random tile sampling removes at the tile level.

### Tile grid

A 1024 px grid is laid over each scene, in the scene's own CRS, from its top-left corner.
Partial edge tiles are dropped rather than padded.

Two corrections matter:

- **Overlap.** Adjacent scenes overlap by about 26 %. A tile is discarded only when it is
  *entirely* covered by the union of its neighbours nearer their own scene centres. An
  earlier rule that discarded on any intersection lost 2,71 % of the total area, about
  9400 km², concentrated exactly at scene transitions.
- **Valid swath.** L4 products are orthorectified onto a north-up UTM grid, but the imaged
  swath inside is a rectangle rotated ~13°, with NoData corners — **mean 67,7 % of each
  bounding box is real imagery**. The grid was originally laid over the bounding box and
  put tiles in empty corners. STAC metadata cannot reveal this, because the declared
  footprint *is* the bounding box (13.520 vs 13.521 km² measured). The grid was rebuilt
  over each scene's valid swath.

Final grid: **49.039 candidate tiles**, 8 to 1807 per scene. Every tile in it is fully
covered by real imagery, and every released tile has `nodata_frac = 0`.

**745 km², 0,39 % of the coverable area, is not covered**, at seams where adjacent swaths
overlap in a band narrower than two tiles so no single scene contains a whole tile. This
is not missing downloads — every catalogued orbit/point over the Pampa is held, and 97 %
of the gap area already has ≥ 2 swaths over it. Closing it would need partial tiles (which
would put NoData back into training) or cross-scene mosaicking.

### Sampling

100 tiles from 49.039, stratified, seed 42. Strata are **12 leaves of a subdivision of the
cover classes**, not the classes themselves, because several classes have subtypes whose
absence would be a blind spot — water is dominated by area by the large coastal lagoons,
so a proportional sample would rarely contain a river; urban is dominated by metropolitan
Porto Alegre; sand differs between beach and inland. The strata raster is derived from
MapBiomas, used as a *prior on where to look*, never as a label.

Three requirements, each met by a distinct mechanism:

1. **Coverage** — a floor of 1 tile per stratum, taken with a purity filter of 10 % of
   tile area (≈ 48,7 ha). Exceptions: Porto Alegre at 50 %, so the stratum gets dense
   metro rather than city-edge tiles; Mining (4,5 ha) and Aquaculture (0,9 ha) qualify by
   absolute area, since 48,7 ha of aquaculture does not exist in the biome.
2. **Proportionality** — the remaining budget by the **Sainte-Laguë divisor method**.
3. **Prefix stability** — extending the budget later must not change earlier picks.
   Formally, the allocation for `M > N` has the allocation for `N` as an exact prefix.
   Each stratum's eligible list is shuffled once under the fixed seed and always consumed
   from the front, and the divisor method is additive and never revises a past step.
   Largest-remainder rounding was rejected for this reason: it is subject to the Alabama
   paradox.

So **a future release extending this set will contain these exact 100 tiles, in these
exact splits**, as a subset.

### Fusion

CBERS-4A WPM L4 delivers a 2 m panchromatic band and four 8 m multispectral bands on the
same grid. INPE's own fused product was evaluated and rejected: its effective resolution
measures around 8 m on a 2 m grid.

Fusion is **SFIM** (Smoothing-Filter-based Intensity Modulation), `out = MS↑ · PAN /
lowpass(PAN)`, at **lowpass width 6**, not Brovey or another component-substitution
method. The reason is specific to this sensor: **the WPM panchromatic band spans
0,45–0,90 µm and therefore includes the near infrared**, where vegetation is highly
reflective. Component-substitution injects that energy into the colour composite, shifting
vegetation hue by an amount that depends on each scene's vegetation fraction — i.e. it
breaks consistency between scenes, which is exactly what a segmentation model must not
have to cope with. Measured against the scene's own 8 m bands, SFIM inflated blue-band
variance by 1,03x against Brovey's 1,68x, with mean absolute error 3x smaller in every
band.

SFIM's usual weakness, ringing under PAN/MS misregistration, does not apply: L4 bands
share a grid and band-to-band registration is −0,02 to −0,16 px.

Output band order is **R, G, B, NIR** (source BAND3, 2, 1, 4). A pixel is treated as
outside the swath only when *every* band is zero — NIR legitimately reads 0 over dark
water, and an earlier any-band rule punched holes through otherwise perfect water tiles.

### Rendering

The 8-bit PNGs are produced in two stages, both recorded per tile in `manifest.csv`:

1. **Linear stretch, per scene, per band** — percentiles **p2 / p99.5** over the scene's
   pooled selected tiles, mapped to 0–255. p99.5 rather than p98 because bright sand and
   surf sit above p98 and a p98 ceiling renders whole beaches flat white.
2. **Gamma, per tile** — solved so the rendered median lands on **128**, clamped to
   **[0,30, 1,20]**.

The two knobs do different jobs and separating them was the point: endpoints decide how
much DN range is stretched (how much contrast is manufactured), gamma decides exposure.
Per-tile endpoints were rejected because a lagoon tile spans ~6 DN and stretching that
over 0–255 is a ~42x gain that turns sensor noise into visible static. One gamma per scene
was rejected because bimodal scenes render their land tiles at 49–74 of 255.

Per-image normalisation is in any case the standard convention for satellite imagery in
deep learning.

To reproduce a PNG from its GeoTIFF: clip `(DN − lo) / (hi − lo)` to [0, 1] per band,
raise to `gamma_exponent`, scale to 255. This matches bit-for-bit on 60 of 100 tiles and
within ±1 DN on the rest — see known issue 4.

### Annotation

CVAT, one annotator, on the 1024 px PNGs, under `docs/annotation_guidelines.md` v1.0.1.

The annotator worked **only from the delivered image** — no other acquisition dates, no
third-party imagery services, no existing land cover maps — so that a label describes what
is visible in that acquisition rather than what is known about the place.

`Unknown` covers unannotated regions and cloud.

---

## Citation

Archived on Zenodo. The **concept DOI** below always resolves to the latest version, which
is what you normally want to cite:

> **10.5281/zenodo.22922625**

If you need the exact bits you worked with, cite the **version DOI** instead. For the
current release, `v1.0.0`, that is **10.5281/zenodo.22922626**. Use this one when
reproducing published numbers, since the concept DOI will move to later versions.

The Zenodo record is typed as a **Dataset** and carries the same CC BY-SA 4.0 licence as
this repository.

```bibtex
@dataset{paim2026pampa,
  author    = {Paim de Cerqueira Melo de Souza, Jo\~{a}o Victor},
  title     = {Pampa {CBERS}-4A Land Cover},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.22922625},
  url       = {https://doi.org/10.5281/zenodo.22922625}
}
```

`CITATION.cff` carries the same metadata, so GitHub's "Cite this repository" button works
as well.

Underlying imagery is CBERS-4A WPM, acquired and distributed by INPE (Instituto Nacional
de Pesquisas Espaciais) and CAST. Cite INPE as the imagery source independently of this
dataset.

## Licence

**CC BY-SA 4.0** (Creative Commons Attribution-ShareAlike 4.0 International). Full text in
[`LICENSE`](LICENSE).

The choice is constrained, not preferential. The annotations are original work and could
have carried a more permissive licence on their own, but they are released alongside the
GeoTIFF crops and the 8-bit composites, which are derivative works of CBERS-4A imagery
distributed by INPE under CC BY-SA 3.0. ShareAlike propagates to those derivatives.
CC BY-SA 3.0 permits licensing adaptations under a later version of the same licence,
which is what makes 4.0 available here.

Practically, this means you may copy, redistribute and adapt the dataset, including
commercially, provided you attribute it and license your adaptations under CC BY-SA 4.0 or
a compatible licence.

Attribution must name **both** this dataset and INPE as the imagery source. See
[Citation](#citation) and [Acknowledgements](#acknowledgements).

## Acknowledgements

Produced as part of a final-year project (PFC) at the Instituto Militar de Engenharia,
Rio de Janeiro, on land cover segmentation for terrain movement-difficulty estimation.
