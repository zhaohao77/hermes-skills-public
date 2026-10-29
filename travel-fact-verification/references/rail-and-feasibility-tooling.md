# 车次 / 时间账核验工具链

配套 SKILL.md 铁律七「出货前四查」的**查1（时间账）与查4（票源）**。

> **⚠️ 别在本文件重造已装配件 —— 通用件在 `skill-install-ops`：**
> - 通用 MCP 探测脚本（HTTP/stdio 双模，任何 MCP server 可复用）→ `skill-install-ops/scripts/mcp_probe.py`
> - MCP 类依赖的安装与验证（`uv tool install` 修法 · `&` 被拒 · `0.0.0.0:8000` 暴露面 ·
>   **反例验收**方法论 · `AMAP_API_KEY` env 优先）→ `skill-install-ops` **#18**
> - 开源旅行 skill 横评结论与打分 → `skill-install-ops/references/travel-skill-landscape-2026-09.md`
>
> 本文件只留**这里独有**的三块：12306 口径与实测价目 · **可行性检查引擎的输入 schema** · 批量查询纪律。

---

## 1. 12306 口径与实测价目

装法与安全注意见 `skill-install-ops` #18。**这里只记会误判的口径**：

| # | 口径 | 不照做会怎样 |
|:--|:--|:--|
| 1 | **预售窗口 = 14 天**（原话「出发日期不能晚于 `<今天+14>`，仅支持提前14天购票」） | 超窗**不是「无票」，是「还没开售」** —— 报「未开售」 |
| 2 | **`无` 不能直接当「售完」** —— 必须做**对照实验**：同车次查一个平日日期 | 平日有票 + 目标日全无 ⇒ 真售完；两边都无 ⇒ 先怀疑口径。（实测 G952：9/23 有票、10/1 全无 ⇒ 国庆真售完。**同一会话、同一接口、只换日期**，结论才站得住） |
| 3 | `query-tickets` **不返回票价**，票价必须单独调 `query-ticket-price` 并传 `train_no` | 报不出价，或误用相邻车次的价 |
| 4 | 余票字段**混装整数与 `有`/`无`** → **禁止 `int()`** | `ValueError`。走 `travel_planner.py normalize-rail`，产出 `status`(AVAILABLE/LIMITED/SOLD_OUT) + `count` + `at_least` + `bookable_classes` 才可比 |

**某日 实测二等座价目**（写费用栏时用得上，但**须当期重查**）：

| 区间 | 二等座 |
|:--|:--|
| 目的地站→郑州东 | **472** |
| 郑州东→洛阳龙门 | **79** |
| 洛阳龙门→开封北 | **107** |

> 2 成人 2 儿童（6–14 岁半价 ⇒ 折 **3.0 个成人当量**）：目的地站→郑州东 = `472 × 3.0 =` **1,416 元**。
> 行程里若写「约 300–400 元/人」，按 4 人估就会错 —— **单价必须实查，别写「约」**（铁律七查2）。

**启动注意**：`mcp-12306` 启动要加载 3384 个车站数据，**慢**。起服务后先 `Start-Sleep -Seconds 6`
再打，或等日志出现 `Application startup complete`。健康检查 `GET http://127.0.0.1:8000/health`。

### 1a. ⭐ 一次性查车次：**直连服务函数**，别起 HTTP 服务（某日 实测）

`mcp-12306` 是**服务**不是 CLI —— 直接敲它会绑 `0.0.0.0:8000` 并**阻塞不返回**
（实测：连 `mcp-12306 --help` 都照样启动服务，60 秒后命令超时。**这不是故障、不是装坏了**，是设计）。
一次查一趟车**不需要**起服务，直接调它的 async 服务函数：

```python
import asyncio, json, sys
sys.path.insert(0, r"$HOME\AppData\Roaming\uv\tools\mcp-server-12306\Lib\site-packages")
from mcp_12306.services.ticket_service import (
    get_train_route_stations_validated, query_tickets_validated, station_service)

async def main():
    await station_service.load_stations()            # ⚠️ 必须！否则见下表
    print(len(station_service.stations))             # 应为 3384
    r = await get_train_route_stations_validated({   # 停站表：逐站 到/发/停时
        "train_no": "G503", "from_station": "北京西",
        "to_station": "株洲西", "train_date": "某日"})
    print(r[0]["text"])
asyncio.run(main())
```

