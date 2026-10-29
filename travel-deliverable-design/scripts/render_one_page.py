# -*- coding: utf-8 -*-
"""单页手账渲染 + 落版自检（不加 Word/xlsx/PDF 重生成）。

用途：临时新增一页手账图（如「行前预习·纪录片单」）时单独出图。
按 travel-deliverable-design「⏸ 阶段规则」：行程未定期间只动图，别顺手重跑 gen_docx / gen_xlsx / PDF。

用法：
  python render_one_page.py --html <页面.html> --out <输出.png> \
      [--copy-to <桌面目标.png>] [--width 1080 --height 1920]

自检：
  document.body.scrollHeight 必须 <= 目标高度；超了会被静默截断 → 退出码 1。
  ⚠️ 高度通过 ≠ 排版没问题：徽章文字被挤成两行、文字压卡片这类问题要看图，
     渲染后请用 vision 复核一遍（.daybadge 记得 white-space:nowrap）。

浏览器：优先用本机 Edge（channel=msedge, headless），独立实例，不打扰用户正在用的 Edge。
"""
import argparse
import shutil
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="单页手账渲染 + 落版自检")
    ap.add_argument("--html", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--copy-to", default="")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--wait-ms", type=int, default=1600)
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    html, out = Path(args.html).resolve(), Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        br = None
        for kwargs in ({"channel": "msedge"}, {"channel": "chrome"}, {}):
            try:
                br = p.chromium.launch(headless=True,
                                       args=["--force-device-scale-factor=1"], **kwargs)
                print("  浏览器: %s" % (kwargs.get("channel") or "bundled-chromium"))
                break
            except Exception as e:  # noqa: BLE001
                print("  launch %s 失败: %s" % (kwargs, str(e)[:70]))
        if br is None:
            raise SystemExit("没有可用浏览器内核")

        page = br.new_context(device_scale_factor=1).new_page()
        page.set_viewport_size({"width": args.width, "height": args.height})
        page.goto("file:///" + str(html).replace("\\", "/"), wait_until="load", timeout=90000)
        page.wait_for_timeout(args.wait_ms)
        h = page.evaluate("document.body.scrollHeight")
        w = page.evaluate("document.body.scrollWidth")
        page.screenshot(path=str(out),
                        clip={"x": 0, "y": 0, "width": args.width,
                              "height": min(h, args.height)})
        br.close()

    ok = h <= args.height + 5
    print("DOM: %sx%s -> 目标 %sx%s  %s" % (w, h, args.width, args.height,
                                           "OK" if ok else "OVERFLOW(会被截断!)"))
    if args.copy_to:
        dst = Path(args.copy_to)
        shutil.copy2(out, dst)
        print("已同步: %s (%d KB)" % (dst, dst.stat().st_size // 1024))
    print("落盘: %s (%d KB)" % (out, out.stat().st_size // 1024))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
