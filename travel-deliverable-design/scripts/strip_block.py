# -*- coding: utf-8 -*-
"""精确删除 HTML 里指定 class 的 div 块（按 div 开闭配对，不用非贪婪正则）。

为什么需要
----------
用正则 `<div class="X">.*?</div>` 删块时，遇到**嵌套 div** 会提前终止：
外框被删掉、内层块留了下来。
症状（某日 实测）：给手账页删配图槽位后，D1 还剩 1 张图、D2 还剩 2 张，
页面出现"裸的 .islot 块"，图片删不干净。

本函数按 `<div` / `</div>` 配对计数删除整块，可安全处理任意嵌套。

用法
----
    from strip_block import strip_class_blocks
    html = strip_class_blocks(html, 'islot')      # 删掉所有 class="islot" 的块
    html = strip_class_blocks(html, 'hero-cap')   # 删掉所有 class="hero-cap" 的块
    html = strip_class_blocks(html, 'inline-slots')

注意
----
- 只匹配 `<div class="X"`（属性顺序需为 class 在前）；若 HTML 里写成
  `<div id="y" class="X">` 则匹配不到 → 用 `strip_any_class_blocks()` 兜底。
- **统计残留时别被 CSS 骗了**：`.X { ... }` 的 CSS 定义也会被 `s.count('X')`
  命中，那不是"没删干净"。判断时应看 `<img` 数量或 `class="X"` 的出现次数。
"""


def strip_class_blocks(html: str, cls: str) -> str:
    """删除所有 `<div class="{cls}" ...>...</div>` 整块（支持嵌套）。"""
    out = html
    i = 0
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
        i = 0
    return out


def strip_any_class_blocks(html: str, cls: str) -> str:
    """兜底版：不管 class 属性在第几个位置，只要能找到 `class="{cls}"` 就删该 div 块。"""
    out = html
    while True:
        k = out.find('class="%s"' % cls)
        if k < 0:
            break
        i = out.rfind("<div", 0, k)
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
    return out


def count_images(html: str) -> int:
    """返回页面里 <img 的数量——比 count(class名) 更可靠的"删干净了吗"指标。"""
    return html.count("<img")


if __name__ == "__main__":
    # 自检：嵌套块应被整块删除
    demo = (
        '<div class="islot">'
        '<div class="cap">P1-IMG1</div>'
        '<img src="x.jpg">'
        '</div>'
        '<div class="keep">保留我</div>'
    )
    r = strip_class_blocks(demo, "islot")
    assert "<img" not in r, "嵌套块未删干净"
    assert "保留我" in r, "误删了其他块"
    print("OK  嵌套块整块删除，其他块保留")
    print("    <img 剩余:", count_images(r))
