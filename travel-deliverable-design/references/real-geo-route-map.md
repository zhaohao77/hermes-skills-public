# 真实地理路线图绘制配方（GeoJSON 省界 + 主图/插图双视图）

> 来源：某日 河南6日亲子游。用户连续否定三版"手工摆位示意图"，最终要求
> 「按照中国地图的形式」后跑通。**下次做带城市的路线图，直接从本文件起步。**

---

## 0. 判断：什么时候需要真实地理版

| 场景 | 用什么 |
|---|---|
| 用户只是要"知道先去哪后去哪" | 纵向行程轴（Day 卡片）就够，**不需要地图** |
| 图上有**多个城市的相对位置** | **必须真实地理**——手工摆位一定会被看出来 |
| 用户说"位置不对""距离不对""按中国地图的形式" | 立刻切本配方，别再微调手工坐标 |

**关键教训**：手工摆位能糊过第一眼，但用户一看距离关系就识破。
**一次做对，比连改三版便宜。**

---

## 1. GeoJSON 数据源（阿里 DataV，免费、无需 key）

```
# 省级行政区划（含省内各地级市边界，用于画分市线）
https://geo.datav.aliyun.com/areas_v3/bound/{adcode}_full.json

河南 410000   湖南 430000   河北 130000   山西 140000   陕西 610000
（adcode = 6 位行政区划代码；带 _full 表示含下级分区）
```

**下载注意**：
- ❌ PowerShell `New-Object System.Net.WebClient` + `DownloadFile` → 实测**静默失败**（文件不存在）
- ✅ **Python `urllib.request` + 浏览器 UA 可行**：
  ```python
  req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
  data = urllib.request.urlopen(req, timeout=30).read()
  ```
- 体量参考：河南 150 KB / 18 个 feature，湖南 172 KB / 14 个 feature

---

## 2. 城市经纬度（本次实测值，可复用）

| 城市 | 经度 | 纬度 |
|---|---|---|
| 洛阳 | 112.45 | 34.62 |
| 郑州 | 113.63 | 34.75 |
| 中牟 | 113.98 | 34.72 |
| 开封 | 114.31 | 34.80 |
| 长沙 | 112.94 | 28.23 |

⚠️ **中牟/郑州的经度容易记反**（中牟 113.98 在郑州 113.63 的**东边**）。

---

## 3. 大圆距离（haversine）——图上标真实里程

```python
import math
def hav(a, b):
    """a, b = (lon, lat) 元组，返回公里"""
    R = 6371.0
    la1, lo1 = math.radians(a[1]), math.radians(a[0])
    la2, lo2 = math.radians(b[1]), math.radians(b[0])
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2 * R * math.asin(math.sqrt(h))
```

**本次算出**：

| 路段 | 直线（大圆） | 实际道路 | 交通 |
|---|---|---|---|
| 长沙 → 郑州 | **728 km** | — | 🚄 3h48 |
| 郑州 → 中牟 | **32 km** | 40 km 级 | 🚕 40 分 |
| 中牟 → 开封 | **31 km** | **43.0 km**（高德实测） | 🚕 约 49 分 |
| 开封 → 洛阳 | **171 km** | — | 🚄 1h05 |
| 洛阳 → 长沙 | **712 km** | — | 🚄 3h37 |

> ⚠️ 「开封→洛阳 / 洛阳→长沙」两行来自**洛阳仍在行程里的旧版本**。某日 改版后
> 洛阳已移出（D5 = 郑州·河南博物院），此处仅作**直线/道路口径对照的样本**保留，**别当现行行程**。

### ⚠️ 口径纪律

**直线距离 ≠ 导航道路里程**（中牟→开封差 **12 km**：直线 31 / 道路 43.0）。
同一段路在**图上**和**攻略文档里**必须口径一致，或**两者都标**并注明。
本次就出现了"文档写 38.6 km、图写 31 km"的打架 → 主动向用户说明并统一；
某日 用高德路线复核后，**道路里程应为 43.0 km**（38.6 km 偏短，已作废）。

---

## 4. 双视图布局（解决"河南四城挤成一团"）

**问题**：5 城纬度跨度 28.23°N–34.80°N（6.57°），
但**河南四城只跨 0.18° 纬度、1.86° 经度** → 等比例画时四城重叠成一个点。

**解法 = 主图 + 插图**：

