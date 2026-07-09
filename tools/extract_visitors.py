#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract visitor metadata + copy one representative sprite per visitor.

Source: apps/wallpaper/data/visitors.js (generated JSON wrapped in a JS assignment).
Output:
  WindyWebSite/assets/visitors/<id>.png   one sprite per visitor
  WindyWebSite/data/visitors.json         [{id,label,labelEn,rarity}] + rarity meta + counts
"""
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
WALLPAPER = os.path.normpath(os.path.join(SITE, "..", "WindyWallpaper", "apps", "wallpaper"))
SRC_JS = os.path.join(WALLPAPER, "data", "visitors.js")
SPRITE_ROOT = os.path.join(WALLPAPER, "assets", "sprites")
OUT_SPRITES = os.path.join(SITE, "assets", "visitors")
OUT_JSON = os.path.join(SITE, "data", "visitors.json")


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
    rarities = data["rarities"]
    os.makedirs(OUT_SPRITES, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)

    out = []
    missing = []
    counts = {"common": 0, "rare": 0, "epic": 0}
    for v in visitors:
        src = pick_sprite(v)
        has_art = bool(src and os.path.exists(src))
        if has_art:
            dst = os.path.join(OUT_SPRITES, v["id"] + ".png")
            shutil.copyfile(src, dst)
        else:
            missing.append(v["id"])
        counts[v["rarity"]] = counts.get(v["rarity"], 0) + 1
        out.append({
            "id": v["id"],
            "label": v["label"],
            "labelEn": v["labelEn"],
            "rarity": v["rarity"],
            "art": ("assets/visitors/" + v["id"] + ".png") if has_art else None,
        })

    payload = {
        "total": len(out),
        "counts": counts,
        "rarities": {
            k: {"label": rarities[k]["label"], "labelEn": rarities[k]["labelEn"]}
            for k in ("common", "rare", "epic") if k in rarities
        },
        "visitors": out,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print("visitors:", len(out), "counts:", counts)
    print("copied sprites:", len(out) - len(missing), "missing:", len(missing))
    if missing:
        print("missing art for:", ", ".join(missing[:20]))


if __name__ == "__main__":
    main()
