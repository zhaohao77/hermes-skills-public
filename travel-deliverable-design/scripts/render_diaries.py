# -*- coding: utf-8 -*-
"""日记作文纸专用收口：渲 6 张 A4 日记纸 → 同步「两个」目录 → 重建 14 页 PDF。

为什么单独一个脚本（某日 实测踩坑）：
    finish_a4.py 只渲 6 页 A4（dX_a4.html），**不含日记纸渲染** —— 它只把已有的
    a4_DIARY_DN.png **复制**到桌面。所以改了 a4/_diary_N.html（提示语/日期/线路）后
    只跑 finish_a4.py == 没改；PDF 里仍是旧日记页。
    实测症状：PDF mtime 停在旧时刻，而 a4/_pdf_pages/* 与 a4_DIARY_D3.png 已是新时刻。

用法（改顶部路径后）：
    python render_diaries.py            # 渲 + 同步 + 重建 PDF
    python render_diaries.py check      # 只打印 mtime/字节，判断 PDF 是不是旧包

验证：① 6 张 DOM 高必须 == 3508（多 1 行会被 overflow:hidden 静默裁掉）
      ② 三个位置（源 PNG / A4装订册 / 独立日记目录）字节一致
      ③ 改过提示语时，再用 vision 看一眼那页（换没换、有没有折行被裁）
"""
import hashlib
import os
import shutil
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ── 按项目改这里 ────────────────────────────────────────────────
BASE = Path(r"$HOME\.hermes\tmp\henan")
A4 = BASE / "a4"                      # 日记源 _diary_N.html 与产物 a4_DIARY_DN.png
DESK = Path(r"$HOME\Desktop\河南6日亲子游")
BOOKLET = "A4装订册"                   # 桌面装订册子目录
DIARY_ALT = "日记作文纸"                # 独立日记纸目录（旧副本容易在这里残留）
COVER = A4 / "a4_COVER.png"
ROUTE_PAGE = A4 / "_pdf_pages" / "p02.jpg"   # 路线图页（"沿用"型，不会自动重渲）
PDF_NAME = "河南6日亲子游_旅行手账册_A4.pdf"
W, H = 2480, 3508                      # A4 @300dpi；A3 项目改 3508 × 4961
DAYS = range(1, 7)
# ──────────────────────────────────────────────────────────────

PDF = A4 / PDF_NAME


def show_mtimes(tag=""):
    rows = [(A4 / ("a4_DIARY_D%d.png" % d), "日记源PNG") for d in DAYS]
    rows += [(DESK / BOOKLET / ("Day%d日记作文纸.png" % d), "装订册副本") for d in DAYS]
    rows += [(PDF, "PDF")]
    print("── mtime 体检 %s" % tag)
    for p, label in rows:
        if p.exists():
            print("   %-22s %-10s %s  %8d B" % (p.name, label,
                  time.strftime("%m-%d %H:%M:%S", time.localtime(p.stat().st_mtime)), p.stat().st_size))
        else:
            print("   %-22s %-10s ❌缺失" % (p.name, label))
    if PDF.exists():
        newest = max([p.stat().st_mtime for p, _ in rows[:-1] if p.exists()] or [0])
        print("   → %s" % ("❌ PDF 早于页面，是旧包，需要重建" if PDF.stat().st_mtime < newest else "✅ PDF 不比页面旧"))


if len(sys.argv) > 1 and sys.argv[1] == "check":
    show_mtimes("(只查看)")
    raise SystemExit(0)

from PIL import Image                                        # noqa: E402
from playwright.sync_api import sync_playwright               # noqa: E402

rows = []
with sync_playwright() as p:
    br = None
    for kw in ({"channel": "msedge"}, {"channel": "chrome"}, {}):
        try:
            br = p.chromium.launch(headless=True, args=["--force-device-scale-factor=1"], **kw)
            break
        except Exception:
            continue
    if br is None:
        raise SystemExit("❌ 起不了浏览器（本机用 msedge channel）")
    ctx = br.new_context(device_scale_factor=1)
    for d in DAYS:
        html = A4 / ("_diary_%d.html" % d)
        out = A4 / ("a4_DIARY_D%d.png" % d)
        if not html.exists():
            print("   ❌ 缺源 %s" % html.name)
            continue
        pg = ctx.new_page()
        pg.set_viewport_size({"width": W, "height": H})
        pg.goto("file:///" + str(html).replace("\\", "/"), wait_until="load", timeout=90000)
        pg.wait_for_timeout(900)
        h = pg.evaluate("document.body.scrollHeight")
        ok = h <= H + 5
        if ok:
            pg.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": W, "height": min(h, H)}, timeout=90000)
        pg.close()
        rows.append((d, h, ok, out))
        print("  Day%d 日记纸 DOM 高 %s %s" % (d, h, "OK" if ok else "❌OVERFLOW（会静默截断，先改源）"))
    br.close()

for d, h, ok, out in rows:
    if not ok:
        continue
    shutil.copy2(out, DESK / BOOKLET / ("Day%d日记作文纸.png" % d))
    (DESK / DIARY_ALT).mkdir(exist_ok=True)
    shutil.copy2(out, DESK / DIARY_ALT / ("Day%d日记作文纸.png" % d))

order = [COVER, ROUTE_PAGE]
for d in DAYS:
    order += [A4 / ("a4_D%d.png" % d), A4 / ("a4_DIARY_D%d.png" % d)]
missing = [f for f in order if not f.exists()]
if missing:
    raise SystemExit("❌ 缺页，未重建 PDF：%s" % missing)
imgs = [Image.open(f).convert("RGB") for f in order]
imgs[0].save(str(PDF), save_all=True, append_images=imgs[1:], resolution=300.0, quality=88)
shutil.copy2(PDF, DESK / PDF_NAME)
print("  PDF %d 页 → %s (%.1f MB) + 桌面副本" % (len(imgs), PDF.name, PDF.stat().st_size / 1048576))

print()
show_mtimes("(收口后)")
for d in DAYS:
    a, b, c = (A4 / ("a4_DIARY_D%d.png" % d), DESK / BOOKLET / ("Day%d日记作文纸.png" % d),
               DESK / DIARY_ALT / ("Day%d日记作文纸.png" % d))
    sizes = {x.stat().st_size for x in (a, b, c) if x.exists()}
    print("  Day%d 三处字节 %s" % (d, "✅ 一致" if len(sizes) == 1 else "❌ 不一致 %s" % sizes))
print("  PDF md5 %s" % hashlib.md5(PDF.read_bytes()).hexdigest()[:12])
print("\n别忘了：改过提示语的那页用 vision 复核（换没换、有无折行被裁）。")
