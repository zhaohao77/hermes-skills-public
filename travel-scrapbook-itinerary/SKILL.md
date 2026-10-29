---
name: travel-scrapbook-itinerary
description: "Use when the user provides a travel itinerary, OCR itinerary text, table itinerary, screenshot-derived text, or rough trip idea with origin/destination/dates/must-go places and wants a Chinese 9:16 vertical travel scrapbook itinerary prompt pack or generated scrapbook images. Specializes in route-first travel-flow visualization: parsing days, evaluating feasibility, supplementing weather/temperature, transportation, lodging areas, attractions, food, timing, tickets, reminders, density-based page splitting, optional user-provided mascot sticker placement, replaceable photo slots, and AI image prompts/images for practical phone-readable travel handbook pages rather than generic travel guides or decorative collages."
---

# Travel Scrapbook Itinerary

## Mission

Turn a user's itinerary or rough trip idea into a route-first 9:16 Chinese travel scrapbook prompt pack or generated image set. Visual beauty is secondary; the first priority is that travelers can understand the route, timing, transfers, hotel changes, ticket/opening constraints, weather risks, and reminders while on the trip.

If an image-generation tool/API is available and the user asks to generate images, generate one 9:16 image per planned page by default. If no image tool is available, output copy-ready prompts plus replaceable image slot manifests.

## Public/Private Asset Boundary

This Skill is designed to be open-source safe. The public Skill must contain only reusable logic, prompt templates, configuration schema, and text style rules.

Do not assume or ship any proprietary cartoon IP. Use user-uploaded characters, a local private character profile, or generic public placeholder companions. Load `references/open-source-ip-policy.md` when preparing the Skill for public release, packaging, licensing, or character asset handling.

## Load These References

- Load `references/prompt-template.md` when writing final image prompts.
- Load `references/visual-style-guide.md` before writing page plans or prompts.
- Load `references/itinerary-structure-rules.md` when parsing screenshots/OCR itinerary text, handling "先不要生图", or deciding whether a sparse day should stay separate.
- Load `references/rough-idea-trip-builder.md` when the user gives only origin, destination, dates, and a few must-go places.
- Load `references/live-data-automation.md` when the user asks for weather/temperature prediction, nearby snacks/restaurants, group-buying/social-platform recommendations, lodging candidates, transport schedules, or fully automated trip planning.
- Load `references/itinerary-feasibility-rules.md` when the user asks whether the route is reasonable, asks for itinerary optimization, or asks Codex to supplement scenic/food visuals.
- Load `references/character-system.md` when the user provides character references, mentions mascots, or asks to include travelers as stickers.
- Load `references/replaceable-image-slots.md` when generating final image prompts, recording generated image results, or handling requests to replace photos inside an existing scrapbook page.
- Load `references/end-to-end-generation-workflow.md` when checking whether the Skill can turn a travel plan into final scrapbook images or when explaining the full pipeline.
- Load `references/default-config.yaml` when the user asks about settings, UI behavior, batch image generation, backend configuration, or public/private asset setup.
- Load `references/open-source-ip-policy.md` when the user asks about open-sourcing, licensing, sharing, character ownership, public repos, or preventing private IP leakage.

## Workflow

### 1. Normalize the Input

Accept plain text, OCR text from screenshots, tables, rough trip ideas, and casual descriptions. Preserve user-provided facts exactly: dates, origin/destination, must-go places, flight numbers, train numbers, times, hotel names, addresses, ticket prices, and notes must not be rewritten or "improved".

If the user provides only a rough idea, first build a practical itinerary with `references/rough-idea-trip-builder.md` and `references/live-data-automation.md`: identify assumptions, run live lookup for weather/temperature, transport, lodging, food/snacks, opening hours, and tickets when possible, then recommend route, transport, lodging areas, food, and page split before generating image prompts.

If a field is missing, write `待补充` or `未提供`. If adding nearby places, food, photos, or supply points, mark them as `建议补充`; never present them as confirmed itinerary facts.

