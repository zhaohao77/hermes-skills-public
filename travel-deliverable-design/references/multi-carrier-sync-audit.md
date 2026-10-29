# 多载体一次性收口 + 「订单/车次/票面 vs 交付物」核对排查

> 来源：某日 河南 6 日亲子游「把今天任务完成 / 根据最新情况全部更新我的出行 / 核对排查错误」全流程实证。
> 回答两类问题：**① 改了一处，要同步哪几个文件？② 出发前，交付物里哪些数字该拿什么去对？**

---

## 一、收口链：一个行程 = 6 类载体（漏一个用户就看到旧内容）

| 载体 | 活源 | 规格 | 落地 | 脚本 |
|:--|:--|:--|:--|:--|
| 9:16 手账图 | `~/.hermes/tmp/<trip>/scrapbook/dN.html`（D2 真源可能是 `d2_v4.html`） | 1080×1920 | 桌面 `DN手账图.png` | `render_pages_<date>.py` |
| A4 装订册页 | `a4/dN_a4.html` + `a3/d2_a3.html`（**独立 HTML，会独自漂移**） | 2480×3508 | 桌面 `A4装订册\0N_DayN手账.png` | `finish_a4.py` |
| 装订册 PDF | 上面的 PNG + `a4/a4_COVER.png` + `a4/_pdf_pages/p02.jpg`（路线图页）+ `a4_DIARY_DN.png` | 图拼页 | 桌面 `*_旅行手账册_A4.pdf` | PIL `save_all` |
| Word 攻略 | 桌面 docx（+ `tmp/*_updated.docx` 镜像，**两边 md5 必须一致**） | — | 桌面 | python-docx / zipfile |
| Excel 明细 | `tmp/<trip>行程明细*.xlsx`（桌面常**没有** xlsx，别擅自新建） | — | tmp | openpyxl |
| 路线图 | `draw_map_wide.py`（横版，进 Word 内嵌）＋ 竖版 1080×1920 PNG | 2658×1514 / 1080×1920 | 桌面 + docx 内嵌 + PDF p02 | matplotlib |

**PDF 页序（14 页版）**：封面 → 路线图页(`p02.jpg`) → (DayN 手账 + DayN 日记纸) × N。
补一天手账页 = **13 → 14 页**；改完用 `pypdf.PdfReader(pdf).pages` **实数一遍**（别只信脚本打印）。

**只在一处改就会不一致的三处**：
1. **Word 内嵌图**（`word/media/image1.jpg` 常是路线图）—— 独立 PNG 改对了，docx 里那张还是旧的；
2. **PDF 的路线图页**（`_pdf_pages/p02.jpg` 上游写"沿用"，不会跟着重渲）；
3. **A4 变体页** —— 与手账源是两份 HTML，改版后必须逐个变体文件做关键词计数（SKILL.md 铁律 23 ①）。

---

## 二、Word 内嵌图片「原位替换」（不重生成 docx，图片数不变）

比整篇重生成稳得多：**只换 zip 里那一个 media 条目**，其余原样 `writestr`（保留 `ZipInfo` 的压缩方式）。

```python
import zipfile, shutil, hashlib
src = r"$HOME\Desktop\<trip>\<攻略>.docx"
new_bytes = open(r"...\_word_mapimage1.jpg", "rb").read()      # 新图，序号与文件名必须仍是 image1.jpg
zin = zipfile.ZipFile(src)
before = [n for n in zin.namelist() if n.startswith("word/media/")]
old_md5 = hashlib.md5(zin.read("word/media/image1.jpg")).hexdigest()[:12]
tmp = src + ".tmp"
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for it in zin.infolist():
        data = zin.read(it.filename)
        if it.filename == "word/media/image1.jpg":
            data = new_bytes
        zout.writestr(it, data)
zin.close(); shutil.move(tmp, src)
# 校验：media 条目数不变（本轮 11→11）、image1 md5 变了、python-docx 仍打得开且 inline_shapes 数不变
```

**收尾三查**：① media 条目数不变；② 目标图 md5 已变；③ `docx.Document(path)` 打得开且 `len(d.inline_shapes)` 不变。
（Word/浏览器**开着**时覆盖会失败 → 先写 `.tmp` 再 `move`。）

