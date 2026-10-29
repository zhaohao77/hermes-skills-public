# -*- coding: utf-8 -*-
"""生成 N 张 A4 横行作文纸（孩子旅行日记）—— 某日 实测通过

用法：
    1. 改下面 DAYS 列表（每天：天序号 / 日期 / 当天路线 / 定制提示语）
    2. 确保本机 Edge 开着 CDP（默认 9223 端口）
    3. python gen_diary.py

产物：page_DIARY_D<N>.png，2480x3508（标准 A4 300dpi），可直接送打印店打 A4。

⚠️ 改行数后必须实测总高：见文件末尾 verify()，目标 3508（1 行 = 132px）。
"""
import io
import os
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

# ---- 配置 ---------------------------------------------------------------
CDP = "http://127.0.0.1:9223"          # 本机 Edge 调试端口（截图用，勿用 chromium.launch）
BASE = os.path.dirname(os.path.abspath(__file__))
TPL_PATH = os.path.join(BASE, "..", "templates", "diary_a4.html")
OUT_DIR = "."                          # 产物落盘目录（相对当前工作目录）
A4_W, A4_H = 2480, 3508                # A4 @300dpi

# ---- 每天一行：天序号 / 日期 / 路线（大字右侧小字） / 提示语（第二人称，按当天行程定制）
DAYS = [
    (1, "2026年10月1日 周四", "长沙 → 郑州 → 中牟",
     "今天坐了 3 小时 48 分钟的高铁，第一次到中原。写写路上看到的风景、听到的方言。"),
    (2, "2026年10月2日 周五", "中牟 · 只有河南·戏剧幻城",
     "看了 21 个剧场里的戏。哪一场最打动你？戏里讲了什么故事，你看懂了什么？"),
    (3, "2026年10月3日 周六", "中牟 → 开封 · 万岁山武侠城",
     "看了真马冲阵的《三打祝家庄》和漫天铁水的打铁花。写写最让你张大嘴巴的一瞬间。"),
    (4, "2026年10月4日 周日", "开封 · 清明上河园",
     "课本里那幅《清明上河图》活了。你在园里找到「虹桥」了吗？和书上画的像不像？"),
    (5, "2026年10月5日 周一", "开封 → 洛阳 · 龙门石窟",
     "卢舍那大佛有 17 米高，比五层楼还高。站在他脚下抬头看，你在想什么？"),
    (6, "2026年10月6日 周二", "洛阳 → 长沙 · 返程",
     "六天走完了郑州、中牟、开封、洛阳。这趟你最喜欢哪里？为什么？"),
]
# ------------------------------------------------------------------------


def build_html(tpl, day, date, route, prompt):
    return (tpl.replace("__DAY__", str(day))
               .replace("__DATE__", date)
               .replace("__ROUTE__", route)
               .replace("__PROMPT__", prompt))


def verify(page):
    """落版校验：总高必须正好 A4；行数变了要相应增减。"""
    m = page.evaluate(
        "() => ({h: document.body.scrollHeight, lines: document.querySelectorAll('.line').length})"
    )
    flag = "" if m["h"] == A4_H else "  ⚠️ 不等于 %d（1 行 = 132px，据此增减）" % A4_H
    return m, flag


def main():
    tpl = io.open(os.path.normpath(TPL_PATH), encoding="utf-8").read()
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP)
        for day, date, route, prompt in DAYS:
            tmp = os.path.join(OUT_DIR, "_diary_%d.html" % day)
            io.open(tmp, "w", encoding="utf-8").write(build_html(tpl, day, date, route, prompt))

            page = browser.contexts[0].new_page()
            page.set_viewport_size({"width": A4_W, "height": A4_H})
            page.goto("file:///" + os.path.abspath(tmp).replace("\\", "/"),
                      wait_until="load", timeout=60000)
            page.wait_for_timeout(1500)
            m, flag = verify(page)

            out = os.path.join(OUT_DIR, "page_DIARY_D%d.png" % day)
            page.screenshot(path=out, clip={"x": 0, "y": 0, "width": A4_W, "height": A4_H},
                            timeout=90000)
            page.close()
            print("  Day%d -> %s (%.0f KB)  行数 %s  总高 %s%s"
                  % (day, os.path.basename(out), os.path.getsize(out) / 1024,
                     m["lines"], m["h"], flag))
        print("  共 %d 张；记得按 '日记作文纸/DayN日记作文纸.png' 归档到交付目录" % len(DAYS))


if __name__ == "__main__":
    main()
