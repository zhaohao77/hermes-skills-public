# 数据源实操笔记（flyai / 飞猪 CLI）

> `trip-advisor` 与 `travel-guide` 是 curation 保护的手工技能，不能自动更新，
> 所以本文件承载这两个技能的**实操补充**。执行行程规划时一起读。

## 一、flyai CLI 参数活用

### 1. 查车次：**必须用车站名，不能用城市名** ⚠️ 最重要

一个城市常有普速站 + 高铁站两个站。用**城市名**查询时，飞猪返回的前 10 条会被
普速站的 Z/K 字头夜车占满，**高铁直达车被挤出结果**，导致误判"没有直达高铁"。

| 城市 | 高铁站（查这个） | 普速站（别用它查） |
|---|---|---|
| 长沙 | 目的地站 | 长沙 |
| 郑州 | 郑州东 | 郑州 |
| 洛阳 | 洛阳龙门 | 洛阳 |
| 开封 | 开封北 | 开封 |

**实踩案例**：查「洛阳→开封」只看到 Z378/K558 等普速夜车（2h+），
误判成"没有高铁直达"；改成「洛阳龙门→开封北」→ **7 趟直达高铁，仅 1h03m**。

### 2. 查换乘接续车次：**必须限定时间段**

不加限定时，10 条上限会把一天的车次摊薄，看着像"中午之后没车"。

```powershell
flyai search-train --origin '郑州东' --destination '洛阳龙门' `
    --dep-date '某日' --dep-hour-start 12 --dep-hour-end 16
```

### 3. 判断"某地有没有铁路"

查不到任何班次（连普速都没有）→ 该地**无铁路客运站**，只能走公路。
**实测**：登封（少林寺）—— 郑州去、洛阳去均无班次。

### 4. `--journey-type 1` 只筛"直达"，不筛"高铁"

普速直达车照样会返回，别拿它当"只看高铁"用。

### 5. 查景点：省 listRank，这是最有价值的字段

返回里的 **`listRank` 是榜单排名**，例如：
- "洛阳亲子景点榜第2名"（应天门）
- "洛阳亲子景点榜第3名"（洛阳古墓博物馆）
- "河南经典必去景点榜第1名"（万岁山武侠城）
- "河南博物馆景点榜第1名"（洛阳博物馆）

**带孩子的行程优先采信"亲子榜"排名**——这比看地图选点靠谱，是平台用真实游览数据算出来的。
`poiLevel`（1-5 级）和 `ticketInfo.price` 也可用（价格在体验模式下打码）。

### 6. 查酒店：两个筛选项

```powershell
flyai search-hotel --dest-name '洛阳' --poi-name '洛邑古城' `
    --check-in-date 某日 --check-out-date 某日 `
    --sort rate_desc --hotel-bed-types '双床房'
```

- `--poi-name <景点>`：按景点筛，返回 `interestsPoi` 显示"近XX景区"
- `--hotel-bed-types`：`大床房` / `双床房` / `多床房`
- `--hotel-types`：`酒店` / `民宿` / `客栈`
- `star` 字段是档次（经济型 / 舒适型 / 高档型）
- **价格在体验模式下打码**（`¥1xx`、`¥7xx`）

### 7. `ai-search` / `keyword-search` 能搜旅游产品，但看不到价格

能搜到"包车""一日游"类产品的标题，确认平台上有没有这类供给，
但体验模式下 `price` 一律 null，**实际报价必须另行询价**。

## 二、体验模式的硬约束（必须向用户交底）

飞猪 CLI 当前是**体验模式**：

| 数据类型 | 是否精确 |
|---|---|
| 机票价格 | ✅ 精确（¥260、¥300） |
| 火车票价 | ❌ 打码（`3xx`、`5xx`） |
| 酒店价格 | ❌ 打码（`¥1xx`、`¥7xx`） |
| 景点门票 | ❌ 打码或为空 |
| 车次时刻 / 站名 / 时长 | ✅ 精确 |
| 酒店名 / 地址 / 坐标 / 档次 | ✅ 精确 |
| 景点名 / 榜单 / 简介 / 坐标 | ✅ 精确 |

**交付铁律**：不得把打码价格当真实报价输出。要精确价格需用户去
飞猪 AI 开放平台申请 API Key —— 这是用户的决定，不要代为注册。

## 三、PowerShell 调用坑

```powershell
# ❌ 会被 Hermes 判定为后台任务而拦截
$args = @('search-hotel','--dest-name','洛阳')
& flyai @args

# ✅ 拼接字符串 + Invoke-Expression
$cmd = "flyai search-hotel --dest-name '洛阳' --check-in-date 某日 --check-out-date 某日 --sort rate_desc"
$raw = Invoke-Expression $cmd 2>$null | Out-String
$j = $raw | ConvertFrom-Json
$j.data.itemList | Select-Object -First 8 | ForEach-Object { ... }
```

**返回结构速查**：
- 车次：`data.itemList[].journeys[0].segments[0]` 里有 `marketingTransportNo`（车次）、
  `depStationShortName` / `arrStationName`、`depDateTime` / `arrDateTime`、`duration`（分钟）、
  `seatClassName`、`journeyType`（直达/中转）；价格在 `itemList[].price`
- 酒店：`data.itemList[].{name,address,star,interestsPoi,price,latitude,longitude}`
- 景点：`data.itemList[].{name,poiLevel,listRank,ticketInfo.price,category,description,latitude,longitude}`

## 四、与 `travel-guide`（文档生成）配合

`travel-guide` 的脚本已补齐并验证可用：

```powershell
# itin.json -> Word（含手绘地图，地图先放到 <工作目录>/.temp/map_<拼音>.jpg）
python <travel-guide>/scripts/gen_docx.py --title "..." --subtitle "..." `
    --output "xx攻略.docx" --itin-file itin.json

# itin_table.json -> Excel（13 列）
python <travel-guide>/scripts/gen_xlsx.py --sheet-name "行程安排" `
    --output "xx行程.xlsx" --itin-file itin_table.json
```

**注意**：
- 它内部引用的 `ImageGen` 和 `report_final_files` 在 Hermes 上不存在
  （已在本机副本里做了替换说明）；配图缺失时脚本会打印清单，**不阻塞出件**
- 手绘地图转成 `.temp/map_<目的地拼音>.jpg` 放好，gen_docx.py 会自动插到
  "出行概览"之后（实测 docx 从 46.7KB → 426.9KB 即嵌入成功）
- 交付前用 `read_file` 读一次 docx/xlsx 确认内容真写进去了