```python
fig = plt.figure(figsize=(10.2, 5.4), dpi=150)     # 最终 1353×831
fig.patch.set_facecolor("#FDF6E3")

# ---- 主图：湖南 + 河南全省 ----
ax = fig.add_axes([0.015, 0.02, 0.575, 0.96])
ax.set_xlim(109.6, 116.6); ax.set_ylim(25.6, 36.6)
ax.set_aspect("equal")            # 保持地理比例，别拉伸
ax.axis("off")
# 主图上用红色虚线框标出放大区域
ax.add_patch(FancyBboxPatch((111.9, 34.1), 2.9, 1.15, boxstyle="round,pad=0.04",
                            fill=False, edgecolor="#C0392B", linewidth=1.6,
                            linestyle=(0, (5, 4)), zorder=3))

# ---- 插图：河南四城放大 ----
ax2 = fig.add_axes([0.605, 0.22, 0.385, 0.60])
ax2.set_xlim(112.1, 114.7); ax2.set_ylim(34.35, 35.05)
ax2.set_aspect("equal")
ax2.set_title("河南四城（放大）", fontsize=11.5, color="#8A6A3A", pad=6)
```

**主图上标注**：图注写「**河南（放大见右图）**」，让读者知道两个视图的关系。

---

## 5. 省界绘制函数

```python
def province(ax, fn, fc, ec):
    j = json.load(open(fn, encoding="utf-8"))
    for feat in j["features"]:
        g = feat["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            for ring in poly:                       # ring[0]=外环, 其余=内环/空洞
                xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
                ax.fill(xs, ys, facecolor=fc, edgecolor=ec,
                        linewidth=1.1, alpha=.55, zorder=1)

province(ax, "geo_hunan.json", "#E8F0E4", "#8FA88A")   # 湖南：绿调
province(ax, "geo_henan.json", "#F5E9D8", "#C09A6A")   # 河南：米调
```

**注意**：`fill` 会把每个地级市都填一遍 —— 顺带就得到了**省内的分市细线**，
看起来像真实地图，比只画省界轮廓好看得多，且**免费**。

---

## 6. 本配色与手账图统一

| 用途 | 色值 |
|---|---|
| 背景 | `#FDF6E3` |
| 墨色/描边 | `#3B3226` |
| 高铁（去程） | `#C0392B` |
| 返程高铁 | `#1F6FB2` |
| 打车 | `#2E8B57` |
| 途经中转 | `#8E6C88` |
| 湖南填充 | `#E8F0E4` / 边 `#8FA88A` |
| 河南填充 | `#F5E9D8` / 边 `#C09A6A` |

箭头：`FancyArrowPatch(..., arrowstyle="-|>,head_width=8,head_length=13", mutation_scale=1, shrinkA=11, shrinkB=11)`
（`shrink` 让线不戳进城市圆点里）。
弧线 `connectionstyle="arc3,rad=0.13"`（**别超过 0.2**，大了会穿出画布或压到标题）。

---

## 7. 踩过的坑（按重要性排序）

### ① emoji 变方块
`matplotlib` + `KaiTi` **没有 emoji 字形** → 🚕🚄 渲染成空心方块。
→ 图内文字用中文词（`打车` / `高铁`）。
→ 清理正则：`[\U0001F300-\U0001FAFF\u2600-\u27BF]`
（**逐条 replace 会漏**，实测漏了 2 个残留）

### ② 城市标签被箭头压住
`郑州` 标签放在圆点正下方 → 被红色箭头盖住。
→ 给容易冲突的城市**指定标签偏移方向**：
```python
OFF = {"洛阳": (-0.16, -0.075, "right"), "郑州": (-0.10, 0.075, "right"),
       "中牟": ( 0.00, -0.085, "center"), "开封": ( 0.16, 0.075, "left")}
```
标签一律加 **`bbox`（米色底 + 同色描边）**，压在线上也读得清。

### ③ 画布留大片空白
初版 `figsize=(10.2, 7.6)` → 下方空一块。
→ 压扁到 `(10.2, 5.4)`，两个 axes 位置重排（主图 `[0.015,0.02,0.575,0.96]`、
插图 `[0.605,0.22,0.385,0.60]`）。

### ④ 城市文字太挤
`长沙` 和 `湖南省` 标注碰在一起 → 拉大字号差、错开位置。

### ⑤ 主图/插图不对应
只画了放大框但没说明 → 图注补「放大见右图」+ 插图标题「河南四城（放大）」。

---

## 8. 验证清单（交付前逐条过）

| # | 检查 |
|---|---|
| 1 | `ax.set_aspect("equal")` 两个视图都设了吗（不设会变形） |
| 2 | 每个城市点是否**落在正确的省份填充内** |
| 3 | 有无 emoji 方块残留（vision 看图确认） |
| 4 | 城市标签有没有被箭头/连线压住 |
| 5 | 距离数字与攻略文档是否**口径一致** |
| 6 | 画布有无大片空白 |
| 7 | 主图↔插图的对应关系读者看得懂吗 |

**一律用 vision 逐张看图**，脚本自检只管文字↔文字，管不了线↔文字。

---

## 9. 嵌回竖版手账图

真实地图 PNG 生成后，替换竖版页面里原来的示意图容器：

```html
<div class="mapwrap" style="height:auto;border:none;background:transparent;padding:0;">
  <img src="file:///C:/.../map_real.png"
       style="width:100%;display:block;border-radius:14px;border:4px solid #fff;
              box-shadow:3px 4px 0 rgba(0,0,0,.10);">
</div>
```

