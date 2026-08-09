#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract the public visitor showcase and its representative sprites.

Source: apps/wallpaper/data/visitors.js (generated JSON wrapped in a JS assignment).
Output:
  WindyWebSite/assets/visitors/<id>.png   one sprite per showcased visitor
  WindyWebSite/data/visitors.json         public showcase metadata + catalogue counts
"""
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
WALLPAPER = os.path.normpath(os.path.join(SITE, "..", "Windy-WallPaper", "apps", "wallpaper"))
SRC_JS = os.path.join(WALLPAPER, "data", "visitors.js")
SPRITE_ROOT = os.path.join(WALLPAPER, "assets", "sprites")
OUT_SPRITES = os.path.join(SITE, "assets", "visitors")
OUT_JSON = os.path.join(SITE, "data", "visitors.json")

# Keep the public landing page deliberately spoiler-light: familiar weather first,
# a small sampling of rarer sights, and only a few epic discoveries.
SHOWCASE_IDS = (
    "cloud", "rain", "wind", "cumulus", "cirrus", "nightmist",
    "fog", "glow", "sunbeam", "birds", "thundercloud", "halo22",
    "arcuscloud", "lenticular", "sundog", "lightpillar", "fullrainbow",
    "glory", "iridescentcloud", "meteor", "doublerainbow",
    "aurora", "redsprite", "noctilucentcloud",
)


def load_data():
    with open(SRC_JS, "r", encoding="utf-8") as fh:
        text = fh.read()
    # strip the leading "window.WW_DATA... = " and trailing ";"
    start = text.index("{", text.index("visitors ="))
    blob = text[start:]
    blob = blob.rstrip().rstrip(";")
    return json.loads(blob)


def pick_sprite(v):
    """Prefer <id>-1, else first spriteName; return absolute png path or None."""
    names = v.get("spriteNames") or [s.get("name") for s in v.get("sprites", {}).get("variants", [])]
    names = [n for n in names if n]
    if not names:
        return None
    vid = v["id"]
    preferred = None
    for n in names:
        base = os.path.basename(n)
        if base == vid + "-1":
            preferred = n
            break
    chosen = preferred or names[0]
    return os.path.join(SPRITE_ROOT, chosen.replace("/", os.sep) + ".png")


def main():
    data = load_data()
    visitors = data["visitors"]
    visitors_by_id = {v["id"]: v for v in visitors}
    unknown_ids = [visitor_id for visitor_id in SHOWCASE_IDS if visitor_id not in visitors_by_id]
    if unknown_ids:
        raise ValueError("Unknown showcase visitor IDs: " + ", ".join(unknown_ids))
    showcase = [visitors_by_id[visitor_id] for visitor_id in SHOWCASE_IDS]
    os.makedirs(OUT_SPRITES, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)

    out = []
    missing = []
    catalogue_counts = {"common": 0, "rare": 0, "epic": 0}
    showcase_counts = {"common": 0, "rare": 0, "epic": 0}
    for v in visitors:
        catalogue_counts[v["rarity"]] = catalogue_counts.get(v["rarity"], 0) + 1
    for v in showcase:
        src = pick_sprite(v)
        has_art = bool(src and os.path.exists(src))
        if has_art:
            dst = os.path.join(OUT_SPRITES, v["id"] + ".png")
            shutil.copyfile(src, dst)
        else:
            missing.append(v["id"])
        showcase_counts[v["rarity"]] = showcase_counts.get(v["rarity"], 0) + 1
        out.append({
            "id": v["id"],
            "label": v["label"],
            "labelEn": v["labelEn"],
            "rarity": v["rarity"],
            "art": ("assets/visitors/" + v["id"] + ".png") if has_art else None,
        })

    selected_files = {visitor_id + ".png" for visitor_id in SHOWCASE_IDS}
    removed = []
    for entry in os.scandir(OUT_SPRITES):
        if entry.is_file() and entry.name.endswith(".png") and entry.name not in selected_files:
            os.remove(entry.path)
            removed.append(entry.name)

    payload = {
        "total": len(visitors),
        "showcaseTotal": len(out),
        "visitors": out,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print("catalogue visitors:", len(visitors), "counts:", catalogue_counts)
    print("showcase visitors:", len(out), "counts:", showcase_counts)
    print("copied sprites:", len(out) - len(missing), "missing:", len(missing))
    print("removed stale sprites:", len(removed))
    if missing:
        print("missing art for:", ", ".join(missing[:20]))


if __name__ == "__main__":
    main()
