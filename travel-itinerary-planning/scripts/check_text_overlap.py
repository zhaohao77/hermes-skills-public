#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""matplotlib 图表「文字重叠」自检器（通用）

为什么需要它：手绘图/信息图里文字框叠在一起，看缩略图很难发现，
打印出来才发现字压字。本脚本用 matplotlib 渲染器取出每个文字元素的
**真实包围盒**（含 bbox 边框），程序化检测两两重叠，把"看着差不多"
变成可量化的通过/不通过。

用法：
    python check_text_overlap.py <绘图脚本.py> [--top 12]

原理：
    runpy 执行目标绘图脚本（脚本需正常调用 plt.savefig），
    拦截 Figure.savefig 拿到 figure 对象，再遍历 ax.texts 取 window_extent。
    带底色框的标签（bbox=dict(...)）会优先取 bbox_patch 的 extent。

退出码：无重叠 0 / 有重叠 1 / 未捕获 figure 2

实战来源（某日 河南6日行程手绘路线图）：
    第一版检出 4 处重叠，最大一处 28848px²（「郑州」节点标签被
    「Day3 高铁」箭头标签压住），调整坐标后重测为 0 重叠。
"""
import argparse
import runpy
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.figure as mfig


def collect(fig):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    items = []
    for ax in fig.axes:
        for t in ax.texts:
            txt = t.get_text().replace("\n", " / ").strip()
            if not txt:
                continue
            patch = t.get_bbox_patch()
            if patch is not None:
                bb = patch.get_window_extent(renderer)
            else:
                bb = t.get_window_extent(renderer=renderer)
            items.append((txt, bb))
    return items


def main():
    ap = argparse.ArgumentParser(description="matplotlib 文字重叠自检")
    ap.add_argument("script", help="绘图脚本路径（需调用 plt.savefig）")
    ap.add_argument("--top", type=int, default=12, help="最多列出多少对重叠")
    args = ap.parse_args()

    captured = {}
    orig_savefig = mfig.Figure.savefig

    def _hook(self, *a, **kw):
        captured["fig"] = self
        return orig_savefig(self, *a, **kw)

    mfig.Figure.savefig = _hook
    try:
        runpy.run_path(args.script, run_name="__main__")
    finally:
        mfig.Figure.savefig = orig_savefig

    fig = captured.get("fig")
    if fig is None:
        print("❌ 没能捕获 figure —— 请确认脚本最后调用了 plt.savefig")
        return 2

    items = collect(fig)
    print("检测到 %d 个文字元素（含带框标签）" % len(items))
    print("-" * 88)

    bad = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            t1, b1 = items[i]
            t2, b2 = items[j]
            if b1.overlaps(b2):
                ox = min(b1.x1, b2.x1) - max(b1.x0, b2.x0)
                oy = min(b1.y1, b2.y1) - max(b1.y0, b2.y0)
                bad.append((t1[:34], t2[:34], ox, oy, ox * oy))

    bad.sort(key=lambda x: -x[4])
    if not bad:
        print("✅ 无重叠 —— 所有文字框互不遮挡")
        return 0

    print("⚠️  发现 %d 对重叠（按重叠面积降序）：" % len(bad))
    for t1, t2, ox, oy, area in bad[: args.top]:
        print("  [%8.0fpx²  x%5.0f y%5.0f]  「%s」 <-> 「%s」" % (area, ox, oy, t1, t2))
    print()
    print("修法：把重叠标签沿 x 或 y 方向挪开（改绘图脚本里的坐标），重跑本脚本直到 ✅")
    return 1


if __name__ == "__main__":
    sys.exit(main())