- 图注文字同步改：`方位示意（按真实经纬度，南北向已压缩）` → **`真实地理路线（省界 + 实际距离）`**
- ⚠️ 替换 HTML 块时**别用非贪婪正则**（会只删外框留内层）→ 用
  `scripts/strip_block.py` 的 div 配对计数法，或把替换逻辑单独写成 `.py` 文件跑
- ⚠️ 渲染时按本文档 §7 的 Playwright 等待写法，`file://` 加载 100KB+ 大图**必须等 `images.every(complete)`**

---

## 10. 横版（Word 用）四联版式 ✅ 某日 已跑通

§4 是**竖版/单图**配方（`figsize=(10.2, 5.4)`，配手机手账）。
**给 Word 用的横版是另一套四联版式**，一次到位别重排：

```python
fig = plt.figure(figsize=(16, 9), dpi=170)          # 最终 2658×1514
fig.patch.set_facecolor("#FDF6E3")

# 标题（用 fig.text，不占 axes）
fig.text(0.5, 0.965, "<标题>", ha="center", va="center", fontsize=27, fontweight="bold")
fig.text(0.5, 0.928, "<副标题：日期｜人数｜城市链>", ha="center", va="center", fontsize=13.5, color="#6B5D4A")

ax  = fig.add_axes([0.025, 0.27,  0.40,  0.62])   # ① 左：出发省+目的地省大区域
ax2 = fig.add_axes([0.455, 0.335, 0.245, 0.50])   # ② 中：目的地密集区放大
ax3 = fig.add_axes([0.715, 0.335, 0.26,  0.50])   # ③ 右：出发省 vs 目的地省对比表
ax4 = fig.add_axes([0.025, 0.045, 0.95,  0.235])  # ④ 底：Day1–DayN 日程条
ax.set_xlim(109.6, 116.6); ax.set_ylim(25.6, 36.6)   # 主图范围
ax2.set_xlim(112.1, 114.7); ax2.set_ylim(34.36, 35.04)
```

**各面板要点**：

| 面板 | 内容 | 注意 |
|---|---|---|
| ① 主图 | 两省真实省界 + **只标两端城市**（图标 + 去/返程双弧线 + 距离标签） | 密集区用红虚线框标出，图注「放大见右图」 |
| ② 插图 | 密集区放大 + 区内城际连线（打车绿 / 高铁红） | `set_aspect("equal")` + `set_xticks([])` |
| ③ 对比表 | **纯 axes 手绘表格**（不引 pandas/matplotlib table） | 见下 |
| ④ 日程条 | 逐行 `ax.text` 的 `Day N` + 说明 + 底部 ★ 要点行 | 行距 `yy -= 0.145` |

**③ 对比表的画法**（避免 `plt.table` 的样式不可控）：
```python
ax3.set_xlim(0, 1); ax3.set_ylim(0, 1); ax3.set_xticks([]); ax3.set_yticks([])
ax3.set_title("出趟门，认识两个省", fontsize=11.5, color="#8A5A2B", pad=5)
# 列头
ax3.text(0.30, 0.93, "湖南（家）",  ha="center", fontsize=10.5, fontweight="bold", color="#1F6FB2")
ax3.text(0.75, 0.93, "河南（此行）", ha="center", fontsize=10.5, fontweight="bold", color="#C0392B")
y = 0.80
for k, a1, a2, b1, b2 in rows:              # 地理 / 人文 / 饮食 三行
    ax3.plot([0.04, 0.96], [y+0.12, y+0.12], color="#E4D8BE", lw=1, ls="--")  # 分隔虚线
    ax3.text(0.06, y+0.01, k, fontsize=10, fontweight="bold", color="#B5544A", va="center")
    ax3.text(0.19, y+0.05, a1, fontsize=8.8, color="#4A4238", va="center")     # 左栏主标签
    ax3.text(0.19, y-0.055, a2, fontsize=8.3, color="#6A6A6A", va="center")    # 左栏例证
    ax3.text(0.60, y+0.05, b1, fontsize=8.8, color="#4A4238", va="center")     # 右栏主标签
    ax3.text(0.60, y-0.055, b2, fontsize=8.3, color="#6A6A6A", va="center")    # 右栏例证
    y -= 0.27
```
**对比表 = SKILL.md 铁律 9**（出发省 vs 目的地省：地理 / 人文 / 饮食三行）。

**两版一致性铁律**：横版和竖版**必须用同一份省界 / 经纬度 / 距离数据**。
只改一版 → 同一趟行程在两张图里位置不同，用户一定会发现。

**交付**：横版 PNG → 转 jpg 覆盖 `.temp/map_*.jpg` → **重跑 `gen_docx.py`** → 校验字节/时间戳
（见 SKILL.md 铁律 6，漏一步用户就看到旧图）。