---

## 三、核对排查：「订单/车次/票面」→ 交付物

**出发点：把用户手里的"事实凭证"拉出来，逐条对交付物上的字。**
用户主动说「我买了 X 车次 / X 门票」时，**凭证（12306 / 携程订单）才是唯一权威**，攻略文本一律可能是旧版。

| 拿什么去对 | 怎么取 | 能抓到什么错（本轮实测） |
|:--|:--|:--|
| **12306 官方车次** | 本机 `mcp-server-12306`（写法见下） | 停站时长写错（"只停 5 分钟"实为**停 11 分钟**）；到发时刻、班次 |
| **携程订单** | `my.ctrip.com` 页面（写法见 3.2） | 票面口径（不限次 / 单次 / 场次）、实付金额与成人·优待张数、住宿晚数与入住人 |
| **景区公告 / 公众号** | 搜索 + 问道 | 演出需**当日公众号抢约**（抢不到就看不了）；节假日限流停售 |
| **地图类资源** | 重出 + 原位替换 | 地图里残留**已取消的城市**（本轮 Word 内嵌图与 PDF p02 都还画着洛阳） |

### 3.1 12306 车次核验（本机现成能力，免装东西）

```python
import sys, asyncio, json
sys.path.insert(0, r"$HOME\AppData\Roaming\uv\tools\mcp-server-12306\Lib\site-packages")
from mcp_12306.services.ticket_service import get_train_route_stations_validated, station_service

async def main():
    await station_service.load_stations()          # ★ 必须先加载 3384 个车站，否则报"出发站无效"
    r = await get_train_route_stations_validated({
        "train_no": "G503", "from_station": "北京西", "to_station": "株洲西", "train_date": "某日"})
    d = json.loads(r[0]["text"])
    for s in d["stations"]:
        print(s["station_no"], s["station_name"], s["arrive_time"], s["start_time"], s["stopover_time"])

asyncio.run(main())
```

用 `~/AppData/Roaming/uv/tools/mcp-server-12306/Scripts/python.exe` 跑（自带 httpx2 等依赖）。
它返回**经停站全表（含每站停几分钟）**，是核"停站/到发时刻"最快的路。
（`search.12306.cn/search/v1/train/search?keyword=G503&date=YYYYMMDD` 可先查车次 ↔ 始发终到，
但这只给起终点、不给经停，停站分钟必须走上面这个接口。）

### 3.2 携程订单怎么读（`my.ctrip.com`）

> ⚠️ `life/ctrip-wendao` 是**用户自有技能**（curator 无权写入），所以这份配方记在这里，
> 不落在那个技能里；如果你有权限，建议 `hermes curator adopt ctrip-wendao` 后把它并回去。

**先记住：问道 API 查不到个人订单** —— 实测问「查我携程账号上的订单」，它明确回复
「我无法直接访问您的携程个人账号订单数据」→ **订单只能走页面（带登录态）**。

1. Edge 调试模式（`--remote-debugging-port=9223 --remote-allow-origins=* --user-data-dir=$HOME\EdgeProfile`）
   → Playwright `connect_over_cdp("http://127.0.0.1:9223")`。
2. 打开 `https://my.ctrip.com/`（用户已登录；出现「**尊敬的黄金贵宾**」= 登录态正常）
   —— **首页直接列出近期待出行订单**（门票 / 酒店 / 讲解，含使用日期、订单号、金额）。
3. 要全部订单：点页面里的「**更多订单**」→ `https://my.ctrip.com/myinfo/all`（近一年；更早须 App / 95010）。
4. 取数：`page.inner_text("body")` 直接解析。
   ⚠️ **别"猜 URL"** —— 本轮一次串 3 个候选 URL、各等 7 秒，重 SPA 直接拖到超时；
   **先开首页再点页面里的链接**，单页 8 秒内出结果。

**⚠️ 订单标题 = 票规的第一手来源**（比任何攻略站都准，核对时**逐字**读）：

| 订单标题原文片段 | 含义 |
|:--|:--|
| 万岁山武侠城门票(赠翰园碑林+城墙景区+铁塔公园门票)（**单日不限次入园**） | 当日可反复进出；赠三园随票 |
| 清明上河园门票(**当日且单次有效**) | 当日有效、**出园不可再进** |
| 只有河南…**12:00场**-幻城剧场 | 已锁定场次（≠ 普通门票） |

