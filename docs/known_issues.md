# Known issues

Everything here is a property of the released data, measured, not a suspicion. Nothing
listed is a reason not to use the dataset; the point is that you should know about it
before you are surprised by it.

---

## 1. One tile renders orange although it is open water

`CBERS_4A_WPM_20230704_206_152_L4_31_11` (train) is 100 % water in its mask
(1,048,576 / 1,048,576 px labelled `Water`) but its RGB composite is bright and warm,
median RGB 219 / 196 / 181.

**This is a rendering artefact. It is not bad imagery, not a fusion failure and not a
mislabel.** The underlying DN in `data/train/rasters/` is genuine turbid water: across
all 14 near-pure-water tiles the red/blue and NIR/blue ratios rise together and
monotonically, which is what sediment load does and not what a processing fault does.
The label was checked by hand and is correct.

Two independent parts of the 8-bit rendering (§*Rendering* in the README) produce the
appearance, and both are documented in the manifest for this tile:

**Brightness — the gamma clamp.** Per-tile gamma is solved so the rendered median lands
on 128, then clamped to `[0.30, 1.20]`. This tile needed an exponent of about **3.78**
and got **1.20**, so it renders at a median around 205 instead of 128. The clamp exists
so that a low-contrast tile cannot have sensor noise amplified into visible texture: at
n ≈ 0,83 the slope of n^3.78 is about 2,28, so the unclamped curve would multiply noise
by that factor.

**Hue — per-band endpoints.** The stretch endpoints are fitted **per band**, and for this
tile they are R 61–145, G 88–134, B 128–160, i.e. widths of 84 / 46 / 32 DN over floors
that differ by 67 DN. Rescaling three bands by three different affine maps reorders the
channels, and that reordering is the warm cast. Gamma cannot undo it, because gamma is
monotonic and therefore acts on luminance, never on hue.

The endpoints are bimodal because of how the scene was sampled: all four tiles selected
from scene `206_152` are essentially pure water, with non-overlapping red distributions,
so the pooled per-scene percentiles fall between two modes and describe neither.

**If you are training on this dataset**, the honest options are to leave it (it is one
tile of 100 and its label is right), to drop it, or to re-render it from
`data/train/rasters/` with your own stretch. The GeoTIFF is the archive; the PNG is one
rendering choice, not the data.

---

## 2. Fourteen tiles sit at a gamma clamp bound

Nine tiles are at `gamma_exponent = 1.20` and five at `0.30`, i.e. the solver wanted to go
further and was stopped. All fourteen are near-100 % water, which have no mid-tones for a
tone curve to move. The clamp rate is **64,3 % among pure-water tiles against 5,8 %
elsewhere**, so this is a property of that one kind of content, not a general defect.

Find them with `gamma_exponent` in `manifest.csv`. The affected tiles are the ones whose
rendered median is away from the documented target of 128, so the invariant "every PNG has
median 128" is **not** true of this release. It is true of the other 86 tiles.

---

## 3. Nineteen of the hundred tiles are water-dominated

Fourteen are above 90 % water and essentially all of those are 100 %. The split is
15 train / 4 test, concentrated in the coastal `206/xxx` and `207/xxx` scenes.

They are legitimate draws: `Water` is a stratum and open lagoon is what most of the
biome's water area is. But they carry very little signal — one measured about **6 DN of
range in red** — and no stretch recovers what is not there. They were kept because the
selection is prefix-stable and removing them would break that contract (see the README).
An NDWI criterion is planned for any future extension beyond N = 100, not applied
retroactively.

If you report per-class numbers, be aware that `Water` in this dataset is dominated by
large homogeneous lagoon and ocean rather than by rivers and small reservoirs.

---

## 4. The PNGs are authoritative; re-deriving them gives ±1 DN on 40 tiles

`manifest.csv` carries the six endpoints and the gamma exponent for every tile, which is
enough to recompute the PNG from the GeoTIFF — and inference preprocessing has to do
exactly that. Verified over all 100 tiles:

- **60 tiles reproduce bit-exactly.**
- **40 tiles differ, always by exactly 1 DN**, on a subset of pixels (worst case 58,842 px
  of 1,048,576). The maximum absolute difference over the whole release is **1**.

The cause is rounding: `gamma_exponent` is written to 4 significant figures, and the
exporter used the unrounded value. For example a tile whose true exponent is 0,77398
is recorded as 0,774, which moves 2,879 pixels by one level.

Irrelevant for training. Relevant if you are checksumming a re-derivation or asserting
bit-equality in a test. Treat the PNG as the authoritative rendering and the manifest as
a description of it accurate to ±1 DN.

---

## 5. The selection spans two UTM zones

65 tiles are EPSG:32722 and 35 are EPSG:32721 (`crs` in the manifest). Each tile is
internally consistent and correctly georeferenced. Anything that mosaics across tiles, or
assumes one projection for the whole set, has to reproject.

---

## 6. Effective ground resolution is coarser than the 2 m grid

The grid is 2 m because the panchromatic band is 2 m, but the CBERS-4A WPM point spread
function has FWHM 2,4–2,6 px, so effective resolution is closer to **~5 m**. Fine texture
is softer than a 2 m dataset resampled from aerial imagery. No fusion method recovers it,
and SFIM was verified to lose nothing relative to the source PAN (fused-to-PAN detail
ratio a constant 0,86–0,91 across sharp and blurry tiles).

Scene-to-scene sharpness varies by about 2x. This was investigated and traced to terrain
content, view geometry and atmosphere at capture time, not to the processing chain.

---

## 7. One annotator, so there is no agreement statistic

All 100 tiles were annotated by one person against `docs/annotation_guidelines.md` v1.0.1.
A multi-annotator round with a replicated subset was planned and cancelled.

The upside is that there is no between-annotator style variance, which on a set this size
would itself be a noticeable noise source. The downside is that boundary consistency is
not quantified, and any systematic misreading of a guideline propagates identically into
train and test, where a metric computed on this dataset cannot detect it.

---

## 8. Agriculture and Rangeland are hard to separate at this resolution

They are annotated and released as **separate classes**, deliberately, so the distinction
stays available. But a model trained at 2 m may not sustain the boundary: in the
DeepGlobe-trained baseline, `Rangeland` reached IoU 45,4 % against 87,5 % for
`Agriculture`, with 20,1 % of true `Rangeland` pixels predicted as `Agriculture` and only
2,8 % the other way. Merging the two raised mean IoU.

Whether you merge is your call. `labelmap.txt` keeps them apart.

---

## 9. Acquisition years are dispersed, and one scene is out of the seasonal window

Season was fixed (winter) and **year was deliberately left free**: with a 31-day revisit,
constraining both leaves only 28 of 42 orbit/point combinations with an eligible scene,
against 41 with season alone. Acquisition dates therefore run **2020 to 2026**, and
brightness, sun angle and phenology vary between tiles. Do not compare brightness across
tiles, and do not treat the set as a single-epoch snapshot.

Scene `207/153` is the one exception to the winter window: no in-window acquisition
reached acceptable cloud cover, so the nearest date was used (24/11/2022). It is recorded
as an explicit exception rather than absorbed by widening the window for everyone.

---

## 10. There is no atmospheric correction

CBERS-4A WPM has no surface-reflectance product. Scenes were screened for cloud (≤ 10 %
from the catalogue) and for haze, but the DN are top-of-atmosphere and uncorrected. Any
absolute radiometric comparison between tiles inherits whatever the atmosphere was doing.
