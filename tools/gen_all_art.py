#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate all promo art pieces for the Windborne website, sequentially."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_image  # noqa: E402

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SITE, "assets", "art")

# Shared style base — mirrors the wallpaper's cut-paper collage + pastel weather look.
STYLE = (
    "手工剪纸拼贴风格（cut-paper collage / papercraft），层叠撕边纸张纹理，"
    "柔和粉彩色调：奶油纸色 #fff8df、粉蓝海面 #cfe8f3、薄荷风区 #d8ecd1、暖黄 #f3e3a7、"
    "淡紫 #a88bd9，墨蓝色描边 #344653，克制低对比、柔和、宁静治愈的氛围，扁平插画，"
    "细腻的纸张颗粒与轻微投影，无文字，无水印，无地图、无国界、无行政区线、无可识别地理轮廓"
)

JOBS = [
    # (filename, width, height, prompt)
    (
        "hero.png", 1600, 1000,
        "一幅横向宽幅主视觉插画：抽象的粉蓝、奶油与淡紫色剪纸天气层次，"
        "天空漂浮着蓬松的云朵、彩虹、旋转的风涡、光柱与流动风线粒子；"
        "下半部分是非地理化的抽象纸艺气流、云带与柔和色块，不出现陆地、海岸线或任何地图轮廓。"
        "画面轻盈梦幻，留白充足适合叠加标题文字。" + STYLE,
    ),
    (
        "visitor-showcase.png", 1200, 900,
        "一组精美的剪纸拼贴天象合集陈列：彩虹、极光、日晕光环、流星、雷雨云、光柱，"
        "如同标本收藏卡片般排列在奶油纸色背景上，柔和粉彩，治愈风。" + STYLE,
    ),
    (
        "ranch.png", 1200, 800,
        "一个温馨的剪纸拼贴小牧场场景：奶油色草地上有几只可爱的剪纸小动物与花朵、"
        "小树，天空漂浮柔和云朵，宁静放松的放置收集玩法氛围。" + STYLE,
    ),
]


def main():
    os.makedirs(ASSETS, exist_ok=True)
    results = []
    for name, w, h, prompt in JOBS:
        out = os.path.join(ASSETS, name)
        print("\n=== generating", name, "===", flush=True)
        rc = gen_image.run(prompt, out, w, h)
        results.append((name, rc))
    print("\n=== summary ===")
    for name, rc in results:
        print(name, "OK" if rc == 0 else "FAILED(rc=%s)" % rc)


if __name__ == "__main__":
    main()