→ 「不限次 / 单次 / 几点的场」直接决定玩法：票面写「单次」的园，图上必须写"**出园后不可再进**"。

**⚠️ 部分订单「仅支持手机端查询」**：桌面端点详情只会提示「此订单仅支持手机端查询，扫描二维码可直接访问」
→ 拿不到"使用说明 / 退改规则"。**降级写法**：交付物上写「**有效期以票面为准**」，别硬写成某一档
（本轮万岁山赠三园的有效期就因此改成中性表述）。

**费用写法**：门票行写成 `已付 XXX 元（成人 A×2 ＋ 优待 B×2）` —— 金额与**张数分档**都能被订单验证。

**问道 API（路 A）现状**：token 已写入 `hermes-home/.env` 的 `WENDAO_API_KEY`；
也可随时从 `https://www.ctrip.com/wendao/openclaw` 页面文本取（`re.search(r"token\s*([0-9a-f]{32})", body)`，页面同给过期日）。
调用特征：**单次约 20 秒**、返回约 1.4 KB Markdown。
⚠️ **它是第三方 AI 正文，进交付物前必须二次核实**：本轮用它查汴河游船票价，与开封本地宝/旅泊网/马蜂窝价差明显
（50/25 元 vs 40/60/30 元）→ 最终在图上写**区间**「夜游单程约 40–60 元/人」+「码头随买随用」。

---

## 四、批改与渲染的硬护栏（本轮一次改 6 个载体没返工）

1. **断言命中才改**：每条 `old` 必须 `count() == 1`，否则该文件**整体不落盘**并汇总报错（杜绝半新半旧）。
2. **先备份再写**：`dN_bak_<时间戳>.html`（备份名要 sanitize，别用含 `/` 的中文标签）。
3. **渲染后三查**：`document.body.scrollHeight` 必须 **== 1920**（手账）/ **== 3508**（A4）；
   关键串**在**、旧错串**不在**（用 `inner_text` 取正文再 `in`，别读源码）；源 PNG 与桌面 PNG **字节一致**。
4. **超框就不入库**：加内容后溢出的正确处理是**删冗余行**（本轮 D3 溢出 20px → 删掉与节点重复的一行），
   不是压字号（零余量页见 SKILL.md 铁律 22/23）。`overflow:hidden` 会**静默截断**。
5. **图片类资源不随文字更新**：改完文字后单独确认"地图/示意图/内嵌图"有无旧版残留。

---

## 五、子任务（delegate）收口纪律

- **拆分前提：文件域互不重叠**（本轮：A=手账源+桌面 PNG / B=Word+xlsx / C=A4+PDF），否则并行互相覆盖。
- **超时=半成品**：先看 `cache/delegation/live/deleg_*/task-N.log` 尾部 + 产物时间戳，盘点改到哪，**从断点收口**。
- **自报产物一律复核**：本轮子任务报告"校验通过"，复核仍发现 `a4/d3_a4.html` 残留旧串一处，
  以及它自认"改不了"的项（Word 内嵌图）需要主会话动手。
- **验收口径由主会话重跑并打印**：DOM 实高 / 关键串 / PDF 页数 / md5 / 图片数 —— 五项一套脚本一次出。

---

## 六、本轮现成脚本（改路径即可复用，均在 `$HOME\.hermes\tmp\henan\`）

| 脚本 | 干什么 |
|:--|:--|
| `fix_pages_<date>.py` | 手账页批量外科式改写（断言命中 1 次 + 自动备份 + 未命中不落盘） |
| `render_pages_<date>.py` | 渲染 5–6 页 1080×1920 + 三查 + 覆盖桌面 PNG |
| `finish_a4.py` | A4 六页重渲（2480×3508）+ 重建 14 页 PDF + 同步 `A4装订册\` |
| `fix_map_<date>.py` | 修地图脚本 → 重出横版图 → 合成 A4 路线图页 p02 / 桌面竖版 → **原位替换 Word image1.jpg** |
| `ctrip_my.py` / `ctrip_allorders.py` | 读携程本人订单（首页 / 全部订单）—— 见本文件 3.2 |
