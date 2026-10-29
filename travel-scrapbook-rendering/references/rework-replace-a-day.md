# 返工案例：替换某一天的落点（某日 · 河南6日 D5 洛阳→郑州）

用户原话：**「D5 改一下不去洛阳，去河南博物院，我已经预约 13:30 亲子票人工讲解 2 小时」**
—— 一句话，牵动 6 个文件/载体。本文件是那次返工的完整账目，下次遇到「某天改去哪」照这个清单走。

---

## 0. 本机文件地图（动手前先认门）

| 角色 | 路径 |
|:--|:--|
| **页面源码（真正的编辑对象）** | `~/.hermes/tmp/henan/scrapbook/d1.html` … `d5.html`（D2 叫 `d2_v4.html`） |
| 渲染脚本 | `~/.hermes/tmp/henan/render_d1_d4.py`、`render_d5.py`（改顶部 `JOBS` 即可） |
| 单页产物 | `scrapbook/page_D5.png` |
| **交付物** | `Desktop/河南6日亲子游/D5手账图.png` |
| hero 配图池 | `scrapbook/imgs_d5/`（另桌面 `配图/` 有副本，新增图从那儿拷） |
| **内部源数据** | `~/.hermes/tmp/henan/itin.json` ← ⚠️ 与手账图**必须同步**，见 §4 |
| 交付物（用户令冻结中） | `河南6日旅行攻略.docx`、`.xlsx`、`A4装订册/`、`旅行手账册_A4.pdf` |

> 冻结 ≠ 可以不管：**正因 itin.json 是"没人记得要改"的那个，它成了 某日 翻车的元凶**
> （读旧版 itin 的兄弟文件 `Desktop/行程数据_明细.json` 得出"龙门石窟在 D1"，被用户一句
> 「你记忆混乱了吧」打回）。权威顺序与踩坑记录见 `travel-fact-verification`。

---

## 1. 渲染脚本的必备输出（缺一不可）

```python
h = page.evaluate("document.body.scrollHeight")
w = page.evaluate("document.body.scrollWidth")
status = "OK" if h <= H + 5 else "OVERFLOW"
print("%-10s DOM %sx%s (目标 %sx%s) %s -> %s (%d KB)" % (...))
```
同步到桌面后**校验字节一致**（`src.stat().st_size == dst.stat().st_size`），不一致直接 `raise`。
本次输出：
```
d5.html    DOM 1080x2047 (目标 1080x1920) OVERFLOW -> page_D5.png (911 KB)   ← 第一版
d5.html    DOM 1080x1920 (目标 1080x1920) OK       -> page_D5.png (781 KB)   ← 压完
page_D5.png -> D5手账图.png  781 KB / 781 KB  一致
```

## 2. 那 8 处一起换（本次逐项）

| # | 位置 | 洛阳版 → 郑州版 |
|:-:|:--|:--|
| 1 | `<h1>` | `开封 → 洛阳 · 龙门石窟` → `开封 → 郑州 · 河南博物院` |
| 2 | 副标题 | `高铁 65 分钟` → `高铁 21 分钟` |
| 3 | hero | `imgs_d5/lu_08.jpg`（龙门）→ `imgs_d5/henanmuseum_1.jpg`（莲鹤方壶） |
| 4 | intro | 四大石窟/卢舍那 → 国家一级馆/17 万件/贾湖骨笛/妇好鸮尊/莲鹤方壶 |
| 5 | booklink | 初中历史会讲 → 课本夏商周的黑白文字 vs 实物 |
| 6 | 节点 1–6 | `08:50 上车` 保留；车次改 `G2207 开封北 09:54 → 郑州东 10:15`；交通改 `郑州东→博物院 打车 25 分 / 地铁 5 号线→2 号线→关虎屯 C 口`；核心节点改 `13:30–15:30 人工讲解 2 小时【已预约】`；末节点改"住郑州 + 两片区二选一" |
| 7 | 费用卡 + 今天要办 | `龙门石窟约 180 元(2成人)` → `河南博物院 免费(讲解已预约)`；`订洛阳今晚住宿` → `订郑州今晚住宿` |
| 8 | 必吃 + 气泡 | 洛阳水席/不翻汤 → 郑州烩面（合记/萧记/惠丰源）+ 方中山胡辣汤 + 健康路夜市；气泡加 `🪪 刷身份证入馆` |

**跨天耦合项（最容易漏）**：原「今天要办」卡写着 *"确认 10/6 G406 车票（洛阳龙门 13:42 发）"*
→ 必须同步改成 *"（**郑州东站**发，车次比洛阳多）"*。当天换城市，**次日的站和车都跟着变**。

## 3. object-position 前后对比（vision 复核抓出来的）

```css
/* ❌ 第一版：鹤头颈被切掉，只剩翅膀+壶身 */
.hero-img img { object-fit:cover; object-position:center 40%; }
/* ✅ 改后：鹤的长喙、头颈、翅膀完整 */
.hero-img img { object-fit:cover; object-position:center 16%; }
```
判据：通栏 ≈1028×180 ≈ **5.7:1**，原图 4:3 → 缩放后高 771px，只取 180px 窗口，
`40%` 取的是 y≈275–485（壶身），`16%` 取的是 y≈124–334（头颈+壶口）。
→ **换图必看**，`vision_analyze` 问一句"主体头部在不在画面里"。

## 4. `itin.json` 同步（务必做，否则下次必踩）

改图**不等于**改数据源。用 Python 脚本改 JSON（**不要 PowerShell Set-Content**）：

```python
shutil.copy2(SRC, BASE / "itin.json.bak_<日期>_<改动名>")       # 先备份
data = json.loads(SRC.read_text(encoding="utf-8"))
d5 = data["days"][4]
d5["title"] = "开封 → 郑州 · 河南博物院"
d5["afternoon"] = "..."      # 逐字段覆盖
d5["tips"] = "..."
data["notes"].insert(0, "【某日 行程变更 · D5 改郑州】用户令：…")   # 变更留痕，便于回溯
data["overview"] = data["overview"].replace("…洛阳…", "…郑州…")       # 概览里也有旧落点
SRC.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
```
⚠️ `overview` 和 `notes` 里**也藏着旧城市名**——grep 一遍"洛阳/洛阳龙门/龙门石窟"确认没有残留。
⚠️ 兑现给用户前，**在对话里明说"itin.json 已同步 D5/D6"**，让冻结的交付物与源数据的差异显式化。

## 5. 用户的确认方式：给他「必须你定的 N 件事」

改完不要自成闭环。本次结尾列了三件待定，用户据此继续推进：
1. D5 住哪个片区（博物院/花园路 vs 郑州东站）→ 决定 D6 上午还能不能玩
2. D6 上午怎么安排 + 坐哪趟车
3. hero 配图（莲鹤方壶）是否要换成主展馆外观全景
