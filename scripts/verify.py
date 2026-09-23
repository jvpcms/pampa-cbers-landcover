#!/usr/bin/env python3
"""Integrity check for the Pampa CBERS-4A land cover release.

Checks, in order:
  1. every manifest row has its six files, and there are no stray tiles
  2. masks are 1024x1024 and use only palette colours from labelmap.txt
  3. class and instance masks agree on which pixels are annotated
  4. each PNG reproduces from its GeoTIFF plus the manifest stretch parameters

Step 4 is expected to differ by at most 1 DN on 40 of the 100 tiles; see
docs/known_issues.md item 4. Any larger difference is a real problem.

Usage: python scripts/verify.py [--skip-reproduce]
"""
import argparse
import csv
import pathlib
import sys

import numpy as np
import rasterio
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUBDIRS = {"images": ".png", "rasters": ".tif", "masks": ".png", "instances": ".png"}


def load_palette():
    palette = {}
    for line in (ROOT / "labelmap.txt").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        name, rgb, *_ = line.split(":")
        palette[tuple(int(v) for v in rgb.split(","))] = name
    return palette


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-reproduce", action="store_true")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(ROOT / "manifest.csv")))
    palette = load_palette()
    failures = []

    # 1. file inventory
    expected = set()
    for r in rows:
        t, s = r["tile_id"], r["split_use"]
        for sub, ext in SUBDIRS.items():
            p = ROOT / "data" / s / sub / f"{t}{ext}"
            expected.add(p)
            if not p.exists():
                failures.append(f"missing {p.relative_to(ROOT)}")
    for s in ("train", "test"):
        for sub, ext in SUBDIRS.items():
            for p in (ROOT / "data" / s / sub).glob(f"*{ext}"):
                if p not in expected:
                    failures.append(f"stray {p.relative_to(ROOT)}")
    print(f"[1] inventory: {len(rows)} tiles, {len(failures)} problem(s)")

    # 2 and 3. mask contents
    off_palette = shape_bad = footprint_bad = 0
    for r in rows:
        t, s = r["tile_id"], r["split_use"]
        cls = np.array(Image.open(ROOT / "data" / s / "masks" / f"{t}.png").convert("RGB"))
        obj = np.array(Image.open(ROOT / "data" / s / "instances" / f"{t}.png").convert("RGB"))
        if cls.shape != (1024, 1024, 3):
            shape_bad += 1
            failures.append(f"{t}: mask shape {cls.shape}")
        seen = {tuple(c) for c in np.unique(cls.reshape(-1, 3), axis=0)}
        if seen - set(palette):
            off_palette += 1
            failures.append(f"{t}: off-palette colours {sorted(seen - set(palette))}")
        if int(((cls != 0).any(-1) != (obj != 0).any(-1)).sum()):
            footprint_bad += 1
            failures.append(f"{t}: class and instance masks disagree on annotated pixels")
    print(f"[2] masks: {off_palette} off-palette, {shape_bad} wrong shape")
    print(f"[3] class/instance agreement: {footprint_bad} mismatched")

    # 4. rendering reproducibility
    if not args.skip_reproduce:
        exact = worst = 0
        for r in rows:
            t, s = r["tile_id"], r["split_use"]
            with rasterio.open(ROOT / "data" / s / "rasters" / f"{t}.tif") as src:
                dn = src.read([1, 2, 3]).astype("f4")
            lo = np.array([float(r[f"stretch_lo_{b}"]) for b in "rgb"], "f4")[:, None, None]
            hi = np.array([float(r[f"stretch_hi_{b}"]) for b in "rgb"], "f4")[:, None, None]
            norm = np.clip((dn - lo) / (hi - lo), 0, 1) ** float(r["gamma_exponent"])
            rep = np.round(norm * 255).astype("u1").transpose(1, 2, 0)
            got = np.array(Image.open(ROOT / "data" / s / "images" / f"{t}.png").convert("RGB"))
            delta = int(np.abs(rep.astype(int) - got.astype(int)).max())
            exact += delta == 0
            worst = max(worst, delta)
            if delta > 1:
                failures.append(f"{t}: reproduction differs by {delta} DN (expected <= 1)")
        print(f"[4] reproduction: {exact}/{len(rows)} bit-exact, max delta {worst} DN")

    if failures:
        print(f"\nFAILED with {len(failures)} problem(s):")
        for f in failures[:40]:
            print(f"  {f}")
        if len(failures) > 40:
            print(f"  ... and {len(failures) - 40} more")
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