### 2. Structure the Trip

Output a table under `【1. 行程结构化拆解】` with these columns:

`Day / 城市 / 交通 / 景点 / 酒店 / 美食 / 关键提醒`

Inside the cells, capture date, departure and arrival, flight/train number, departure and arrival time, hotel address, tickets, opening times, time cutoffs, user notes, day type, and risk warnings when present. Keep the table compact enough to read.

Classify each day as one or more of:

- `赶路日`: cross-city movement, flight/train, car pickup/dropoff, hotel switch, or tight transfer.
- `轻松游玩日`: same-city, low fixed-time pressure, mostly free activity.
- `重点提醒日`: ticket/opening-hour dependency, hard departure deadline, complex transfer, heavy route density, weather risk, or likely fatigue.

### 3. Decide Page Count by Information Density

Do not make one page per day mechanically. Build page groups by day density and route continuity.

If an earlier draft or user wording says `每天一页`, still run the density check unless the user explicitly insists that every day must be separate. The product goal is a phone-readable travel flow, not a rigid calendar.

Use these signals as single-page reasons:

- Cross-city transport.
- Explicit flight number or train number.
- Hotel switch.
- Two or more core attractions.
- Ticket, opening time, reservation, or hard cutoff reminder.
- Opening day or return day.

Merge adjacent days only when all are mostly true:

- Same city or same travel theme.
- Light same-city travel.
- Few fixed time points.
- No complex transport or hotel switch between the merged days, except a simple end-of-day return segment that can be treated as a reminder.
- The merged page still remains readable on a phone.

When a day is too packed, explicitly say `这天偏赶` and name the bottleneck: transfer time, opening hours, distance, hotel switch, weather, or too many attractions.

### 4. Plan Each Page as a Travel Flow

For every page under `【3. 每页内容规划】`, include:

- 页面标题: `Day X` or `Day X-Y` plus city/theme.
- 路线顺序: a clear ordered route using arrows.
- 必放信息: transportation, hotel, attractions, food, tickets, opening times, time reminders, weather, and warnings.
- 可补充视觉元素: landmark photos, food photos, train/plane/car icons, map fragments, ticket stickers, weather or packing hints.
- 可替换图片槽位: stable slot IDs for scenic, food, hotel, transport, and memory photo stickers.
- 角色动作建议: small traveler/mascot stickers matched to the page situation.
- 版式建议: large Day badge, route map logic, card placement, reminder bubble placement, and density control.

Make route logic visible: each page should have a gray dashed path or numbered route spine connecting transportation, hotel, attractions, food, and reminders in the correct order.

### 5. Use Characters as Supporting Stickers

Character priority is:

1. User-uploaded character reference images in the current request.
2. Local private profile at `private/character-profile.local.yaml`, if it exists.
3. Generic public placeholder companions from `references/character-system.md`.

Keep characters small. They should appear as corner stickers, interaction stickers, or reminder stickers, never as the page subject. If no private or user-provided characters are available, do not use proprietary names or distinctive private IP traits.

Choose actions by page type:

- 出发页: dragging luggage, waving, boarding plane/train.
- 山水页: taking photos, looking at scenery, surprised reaction.
- 赶路页: carrying luggage, catching train, checking time.
- 海边页: eating seafood, watching the sea, taking photos.
- 返程页: waving, packing luggage, boarding.

### 6. Generate Copyable Image Prompts

Under `【4. 每页生图提示词】`, write one complete prompt per page. Each prompt must be independently copyable; do not write "同上". Use `references/visual-style-guide.md` for visual grammar, then use `references/prompt-template.md` and fill every placeholder with the page's actual route and facts.

Also use `references/replaceable-image-slots.md` so the prompt describes distinct replaceable photo sticker slots rather than a flattened collage.

Every prompt must include:

- `vertical 9:16`.
- Chinese travel scrapbook itinerary page.
- Beige grid-paper background.
- Sticker-like cutout photos with white borders.
- Gray dashed route lines.
- Handwritten Chinese labels.
- Large `Day X` date bubble.
- Attraction, transport, food, hotel, ticket, weather, and reminder cards when relevant.
- Black handwritten Chinese text.
- Cute but practical layout.
- Clear route, high information density, and no clutter.

The prompt must read like a phone-readable travel process board, not a poster. Route order, time constraints, transport cards, hotel cards, weather cards, and reminder bubbles must be explicitly described before decorative elements.

### 7. Output in the Required Contract

For full prompt-generation requests, always use this section order:

`【1. 行程结构化拆解】`

`【2. 手账页数建议】`

State how many 9:16 images to create and why the split is route-readable. Include titles such as `Page 1: Day1｜抵达日`.

`【3. 每页内容规划】`

`【4. 每页生图提示词】`

`【5. 批量生成说明】`

For batch generation, default to 9:16, one image per page, all pages generated from their own prompt. Allow regenerating a single page by page number.

For full prompt-generation requests, include replaceable image slot manifests inside each page plan or under `【5. 批量生成说明】`; this is required for later photo replacement.

If the user selected `只拆解行程` or says `先不要生图 / 先拆解内容`, output only `【1. 行程结构化拆解】`, `【2. 手账页数建议】`, and `【3. 每页内容规划】`; add a compact `待补信息` note when fields are missing, and do not write final image prompts until the user asks for them.

If the user says an existing generated page is good and only wants to replace pictures, keep the page split, route, text cards, characters, and layout stable; ask for or infer the target slot ID, then generate a replacement instruction for that slot only.

## Hard Rules

- **⚠️ 批量复制到交付目录时，PowerShell 变量必须加花括号断开边界**（某日 踩坑，害用户看到旧图）
  拼接路径时写成 `page_` + 变量 + `.png` 的形态，若变量后紧跟中文（如「手账图」），PowerShell 会把
  **整个「变量+中文」当成一个变量名**（中文与 `-` 都是合法变量名字符）→ 该变量未定义 → 取空 →
  路径塌缩成同一个目标文件 → **循环 N 次全部写到同一个文件**（最后一个覆盖前面全部）。
  正确做法：给变量加花括号明确边界，即 `page_${d}.png` 与 `${d}手账图.png`。
  **症状识别**：循环里每次都"成功"，但交付目录里每个文件大小完全一样；本次导致 D1–D4 全变成 D5 的图。
  **强制校验**：每次批量复制后立刻比对源与目标的字节大小与时间戳，不一致就停下排查，不要相信"复制成功"的输出。
  同类风险适用于任何 `"$var中文"`、`"$var-英文"`、`"$var数字"` 的拼接。
- **同一信息不要在一页里出现两次**（某日 用户当场指出 D4 重复）：
  典型错法 —— 行程节点里写"成人120·儿童60→4人合计360元"，页面底部「今日费用」卡又写"门票360元"。
  **正确分工**：**行程节点只说"怎么用/要注意什么"**（如"已提前预约 · 门票三日有效 · 千场演出全含"），
  **价格一律只放底部费用卡**。同理，车次/房型/营业时间也各自只出现一次，出现多次要合并。
  自检：生成后按"元/¥/公里/分钟"等关键词扫一遍，看同一数字是否重复。
- Optimize for travel-day usability before aesthetics.
- Make route, time, weather, and reminders visible.
- Highlight hard time points, departures, arrivals, opening hours, ticket prices, hotel switches, and weather risks.
- Never change flights, trains, hotels, addresses, ticket prices, or user notes.
- For weather, transport schedules, hotel availability/prices, restaurant status, ticket policy, and opening hours, run live lookup by default. Use fallback sources automatically if the first source fails; only mark `待实时查询` after lookup attempts fail.
- Do not invent non-existent places.
- Mark additions as `建议补充`.
- Merge low-density days when it improves readability.
- Keep all generated images vertical 9:16 by default.
- Do not use proprietary character names, likenesses, or private reference assets unless the user supplied them in the current request or a local private profile is present.
- Keep output direct, copyable, and free of generic travel-guide filler.

