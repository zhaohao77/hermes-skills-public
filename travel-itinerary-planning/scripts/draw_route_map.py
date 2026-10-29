#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""手绘风格路线图生成器（不依赖任何生图模型）

用 matplotlib 的 path.sketch 手绘抖动内核 + 中文楷体，画出"手绘感"的
行程路线图。全程本地、秒级出图，比跑 Stable Diffusion 快得多，
且文字是真实可读的中文（生图模型画中文往往糊成一团）。

用法：
    python draw_route_map.py map.json

然后 **必须** 过一遍布局自检：
    python check_text_overlap.py draw_route_map.py   # 若把配置写死在脚本里
    # 或直接对生成的图目视复核，再根据重叠报告调 map.json 里的坐标

输入 JSON 结构（所有坐标都在 0-10 x 0-7.4 的数据坐标系里，自己调）：
{
  "title": "XX 6 日游 · 行程路线图",
  "subtitle": "2026.10.1 — 10.6 ｜ 2 成人 2 儿童 ｜ 一路向西不折返",
  "cities": [
    {"name":"洛阳","x":1.0,"y":5.05,"tag":"Day1下午–10/2\\n龙门石窟·白马寺",
     "color":"#C0392B","tag_dy":-0.8}
  ],
  "arrows": [
    {"from":[0.95,2.30],"to":[1.00,4.55],"rad":0.0,"color":"#C0392B",
     "label":"Day1  G952 高铁 4h07\\n目的地站 07:48 → 郑州东 11:55","lx":2.34,"ly":3.30}
  ],
  "legend": [["#C0392B","去程 / 省内高铁"],["#1F6FB2","返程高铁"]],
  "schedule": [["Day1","目的地站→郑州东→洛阳龙门  |  龙门石窟"]],
  "tips": "★ 每天 9 点左右出发    ★ 仅 D3 需 07:20 出发",
  "out": "route_map.png"
}

关键参数说明：
  cities[].tag_dy   标签相对节点的 y 偏移（负值=放节点下方，正值=上方）
  arrows[].rad      弧线弯曲度（0=直线，正负决定弯向）
  arrows[].lx/ly    标签位置（**必须手工调开**，这是重叠的高发区）
  xlim/ylim         可选，默认 [0,10] / [0,7.4]

踩坑提醒：
  1. KaiTi 没有 bold 字重，会打印 "findfont: Failed to find font weight bold"
     警告 —— 不影响输出，可忽略。
  2. plt.xkcd() 会把字体覆盖成 Humor Sans（中文变方框）——所以本脚本
     **不用 xkcd()，只用它的内核** `path.sketch`，并显式设中文字体。
  3. 箭头标签和节点标签最容易叠，先跑 check_text_overlap.py 再交付。
"""
import argparse
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Circle, FancyArrowPatch

BG = "#FDF6E3"      # 牛皮纸米色
INK = "#3B3226"     # 墨色


def setup():
    plt.rcParams["path.sketch"] = (1.8, 140, 3.2)   # (幅度, 波长, 随机度)
    plt.rcParams["font.sans-serif"] = ["KaiTi", "SimHei", "Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False


def draw(cfg):
    setup()
    xlim = cfg.get("xlim", [0, 10])
    ylim = cfg.get("ylim", [0, 7.4])
    fig, ax = plt.subplots(figsize=(18, 11), dpi=200)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")

    # 标题
    ax.text(5, 7.05, cfg["title"], ha="center", va="center", fontsize=27,
            fontweight="bold", color=INK)
    if cfg.get("subtitle"):
        ax.text(5, 6.62, cfg["subtitle"], ha="center", va="center",
                fontsize=13.5, color="#6B5D4A")
    ax.plot([1.4, 8.6], [6.40, 6.40], color=INK, linewidth=1.8, alpha=0.45)

    # 城市节点
    for c in cfg.get("cities", []):
        x, y, col = c["x"], c["y"], c.get("color", "#E8A33D")
        r = c.get("r", 0.40)
        ax.add_patch(Circle((x, y), r, facecolor=col, edgecolor=INK,
                            linewidth=2.4, zorder=5, alpha=0.93))
        ax.text(x, y, c["name"], ha="center", va="center", fontsize=17,
                fontweight="bold", color="white", zorder=6,
                path_effects=[pe.withStroke(linewidth=2.6, foreground=INK)])
        tag = c.get("tag", "")
        if tag:
            ax.text(x, y + c.get("tag_dy", -0.80), tag, ha=c.get("tag_ha", "center"),
                    va="center", fontsize=11, color=col, fontweight="bold", zorder=7,
                    linespacing=1.5,
                    bbox=dict(boxstyle="round,pad=0.32", facecolor=BG,
                              edgecolor=col, linewidth=1.2, alpha=0.96))

    # 路线箭头
    for a in cfg.get("arrows", []):
        col = a.get("color", "#C0392B")
        ax.add_patch(FancyArrowPatch(a["from"], a["to"],
                                     connectionstyle="arc3,rad=%s" % a.get("rad", 0),
                                     arrowstyle="-|>,head_width=10,head_length=16",
                                     linewidth=a.get("lw", 3.2), color=col, zorder=3,
                                     mutation_scale=1, shrinkA=28, shrinkB=28))
        if a.get("label"):
            ax.text(a["lx"], a["ly"], a["label"], ha="center", va="center",
                    fontsize=a.get("fs", 11.5), color=col, fontweight="bold",
                    zorder=8, linespacing=1.55,
                    bbox=dict(boxstyle="round,pad=0.34", facecolor=BG,
                              edgecolor=col, linewidth=1.3, alpha=0.96))

    # 图例（默认右上空白区；挨着节点会重叠，注意避让）
    for i, (col, txt) in enumerate(cfg.get("legend", [])):
        lx0 = cfg.get("legend_x", 8.45)
        ly0 = cfg.get("legend_y", 6.05)
        yy = ly0 - i * 0.32
        ax.add_patch(Circle((lx0, yy), 0.075, facecolor=col, edgecolor=INK, linewidth=1.2))
        ax.text(lx0 + 0.20, yy, txt, ha="left", va="center", fontsize=10.5, color=INK)

    # 底部日程条
    sched = cfg.get("schedule", [])
    if sched:
        ax.plot([0.35, 9.65], [1.52, 1.52], color=INK, linewidth=1.6, alpha=0.45)
        for i, (d, txt, *rest) in enumerate(sched):
            col = rest[0] if rest else INK
            yy = 1.22 - i * 0.175
            ax.text(0.42, yy, d, ha="left", va="center", fontsize=11,
                    fontweight="bold", color=col)
            ax.text(1.28, yy, txt, ha="left", va="center", fontsize=11, color=INK)

    if cfg.get("tips"):
        ax.text(5, -0.10, cfg["tips"], ha="center", va="center", fontsize=11.5,
                color="#6B5D4A")

    out = cfg.get("out", "route_map.png")
    plt.savefig(out, bbox_inches="tight", facecolor=BG, pad_inches=0.35)
    print("OK ->", out)
    print("⚠️  接着跑 check_text_overlap.py 确认无文字重叠，再交付")


def main():
    ap = argparse.ArgumentParser(description="手绘风格路线图生成器")
    ap.add_argument("config", help="map.json 路径")
    args = ap.parse_args()
    with open(args.config, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    draw(cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
