# PIL 手工合成页配方（竖版路线图 / A4 路线图页 p02）

> 来源：某日 河南 6 日亲子游。用户原话：「**6 日行程线路竖版里面有问题，有字没有显示出来，出框架了**」。
> 适用：用 PIL (`ImageDraw.text`) 手工把「地图 + 文字块 + 卡片」拼成一张交付图（竖版路线图 1080×1920、A4 路线图页 2480×3508）。
> 反面教训：**先把内容堆上去、事后再量** → 长行直接跑出画布被裁，交付出去才被发现。

---

## 一、三条落盘护栏（缺一条就会交出错图）

```python
def wrap(draw, text, font, max_w):
    """先按空格切词装箱；词本身超宽再按字切（纯按字切会把 "1.6km/11分" 切碎）"""
    out, line = [], ""
    for token in text.split(" "):
        cand = (line + " " + token) if line else token
        if draw.textlength(cand, font=font) <= max_w:
            line = cand; continue
        if line: out.append(line); line = ""
        if draw.textlength(token, font=font) <= max_w:
            line = token
        else:
            cur = ""
            for ch in token:
                if draw.textlength(cur + ch, font=font) <= max_w or not cur: cur += ch
                else: out.append(cur); cur = ch
            line = cur
    if line: out.append(line)
    return out

def fit(draw, text, x, y, max_w, max_bottom, start, fill=INK, min_size=18, lh_ratio=1.24):
    """自动缩字号直到「行数 × 行高」装进 max_bottom；逐行断言不超宽"""
    sz = start
    while sz >= min_size:
        f = F(sz); ls = wrap(draw, text, f, max_w); lh = int(sz * lh_ratio)
        if y + len(ls) * lh <= max_bottom: break
        sz -= 2
    f = F(max(sz, min_size)); ls = wrap(draw, text, f, max_w); lh = int(max(sz, min_size) * lh_ratio)
    for i, ln in enumerate(ls):
        assert draw.textlength(ln, font=f) <= max_w + 1, "行超宽: %s" % ln[:16]   # ★ 护栏 3
        draw.text((x, y + i * lh), ln, font=f, fill=fill)
    return y + len(ls) * lh
```

- 字体：`C:/Windows/Fonts/msyh.ttc`（正文）/ `msyhbd.ttc`（标题）；中文必须显式给 ttf，别用 `load_default()`。
- **落盘前打印**「内容底部 y / 画布高」（如 `内容底部 y=1715 / 1920`）—— 这是唯一能证自己没出框的数字。
- **排版不够满也要打印**：第一版文字块只到 y=1059 / 1920（下方 860px 空白）→ 把日程文字 27px→38px、
  行间距 8px→44px 后才填到 1456。**「没超框」不等于「排得对」**。
- ⚠️ **每次改块（加卡片/加减行）都要重跑这个数字**：v2→v4 期间内容底部从 1456 → 1556 → **1715**，
  只是加了 1 张卡就吃掉 160px，接近 1920 时必须回头压上面日程区的字号/gap。

---

## 二、裁掉源图自带的标题与日程条（否则重复 + 缩小到看不清）

横版路线图（`draw_map_wide.py` 出的 2658×1514 PNG）**内部已含**：顶部标题条 + 底部「Day1–DayN 六天日程条 + 页脚」。
原样贴进竖版会有两个问题：
1. **重复** —— 竖版下方另写了 D1–D6（违反铁律 5），vision 直接报「标题出现两次」；
2. **看不清** —— 2658→~1010 缩放 0.38×，图内 11.5pt 字只剩约 10px。

```python
mp_c = mp.crop((0, 104, W0, int(H0 * 0.70)))   # 裁顶 104px（标题条）+ 裁底 30%（日程条与页脚）
# 2658×1514 → 2658×955
```

裁完把**可读的 D1–D6 写在竖版下方**（字号 28–38），信息不丢、也不重复。

---

## 三、本轮实测排版参数（可直接复用）

### 竖版 1080×1920
| 元素 | 位置/字号 |
|:--|:--|
| 主标题 | y=70 · 46px 粗体 · 居中 |
| 副标题（日期+城市链） | y=126 · 23–24px · 居中 |
| 地图（`mp_c` 等比，宽 992） | y=164–178 · 高约 356px |
| D1–D6 六行 | 地图下 24–40px 起 · `fit(start=28, max_bottom=985)` · 每行后 +18~22px |
| 分隔线 + 「D6 全天备选」小标题 | 日程区下方 · 28px 粗体 · 强调色 |
| **备选卡片 ×5** | 见下方「卡片式备选区」 |
| 页脚（来源/住宿口径） | 19–22px · 灰棕 · 贴底 `1920-12` |

### A4 路线图页 2480×3508（写成 `a4/_pdf_pages/p02.jpg`）
| 元素 | 位置/字号 |
|:--|:--|
| 主标题 / 副标题 | y=196 / 306 · 94–96px 粗 / 48–50px |
| 地图 | y=404 · 宽 2220 |
| D1–D6 | 地图下 50px 起 · `fit(start=50, max_bottom=1780)` · 行后 +22 |
| 备选卡片 ×5 | `card(..., S=1.72)` |
| 交通时刻 4 条（去程/城际/返程/住宿） | 38–50px · 每条前加 `◆ ` |
| 页脚 | 42px |

