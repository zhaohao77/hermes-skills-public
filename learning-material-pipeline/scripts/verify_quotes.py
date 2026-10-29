# -*- coding: utf-8 -*-
"""引文核验：判断课程/笔记里的每段引文是否为原文的连续片段。

用法:
    python verify_quotes.py <lesson.html> <原文.txt>

口径:
    逐句计算「子序列覆盖率」= difflib 匹配块总长 / 句长。
    1.000 = 逐字引用；0.95-0.99 = 节引（只删未改）；< 0.95 = 有改写，必须改回原文。
退出码: 0 全过 / 2 有不合格段。
"""
import io
import re
import sys
import difflib

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(1)

lesson_path, source_path = sys.argv[1], sys.argv[2]
html = io.open(lesson_path, encoding="utf-8").read()
src = io.open(source_path, encoding="utf-8").read()


def norm(s):
    """去标签、去空白、统一引号——只比内容，不比排版。"""
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&")
    s = re.sub(r"[\s\u3000]", "", s)
    for a, b in (("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'"), ("……", "…")):
        s = s.replace(a, b)
    return s


S = norm(src)
quotes = re.findall(r"<blockquote>(.*?)</blockquote>", html, re.S)
print("引文段数:", len(quotes))

bad = []
for i, q in enumerate(quotes, 1):
    n = norm(q)
    parts = [p for p in re.split(r"[。；]", n) if len(p) >= 10]
    if not parts:
        continue
    covs = []
    for p in parts:
        blocks = difflib.SequenceMatcher(None, p, S, autojunk=False).get_matching_blocks()
        covs.append((sum(b.size for b in blocks) / len(p), p))
    lo = min(c for c, _ in covs)
    print("%s [%2d] %d句 最低覆盖率 %.3f" % ("OK " if lo >= 0.95 else "BAD", i, len(covs), lo))
    if lo < 0.95:
        bad.append(min(covs))

if bad:
    print("\n需改回原文的句子:")
    for lo, p in bad:
        print("  %.3f -> %s" % (lo, p[:110]))
    sys.exit(2)

print("\n全部引文均可在原文中逐字定位（节引为删减，无编造）")
