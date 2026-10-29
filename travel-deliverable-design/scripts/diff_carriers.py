# -*- coding: utf-8 -*-
"""A4 变体页 vs 9:16 手账图（合并版）文本差异体检。

用途：A4 页（a4/dX_a4.html、a3/d2_a3.html）与手账图源（scrapbook/d*.html）是**两套独立 HTML**，
      改一边不会自动同步（见 skill 铁律 23 ⑥）。每轮改完跑一次，确认没有"数字/口径漂移"。

判读：连续两轮仍出现在「手账图有 A4 缺」里的条目 = 真缺口；
      只在措辞/emoji/标点上不同的 = 正常（A4 版允许换行与语气不同）。

改顶部 BASE / PAIRS 即可换项目。
"""
import html, io, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"$HOME\.hermes\tmp\henan")
PAIRS = [("D1", "scrapbook/d1.html", "a4/d1_a4.html"),
         ("D2", "scrapbook/d2_v4.html", "a3/d2_a3.html"),
         ("D3", "scrapbook/d3.html", "a4/d3_a4.html"),
         ("D4", "scrapbook/d4.html", "a4/d4_a4.html"),
         ("D5", "scrapbook/d5.html", "a4/d5_a4.html"),
         ("D6", "scrapbook/d6.html", "a4/d6_a4.html")]


def text(p):
    t = io.open(BASE / p, encoding="utf-8").read()
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|h[1-6]|li|tr|section)>", "\n", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = html.unescape(t)
    lines = [re.sub(r"[ \t\u3000]+", " ", l).strip() for l in t.split("\n")]
    return [l for l in lines if l]


def norm(l):
    return re.sub(r"[\s·｜|,，。．:：()（）「」【】\-–—~～/]+", "", l)


for day, sb, a4 in PAIRS:
    A, B = text(sb), text(a4)
    na = {norm(x) for x in A if len(norm(x)) >= 6}
    nb = {norm(x) for x in B if len(norm(x)) >= 6}
    miss = [x for x in A if len(norm(x)) >= 6 and not any(norm(x) == y or norm(x) in y or y in norm(x) for y in nb)]
    extra = [x for x in B if len(norm(x)) >= 6 and not any(norm(x) == y or norm(x) in y or y in norm(x) for y in na)]
    print("=" * 20, day, "｜手账图 %d 行 / A4 %d 行" % (len(A), len(B)))
    print("  ① 手账图有、A4 缺（%d）：" % len(miss))
    for x in miss[:22]:
        print("     -", x[:100])
    print("  ② A4 有、手账图无（%d）：" % len(extra))
    for x in extra[:14]:
        print("     +", x[:100])
    print()