跑法：**用工具自带 venv 的 python**（依赖只装在那里）
`~/AppData/Roaming/uv/tools/mcp-server-12306/Scripts/python.exe`；
输出会带一行「环境配置文件 …\.env 不存在」——**无害，忽略**。

**两个会伪装成「数据不对」的假故障**：

| 现象 | 真因 | 修 |
|:--|:--|:--|
| `{"success": false, "error": "出发站无效或无法识别：北京西"}` | **没先 `load_stations()`** —— `get_station_code` 遍历的是空列表，跟站名对错无关 | 调用前 `await station_service.load_stations()`（约 0.1 s） |
| 手搓 curl 打 12306 网页接口：`leftTicket/query*` 回空 `result`、`queryTrainInfo` 回 `data:{"data":null}` | 缺 `leftTicket/init` 的会话 cookie，且现在走 `queryI → 302 → queryG` | **别手搓 curl，走上面这套服务函数**（它内部会先 `init` 再跳转） |

⚠️ **`query_tickets_validated` 的 `train_code` 过滤参数不生效**（实测：传 `train_code="G503"` 仍回
**101 趟**全表）→ 拿回全表后**自己在 Python 里筛**，别以为「它只回了一趟」。
**要单一车次的到发时刻，用 `get_train_route_stations_validated`**（也顺带解决 SKILL.md 口径 5 的
「同城多站被合并成城市名」问题 —— 停站表按站名逐站给，能直接读「我上车的这一站几点开」）。

**实测样板（某日 G503 · 官网口径）**：北京西 14:45 始发 → 郑州东 17:58 到 / **18:02 开**（停 4 分）
→ **目的地站 21:52 到**（停 19 分）→ 株洲西 22:27；**郑州东 → 目的地站 = 3h50m**，共 14 站。
→ 有停站表就能顺手看出**大站停站只有 4 分钟**（郑州东）这种「别卡点到站」的事实用。

**⭐ 免 venv 的轻量核验（一条 curl，某日 实测可用）**——只要「这趟车这天存不存在 + train_no + 首末站」时，
不用起脚本，官方搜索接口就够（**不需要 cookie、不需要装任何东西**）：

```bash
curl -s "https://search.12306.cn/search/v1/train/search?keyword=G503&date=20261006" \
  -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.12306.cn/index/"
# -> data[]: station_train_code / from_station / to_station / total_num / train_no
#    实测：{"date":"20261006","from_station":"北京西","station_train_code":"G503",
#          "to_station":"株洲西","total_num":"14","train_no":"240000G5030J"}
```

用途：① 先确认车次与日期存在（免得把「车次没排班」误报成「查不到」）② 拿到 `train_no` 再进服务函数。
⚠️ 但**它只给车次级信息**（哪个区间、几站）—— **到、发时刻与逐站停站表仍必须走 `get_train_route_stations_validated`**；
且它**不验证「你从哪站上车」**（同城多站问题照旧，见 SKILL.md 口径 5）。
⚠️ 别把「手搓 curl 不行」推广开：**网页版 `kyfw.12306.cn` 需要会话 cookie（不行），这个搜索接口不用（行）** ——
上一节表里的结论只适用于 `leftTicket` / `queryTrainInfo` 那两个端点。

---

## 2. 可行性检查引擎：`tanweiping1012-source/travel-planner`

MIT，7⭐，Python 3.9–3.14。实测在 **Windows + Python 3.11 上 12 个子命令全通**
（81KB 测试、`feasibility.py` 19KB、`geomatch.py` 防高德把境外地名误返回国内同名地点）—— 不是提示词壳子。

```powershell
git clone --depth 1 https://github.com/tanweiping1012-source/travel-planner.git $HOME\hermes-lab\travel-planner
python scripts/travel_planner.py evaluate --input itin.json --output out.json
```

