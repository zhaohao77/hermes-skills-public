# -*- coding: utf-8 -*-
"""打印/交付前体检（多载体一次性总检）。

为什么需要它：同一份行程散在 **6 类载体**里（9:16 手账图 / A4 变体页 / 合成 PDF / Word / 竖版路线图 / 单页图），
而这些源文件**各自独立维护、会互相漂移**。用户原话「A4纸版不对，D1 单独的内容和合并版有差异」
= 跨载体一致性；「全部再检查一下，有问题疑问的都可以找我确认，我要准备打印了」
= 规格/残留扫描 + 一份可直接回的「疑问清单」。

用法：改顶部 CONFIG（目录 / 变体对 / 关键事实 / 旧词 / 规格），`python preprint_audit.py`，逐段看输出。
判读：① 有 ❌/⚠️ 就先修；③ 的命中要人工判（地名可能来自菜名，如「洛阳水席」）。
配套：`scripts/diff_carriers.py`（逐行文本差异）、`scripts/scan_stale.py`（旧口径串扫描）。
"""
import html, io, re, sys, zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ─────────── CONFIG（换项目只改这一段）───────────
ROOT = Path(r"$HOME\.hermes\tmp\<项目>")
DESK = Path(r"$HOME\Desktop\<交付目录>")
SOURCES = [ROOT / s for s in ("scrapbook", "a4", "a3")]
PAIRS = [("D1", "scrapbook/d1.html", "a4/d1_a4.html")]          # 同一页的两套源
FACTS = {"13:45 出门": ["scrapbook/d1.html", "a4/d1_a4.html"]}   # 关键事实 → 应出现在哪些源
STALE = ["洛阳", "龙门", "G311", "38.6", "4.6 km", "07:00", "15:30 取", "待实时查询"]
EXPECT_PX = {"D1手账图.png": (1080, 1920), "A4装订册/01_Day1手账.png": (2480, 3508)}
PDF = "旅行手账册.pdf"          # 相对 DESK；None = 跳过
# ───────────────────────────────────────────────


def text_of(p):
    t = io.open(p, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|h[1-6]|li|tr|section)>", "\n", t)
    return html.unescape(re.sub(r"(?s)<[^>]+>", " ", t))


def norm(s):
    return re.sub(r"[\s·｜|,，。．:：()（）「」【】\-–—~～/]+", "", s)


print("=== ① 变体页 vs 主载体 文本差异（同一页两套源）===")
for day, main, variant in PAIRS:
    A = [l.strip() for l in text_of(ROOT / main).split("\n") if l.strip()]
    B = [l.strip() for l in text_of(ROOT / variant).split("\n") if l.strip()]
    na = {norm(x) for x in A if len(norm(x)) >= 6}
    nb = {norm(x) for x in B if len(norm(x)) >= 6}
    miss = [x for x in A if len(norm(x)) >= 6 and not any(norm(x) in y or y in norm(x) for y in nb)]
    extra = [x for x in B if len(norm(x)) >= 6 and not any(norm(x) in y or y in norm(x) for y in na)]
    print("  %s：主载体有/变体缺 %d 条；变体有/主载体无 %d 条" % (day, len(miss), len(extra)))
    for x in miss[:12]:
        print("     - " + x[:100])
    print("     判读：连续两轮仍在 miss 里 = 真缺口；只剩措辞/换行差异 = 正常")

print("\n=== ② 关键事实跨载体抽查 ===")
for k, files in FACTS.items():
    miss = [f for f in files if k not in io.open(ROOT / f, encoding="utf-8", errors="ignore").read()]
    print("  %-24s %s" % (k, "✅" if not miss else "❌ 缺: " + ", ".join(miss)))

print("\n=== ③ 旧口径 / 旧行程词扫描 ===")
any_hit = False
for d in SOURCES:
    for p in sorted(d.glob("*.html")):
        if "_bak" in p.name:
            continue
        hits = [k for k in STALE if k in io.open(p, encoding="utf-8", errors="ignore").read()]
        if hits:
            any_hit = True
            print("  %-24s %s" % (p.name, hits))
print("  （命中要人工判：可能是菜名/正常词，如「洛阳水席」「占位」）" if any_hit else "  ✅ 无残留")

print("\n=== ④ Word 文本扫描 ===")
for w in DESK.glob("*.docx"):
    xml = zipfile.ZipFile(w).read("word/document.xml").decode("utf-8", "ignore")
    txt = re.sub(r"<[^>]+>", "", xml)
    print("  %-30s 旧词: %s" % (w.name, [k for k in STALE if k in txt] or "无 ✅"))

print("\n=== ⑤ 交付物清单与规格 ===")
try:
    from PIL import Image
    import pypdf
    for f, px in EXPECT_PX.items():
        p = DESK / f
        if not p.exists():
            print("  ❌ 缺 %s" % f)
            continue
        real = Image.open(p).size
        print("  %-40s %s %s" % (f, "×".join(map(str, real)), "✅" if (px is None or real == px) else "❌ 期望 %s" % (px,)))
    if PDF:
        r = pypdf.PdfReader(DESK / PDF)
        dims = {(round(p.mediabox.width), round(p.mediabox.height)) for p in r.pages}
        print("  PDF %s：%d 页 · 尺寸集 %s" % (PDF, len(r.pages), dims))
except Exception as e:
    print("  （PIL/pypdf 不可用，跳过规格检查：%s）" % e)

print("\n=== ⑥ 交给用户的「疑问清单」草稿（每条一句、编号，他会回编号）===")
print("  1. <要他拍板的时间/取行李等口径：给 A/B 两个时刻各带缓冲分钟>")
print("  2. <未购票项（船票/讲解等）买不买>")
print("  3. <写死的事件型提示（如打铁花）是否改中性版>")
print("  4. <打印范围与版式确认（要不要只含手账页的 PDF）>")
print("  交付语里明确写：天气/演出属趋势信息、出行前 N 天复核；A4 打印说「按实际大小 100% 不缩放」。")
