# -*- coding: utf-8 -*-
"""全载体「旧口径串」扫描：一次列出所有还在用旧地名/旧里程/旧车次/旧方案词的文件。

用途：改完一批载体后，确认旧表述**一处不剩**（skill 铁律 23 ⑥ / 自检清单 #18）。
改顶部 HENAN / DESK / STALE 即可换项目。
"""
import io, re, sys, zipfile
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

HENAN = Path(r"$HOME\.hermes\tmp\henan")
DESK = Path(r"$HOME\Desktop\河南6日亲子游")
# 旧口径串：旧地名 / 旧里程 / 旧车次 / 旧方案词 / 旧时间
STALE = ["38.6", "4.6 km", "1.8–2.2", "2.4–2.7", "G311", "11:30 出发", "12:00 到目的地站",
         "酒店接驳", "酒店专车接", "汴梁不夜城", "21:00–22:00 出园", "洛阳", "龙门"]

FILES = []
for sub in ("scrapbook", "a4", "a3"):
    for p in (HENAN / sub).glob("*.html"):
        if "_bak" not in p.name:
            FILES.append(p)
for p in sorted(DESK.glob("*")):
    if p.suffix.lower() in (".html", ".md", ".json", ".csv", ".txt"):
        FILES.append(p)

print("扫描文件数:", len(FILES))
for f in FILES:
    try:
        t = io.open(f, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    hits = [s for s in STALE if s in t]
    if hits:
        print("  %-42s %s" % (f.name, hits))

wp = DESK / "河南6日旅行攻略.docx"
if wp.exists():
    xml = zipfile.ZipFile(wp).read("word/document.xml").decode("utf-8", "ignore")
    txt = re.sub(r"<[^>]+>", " ", xml)
    print("\nWord 里命中:", [s for s in STALE if s in txt])