实测内容底部：v2 竖版 **1456/1920** · v4（5 张卡）竖版 **1715/1920**、A4 **3107/3508**。

### 卡片式备选区（v3 起，用户要求「**更美观 + 写景观特色**」）

用户原话：「**竖版的下面备选的要更加美观点，景观特色也要写出来**」 ——
从"一段文字列 4 个地方"改成**圆角卡片**，每卡固定三行：

```python
def card(draw, idx, name, meta, feat, x0, y0, x1, S=1.0, feat_sz=23, name_sz=29):
    pad = int(18 * S)
    h_card = int((24 + name_sz + 4 + 2 * feat_sz + 24) * S)      # 按"最多两行特色"预留高度
    draw.rounded_rectangle([x0, y0, x1, y0 + h_card], radius=int(14 * S),
                           fill=CARD_BG, outline=CARD_ED, width=max(1, int(1.4 * S)))
    draw.rounded_rectangle([x0, y0 + int(6 * S), x0 + int(7 * S), y0 + h_card - int(6 * S)],
                           radius=int(3 * S), fill=ACC)          # 左侧红色标条
    fn, fm, ff = F(int(name_sz * S), True), F(int(22 * S)), F(int(feat_sz * S))
    draw.text((x0 + pad, y0 + int(13 * S)), "%s %s" % (idx, name), font=fn, fill=INK)
    mw = draw.textlength(meta, font=fm)                          # 右上角「距离·耗时·门票」右对齐
    draw.text((x1 - pad - mw, y0 + int(19 * S)), meta, font=fm, fill=ACC)
    inner = (x1 - pad) - (x0 + pad)
    ty = y0 + int((name_sz + 22) * S)
    for ln in wrap(draw, feat, ff, inner):                       # 特色最多 2 行，逐行断言不超宽
        assert draw.textlength(ln, font=ff) <= inner + 1
        draw.text((x0 + pad, ty), ln, font=ff, fill=FEAT)
        ty += int(feat_sz * 1.26 * S)
    return y0 + h_card

for idx, name, meta, feat in ALTS:           # ALTS = [(序号, 名称, 距离·耗时·门票, 一句话景观特色), ...]
    y = card(d, idx, name, meta, feat, M, y, VW - M, 1.0) + 12
assert y <= VH - 40, "内容超出：%d" % y       # ★ 落盘前再断言一次整块高度
```

配色（与手账图米色系一致）：卡底 `#FFFAEC` · 卡边 `#E3D3B4` · 强调条/右上文字 `#B5544A` ·
特色文字 `#706048`；名称 `#3B3226`。

**实测**：竖版卡高 118px（S=1）、卡间距 12px，**5 张卡 = 650px**；A4 用 S=1.72（卡高约 202px、间距 22px）。
卡片区域占满剩余版面时，**把上方 D1–D6 的 `max_bottom` 相应上调/下调**（竖版用 985），
不要指望 `fit()` 自己把两段挤在一起。

**每张卡必须写「孩子能看到什么」**（不是复述门票政策）—— 本轮定稿：
熊猫馆·狮虎山索道俯瞰·南湖水禽 ｜ 巨型汝阳龙骨架·地震海啸剧场 ｜ 环湖步道+538 栋楼宇亮化 ｜
商代青铜·模拟考古 ｜ 黄河大堤「地上悬河」·1938 决堤纪事广场·将军坝。

---

## 四、验证：必须 vision 看图，不能只看数字

> 铁证：**第一版数字全都"合法"**（超宽断言都过，因为那一版根本没做断言，只人工看过），字号看着也正常，
> 但用户一眼就看出「有字没显示、出框架」；改完后再用 vision 复核，才又抓出「标题重复出现两次」。

`vision_analyze(image_url=<PNG 绝对路径>, question=...)` 提问模板（照抄即可）：
```
1) 有没有任何文字被裁掉、超出画布、或互相重叠？
2) 标题是否只出现一次？
3) 地图区域有没有被切掉关键内容（省份轮廓 / 城市名 / 路线箭头 / 对比表）？
4) 从上到下列出所有可见文字块，并说明每块是否完整可读。
```
改卡片区时再加一句：
```
5) N 张卡片是否排版整齐、间距均匀？每卡三行（名称 / 右上距离门票 / 景观特色）是否完整、无被边框裁掉或压线？
```

**改完 p02 必须重建 PDF**：`a4/_pdf_pages/p02.jpg` 是装订册第 2 页，改完跑 `finish_a4.py`
（它会重渲 A4 六页 + 重建 14 页 PDF + 同步桌面），再用 `pypdf.PdfReader(pdf).pages` **实数页数**。

---

## 五、现成脚本（`$HOME\.hermes\tmp\henan\`）

| 脚本 | 干什么 |
|:--|:--|
| `fix_vertical_map.py` | 第一版合成（无断言、字号偏小）—— 保留作为反面样本 |
| `fix_vertical_map2.py` | 第二版：`wrap`/`fit`/断言 + 裁图（标题条+日程条）+ 竖版与 A4 p02 一起出 |
| `fix_vertical_map3.py` | 第三版：**备选区改卡片式**（`card()` + 4 张） |
| `fix_vertical_map4.py` | **当前正式版**：D6「全天自由活动」框架 + 5 张卡（含黄河花园口） |
| `finish_a4.py` | A4 六页重渲 + 重建 14 页 PDF + 同步桌面（改过 p02 后必跑） |
