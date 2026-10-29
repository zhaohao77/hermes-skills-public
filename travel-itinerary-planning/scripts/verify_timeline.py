#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""行程「时间链」可行性验证器

把行程拆成一个个衔接环节，逐段计算「可用间隔」与「最小所需时间」，
输出可行性矩阵。用途：用户问"这个方案可行吗 / 验证可行性"时，
给出量化结论而不是"应该没问题"。

用法：
    python verify_timeline.py plan.json

输入 JSON 结构：
{
  "base_date": "某日",
  "checks": [
    ["D1", "郑州东站内换乘", "11:55", "13:15", 40, "同站换乘通道，大站留40分"],
    ["D1", "龙门站→出站+寄存+打车到石窟", "13:51", "14:35", 35, "出站10+寄存10+打车7km约20分"]
  ],
  "play": [
    ["D1", "龙门石窟", "14:35", "19:30"]
  ]
}

checks 每项：[天, 环节名, 起点HH:MM, 终点HH:MM, 最小所需分钟, 依据说明]
  - 最小所需分钟填 0 表示"固定车程，不做缓冲判定"（如已实测的高铁运行时长）
play 每项：[天, 内容, 起, 止]

判定阈值（可用间隔 gap vs 需要 need）：
  gap >= need + 15  -> ✅ 充裕
  need <= gap < need+15 -> ⚠️ 偏紧（建议提前 15-20 分钟出发）
  gap < need        -> ❌ 不足（必须调整）

经验值（来自实战）：
  同站换乘大站 ≥ 40 分；市区→车站 = 打车时长 + 进站 15 分；
  国庆/黄金周所有缓冲再上浮 15 分。
"""
import argparse
import json
import sys
from datetime import datetime


def to_min(hhmm, base_date):
    t = datetime.strptime(base_date + " " + hhmm, "%Y-%m-%d %H:%M")
    return t.hour * 60 + t.minute


def main():
    ap = argparse.ArgumentParser(description="行程时间链可行性验证")
    ap.add_argument("plan", help="plan.json 路径")
    args = ap.parse_args()

    with open(args.plan, "r", encoding="utf-8") as fh:
        plan = json.load(fh)

    base = plan.get("base_date", "2026-01-01")
    checks = plan.get("checks", [])
    play = plan.get("play", [])

    print("=" * 100)
    print("行程时间链可行性验证")
    print("=" * 100)
    print("%-4s%-30s%>6s%>7s%>6s%>6s  %s" % ("天", "环节", "起点", "终点", "可用", "需≥", "判定"))
    print("-" * 100)

    ok, warn, fail = 0, [], []
    for item in checks:
        day, name, a, b, need, why = item
        gap = to_min(b, base) - to_min(a, base)
        if gap < 0:
            gap += 24 * 60
        if need == 0:
            verdict = "·  固定车程"
        elif gap >= need + 15:
            verdict = "✅ 充裕"
            ok += 1
        elif gap >= need:
            verdict = "⚠️ 偏紧"
            warn.append((day, name, gap, need, why))
        else:
            verdict = "❌ 不足"
            fail.append((day, name, gap, need, why))
        print("%-4s%-30s%>6s%>7s%>5d分%>5d分  %s" % (day, name, a, b, gap, need, verdict))

    print("-" * 100)
    print("通过: %d 项 | 偏紧: %d 项 | 不足: %d 项" % (ok, len(warn), len(fail)))
    print()

    if warn:
        print("⚠️  偏紧项（缓冲 < 15 分钟，建议提前 15-20 分钟出发）：")
        for d, n, g, need, why in warn:
            print("   %s %s：可用 %d 分 / 需 %d 分 —— %s" % (d, n, g, need, why))
    if fail:
        print("❌ 不足项（必须调整行程）：")
        for d, n, g, need, why in fail:
            print("   %s %s：可用 %d 分 / 需 %d 分 —— %s" % (d, n, g, need, why))

    if play:
        print()
        print("=" * 100)
        print("每日有效游玩时长")
        print("=" * 100)
        for d, n, a, b in play:
            span = to_min(b, base) - to_min(a, base)
            print("  %-4s %-26s %3d 小时 %2d 分" % (d, n, span // 60, span % 60))

    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