---

## 🖥 本机适配（Hermes Desktop · 某日 落库实测）

**本技能无 `scripts/`**，是纯方法论 + 提示词模板，执行时要接本机的两个能力：

### 1. 生图后端：**用 HTML/CSS 渲染，不要喂文生图模型** ⚠️（某日 实测结论）

**踩过的坑（务必先读）**：本技能默认设想"用 AI 生图模型直接画 9:16 手账页"。
在 Hermes 本机用 `Kwai-Kolors/Kolors`（SiliconFlow）实测 D2 一页 —— **彻底失败**：

| 技能要求 | 文生图实测结果 |
|---|---|
| 清晰可读的中文标签 | ❌ 全是乱码伪汉字（"签着""朱脉脉逊"） |
| 灰色虚线路线 + 编号节点 | ❌ 完全没有 |
| Day 徽章 / 时间卡 / 门票卡 / 提醒气泡 | ❌ 一个都没有 |
| 路线优先的行程板 | ❌ 退化成"中国古建筑贴纸大杂烩" |
| 白边贴纸 / 9:16 | ✅ 仅这两项达标 |

**根因**：文生图模型**只会画"风格"，不会装"信息"**；中文渲染能力≈0，信息密度一高就崩。
换模型（即梦/可灵/Qwen-Image）只能让乱码好看一点，**文字依然会错**。

**正解**：**HTML/CSS 渲染 → 截图**。文字是真字体渲染，100% 准确。

#### 已跑通的实现（本机范式）

**① HTML 样式骨架**（实测有效）：
- 画布：`body { width:1080px; height:1920px; }`（精确 9:16）
- 米色网格纸：`background:#FAF6EC` +
  `repeating linear-gradient(rgba(140,160,180,.16) 1px, transparent 1px)` 两个方向，`background-size:36px 36px`
- 字体：`"楷体","KaiTi","STKaiti",serif`（标题可配 `"黑体"`）
- 路线脊柱：容器 `padding-left:74px` + `::before { border-left:4px dashed #9AA7B4 }`
- 编号节点：绝对定位圆点 `.dot.num`（赭红 `#B5544A`，白字）
- 卡片：白底 + `border-left:9px solid` 色条 + `box-shadow:3px 4px 0 rgba(0,0,0,.09)`
  - 配色：蓝 `#5C7FA3` / 红 `#B5544A` / 黄 `#D9A62E` / 绿 `#6E9E78`
- 重点卡（主剧）：整块赭红底 + 白字 + `transform:rotate(-.7deg)`
- 提醒气泡：`border-radius:999px` 胶囊，黄色/红色两档
- 照片槽位：白底 + `outline:3px dashed #B9C4CE` + 轻微旋转（奇偶交替）
- 胶带装饰：半透明米黄小条 + 旋转

**② 渲染截图**（Playwright 连本机 Edge CDP，**别用 `p.chromium.launch()`**）：
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9223")   # 用已开的 Edge
    page = b.contexts[0].new_page()
    page.set_viewport_size({"width": 1080, "height": 1920})
    page.goto("file:///" + html_path.replace("\\", "/"), wait_until="load")
    page.wait_for_timeout(2500)
    h = page.evaluate("document.body.scrollHeight")   # 校验是否 1920，超出说明内容要缩
    page.screenshot(path=out_png, clip={"x":0,"y":0,"width":1080,"height":min(h,1920)})