凭据：`AMAP_API_KEY` **环境变量优先**，macOS Keychain 只是 fallback
（缺失只抛 `macOS Keychain command is unavailable`）→ **Windows 完全可用**，唯一门槛是
申请一个免费高德 Web API Key。**别因为看到 `.sh` 就判定不兼容。**

### 输入 schema

```jsonc
{
  "budget_cny": 12000,
  "timezone": "Asia/Shanghai",
  "constraints": {
    "max_daily_minutes": 780,               // 超了 → 日时长告警
    "max_walking_km_per_day": 8,            // 带孩子必设；超了 → WALKING_LIMIT_EXCEEDED
    "default_transfer_buffer_minutes": 20,  // 候车余量。用户自己的标准是「到站留 1 小时」，按需调
    "stale_after_hours": 24
  },
  "activities": [
    { "id": "d3-g2226", "name": "G2226 洛阳龙门→开封北", "type": "TRANSIT",
      "start": "某日T08:34:00+08:00", "end": "某日T09:50:00+08:00",
      "opening_time": "08:00", "closing_time": "19:30", "last_entry_time": "20:00",
      "estimated_cost": 107, "walking_km": 0.3 }
  ],
  "segments": [
    { "from_id": "d3-hotel-out", "to_id": "d3-g2226",
      "duration_minutes": 30, "buffer_minutes": 20, "estimated_cost": 30 }
  ]
}
```

判据：`available = 下一段.start − 上一段.end` 是否 ≥ `duration_minutes + buffer_minutes`。

### 输出与实测抓到的 code

`status`(FEASIBLE/INFEASIBLE) · `score` · `hard_conflicts[]` · `warnings[]` · `suggestions[]`

| code | 含义 |
|:--|:--|
| `INSUFFICIENT_TRANSFER_TIME` | 换乘不足，**还算出少几分钟**（details 给 available_minutes / travel_minutes / buffer_minutes） |
| `AFTER_CLOSING` | 结束时间晚于闭馆 |
| `WALKING_LIMIT_EXCEEDED` | 当日步行超上限（WARNING） |
| `INVALID_ACTIVITY_RANGE` | `end` 不晚于 `start` —— **多数是自己建模的锅**（零时长活动），不是行程的错 |
| `MISSING_TRANSIT_SEGMENT` | 两个活动间没给通勤段（WARNING） |

### 建模 pitfalls

- **零时长活动**（如「酒店退房 07:40–07:40」）会触发 `INVALID_ACTIVITY_RANGE`，是**假警报**。给 1 分钟。
- **同站换乘**（同一车站内换另一趟车）会让 schema 退化，别硬套；
  按 `duration_minutes = 站内走行 15` 建模才有意义。
- **报结果时必须把「机器判定」与「自己建模的假设」分开说** —— `INVALID_ACTIVITY_RANGE` 这类
  是自己喂错数据，别当成行程的问题报给用户。
- 只读边界：不下单、不填验证码、不导出 cookie；技能明写「绝不编造路线/时刻/价格/营业时间」——
  与本技能铁律同源，**引用时要保留「数字都带来源 + 查询时间戳」这一点**。

---

## 3. 批量查询纪律（用户实况：长循环会被打断）

查多条腿时，**一轮把所有腿跑完并落盘**，不要来回多轮试探：

- 一个脚本跑完全部腿，中间产物写 JSON（如 `audit_rail.json`），后续复算**复用落盘数据，不重跑**。
- 12306 建议限速「每秒最多一个新请求」→ 脚本内 `Start-Sleep -Seconds 1.1`，
  **但把 sleep 藏进单次运行里**，不要为了「稳」拆成多次工具调用。
- 用户反感冗余重复执行；实测一次带 1.1s 间隔的 4 腿循环就被手动打断过。
- **最大的浪费不是慢，是查错了对象**（见 SKILL.md 铁律零）：本轮验了 5 个车次，**没有一个是他要坐的**。
  → 开跑之前，先用 `D<n>手账图.png` 锁定当日真实车次与城市映射，再动手查。
