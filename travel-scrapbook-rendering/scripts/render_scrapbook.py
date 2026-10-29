# -*- coding: utf-8 -*-
"""
旅行手账图渲染：HTML -> 1080x1920 (9:16) PNG

用【本机 Edge CDP】渲染，不用 playwright 自带浏览器
（playwright 的 chromium 常没装，会报 `Executable doesn't exist ... chrome-headless-shell.exe`）。

用法：
    1) 改下面 JOBS 列表（html 文件 -> 输出 png）
    2) python render_scrapbook.py
    3) 截图后【一定要看一眼图】再交付（查乱码/溢出/留白）
"""
import os
import sys
import subprocess

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

# ---------- 配置 ----------
BASE = r"$HOME\.hermes\tmp\travel_scrapbook"   # 工作目录（html 与 png 都放这）
JOBS = [
    ("d1.html", "page_D1.png"),
    ("d2.html", "page_D2.png"),
]
W, H = 1080, 1920          # 9:16，别改
EDGE_PORT = 9223
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
EDGE_PROFILE = r"$HOME\EdgeProfile"


def edge_alive(port=EDGE_PORT):
    """探活 Edge CDP 端口（用户关掉窗口就没了，必须先起）"""
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "try{(Invoke-WebRequest 'http://127.0.0.1:%d/json/version' -UseBasicParsing "
             "-TimeoutSec 6).StatusCode}catch{0}" % port],
            capture_output=True, text=True, timeout=20)
        return "200" in (out.stdout or "")
    except Exception:
        return False


def ensure_edge():
    """掉线就重启 Edge（保留登录态，profile 持久化）"""
    if edge_alive():
        print("  Edge CDP OK (: %d)" % EDGE_PORT)
        return True
    print("  Edge 掉线，重启中……")
    subprocess.Popen([EDGE_EXE,
                      "--remote-debugging-port=%d" % EDGE_PORT,
                      "--no-first-run", "--no-default-browser-check",
                      "--user-data-dir=" + EDGE_PROFILE])
    import time
    for _ in range(10):
        time.sleep(3)
        if edge_alive():
            print("  Edge 已就绪")
            return True
    print("  ! Edge 起不来，检查路径/端口")
    return False


def strip_class_blocks(html, cls):
    """
    按 <div>/</div> 配对删除 class=cls 的整块。

    为什么不用正则：`<div class="x">.*?</div>` 这种非贪婪匹配会在
    第一个内层 </div> 处停下，只删掉外框，内层元素残留（页面照旧显示）。
    实测：删配图容器时残留了 .islot 内层块，图上还有图。
    """
    out, i = html, 0
    while True:
        i = out.find('<div class="%s"' % cls, i)
        if i < 0:
            break
        depth, j = 0, i
        while j < len(out):
            if out.startswith("<div", j):
                depth += 1
            elif out.startswith("</div>", j):
                depth -= 1
                if depth == 0:
                    j += 6
                    break
            j += 1
        out = out[:i] + out[j:]
        i = 0                      # 删完从头再找（偏移已变）
    return out


def render_one(page, html_path, png_path, base=BASE):
    url = "file:///" + os.path.join(base, html_path).replace("\\", "/")
    page.goto(url, wait_until="load", timeout=60000)
    page.wait_for_timeout(2500)                      # 等字体/图片
    h = page.evaluate("document.body.scrollHeight")
    warn = ""
    if h > H + 5:
        warn = "  <-- 超出 %d px，截图会截断：去压缩 margin/padding" % (h - H)
    page.screenshot(path=os.path.join(base, png_path),
                    clip={"x": 0, "y": 0, "width": W, "height": min(h, H)})
    size = os.path.getsize(os.path.join(base, png_path)) // 1024
    print("  %-16s DOM高度 %-5s -> %-16s (%d KB)%s" % (html_path, h, png_path, size, warn))
    return h


def main():
    os.makedirs(BASE, exist_ok=True)
    if not ensure_edge():
        return 1
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:%d" % EDGE_PORT)
        for html_file, png_file in JOBS:
            if not os.path.exists(os.path.join(BASE, html_file)):
                print("  ! 找不到 %s，跳过" % html_file)
                continue
            page = browser.contexts[0].new_page()
            page.set_viewport_size({"width": W, "height": H})
            try:
                render_one(page, html_file, png_file)
            except Exception as e:
                print("  ! %s 渲染失败: %s" % (html_file, str(e)[:90]))
            finally:
                page.close()
    print("\n完成。⚠️ 交付前必须自己看一眼图：中文乱码？溢出截断？底部留白？")
    return 0


if __name__ == "__main__":
    sys.exit(main())