```
- ⚠️ **坑**：`p.chromium.launch()` 会报 `Executable doesn't exist ... chrome-headless-shell.exe`
  （Hermes venv 里 playwright 没下浏览器）。**直接用 Edge CDP 反而更省事**，不用下 100MB。
  **更好的办法（某日 实测）**：`p.chromium.launch(headless=True, channel="msedge")` ——
  **直接用本机 Edge 内核，完全不依赖 CDP 端口**，也就不怕用户关窗口导致 9223 掉线。
  写成三级回退最稳：`channel="msedge"` → `channel="chrome"` → 默认内核。
  ```python
  def launch(pw):
      for kwargs in ({"channel": "msedge"}, {"channel": "chrome"}, {}):
          try:
              return pw.chromium.launch(headless=True, args=["--force-device-scale-factor=1"], **kwargs)
          except Exception as e:
              print("launch %s 失败：%s" % (kwargs, str(e)[:80]))
      raise SystemExit("没有可用浏览器内核")
  ```
  参考实现：`$HOME\.hermes\tmp\henan\render_d1_d4.py`（单页/多页渲染 + 拷桌面 + 字节校验 + 溢出自检）
- ⚠️ Edge 的 CDP 端口会掉（用户关窗口就没了）→ 截图前先探活
  `Invoke-WebRequest http://127.0.0.1:9223/json/version`，掉线就重启 Edge。
- 交付：`MEDIA:<png绝对路径>`

**③ 已验证产物**（可作为下个会话的模板）：
- HTML 模板：`$HOME\.hermes\tmp\henan\scrapbook\d2.html`
- 渲染脚本：`$HOME\.hermes\tmp\henan\render_scrapbook.py`
- 成品：`...\scrapbook\page_D2_html.png`（1080×1920，415 KB）

**④ 文生图何时仍可用**：只做**配图/插画**（如景点头图、风格底图），
**绝不要让它承担"画文字和表格"的职责**。

### 2. 交付方式（本机无 `report_final_files` 等宿主工具）

- 出图后用 **`MEDIA:<绝对路径>`** 在对话里交付（Hermes 会内联显示 PNG/JPG）
- 产物落盘建议：`$HOME\.hermes\tmp\<topic>\scrapbook\page1.jpg`、`page2.jpg`…

### 3. 缺生图工具时的降级路径（SKILL.md 已定义，本机照此执行）

若 API 不可用 → 只输出 **【4. 每页生图提示词】** + **可替换图片槽位清单**（copy-ready），
让用户拿去任意生图工具（即梦/可灵/Midjourney）自行生成。本机实测生图可用，默认走"直接出图"。

### 4. 本机运行环境事实（省得下个会话重踩）

- Windows 11 + **PowerShell 5.1**：含中文的 `.ps1` 用 `write_file` 落盘会被按 GBK 读成乱码 → **改用 Python 脚本或把命令内联进 terminal**
- Python：`python`=3.11 / `python3`=3.14；已装 `playwright`、`websocket-client`、`PIL`、`requests`、`python-docx`、`openpyxl`
- 写中文文件一律 **UTF-8**；PowerShell 追加写用 `Set-Content -Encoding UTF8`
- `private/character-profile.local.yaml`（本技能的角色私有配置）→ 若用户要放**自家孩子/宠物的形象做贴纸**，把参考图放 `assets/character-references/`，再把特征写进 private 配置（该目录不随技能公开分发）

### 5. 与同族技能的分工（避免重复劳动）

| 技能 | 产出 | 用在哪 |
|---|---|---|
| `life/travel-guide` | **Word / Excel** 攻略与明细 | 出发前做功课、打印/存档 |
| **本技能** | **9:16 竖版手账图** | **旅途中手机翻着看** |
| `life/travel-planning-cn` / `life/trip-planning-cn` | 行程方法论、真实数据核验 | 排行程阶段 |
| `life/trip-advisor` | 高铁/酒店/景点数据查询 | 查数据阶段 |

**推荐组合**：先用 `travel-guide` 出 Word 底稿 → 再用本技能把它转成 9:16 手账图（手机端）。

