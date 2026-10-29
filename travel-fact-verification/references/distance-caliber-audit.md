# 里程 / 车程口径：高德 REST 实测 + 「哪个数对」的裁决

**触发**：交付物里出现距离/车程（打车、步行、换乘前的那段），或**两个载体写了不一样的数字**、
用户问「**查证一下哪个正确**」。

---

## 一、为什么必须实测：同一段路会同时存在三个版本

某日 河南线实例（同一批交付物里）：

| 路段 | Word 写的 | 手账图写的 | **高德 REST 实测** | 判定 |
|:--|:--|:--|:--|:--|
| 中牟酒店 → 开封酒店 | 38.6 km / 约 80 元 | 43.0 km / 49 分 | **41.3 km / 45 分** | 两者都不准；**旧车费少报 40%** |
| 开封酒店 → 万岁山 | 1.8–2.2 km / 6–8 分 | 3.4 km / 16 分 | **2.6 km / 8 分** | 一个偏小一个偏大 |
| 开封酒店 → 宋城路站 | 8.0 km / 23 分 | 8.0 km / 23 分 | **8.9 km / 23 分** | 耗时对、距离略短 |
| 花园路亚朵 → 河南博物院 | 680 m（**直线**） | 1.2 km / 16 分 | **步行 1.1 km / 14 分** | 直线值不能当步行动线 |
| 郑州东站 → 花园路亚朵 | 12.0 / 11.6 km 两个数 | 同 | **11.9 km / 27 分** | 两个数都不对，且**同一段在两张卡上是两个值** |
| 花园路亚朵 → 二七广场 | 5.0 km / 16 分 | 同上 | **4.7 km / 19 分** | 耗时少报 3 分 ⇒ 出门时刻跟着错 |

**三条结论**：
1. **同一批交付物里，Word 那套数字往往最旧**（Word 是上一版行程的遗留，手账图是当轮在改的）——
   冲突时**先怀疑 Word**，但仍要实测确认，别反过来拍。
2. **直线距离 ≠ 道路里程 ≠ 步行动线**，三者可以差 50%（680 m 直线 → 1.1 km 步行）。
   交付物里凡是"几分钟"，只认**路线规划接口**的值。
3. **改了距离就要扫掉基于它的比较级结论**（本轮旧文写"到清园比到万岁山更近"，实测两边都是 2.6 km ⇒ 作废）。

---

## 二、配方：直接调高德 Web 服务 REST（比 node 脚本更省事）

key 三处都有（环境变量 `AMAP_WEBSERVICE_KEY` / `AMAP_KEY` / 技能目录 `config.json` 的 `webServiceKey`）。

```python
import json, os, time, urllib.parse, urllib.request
from pathlib import Path
KEY = os.environ.get("AMAP_WEBSERVICE_KEY") or json.loads(Path(
    r"<hermes-home>\skills\life\amap-lbs-skill\config.json").read_text(encoding="utf-8"))["webServiceKey"]

def api(path, **params):
    params.update(key=KEY, appname="amap-lbs-skill")      # appname 必带，别省
    for i in range(4):
        try:
            r = json.loads(urllib.request.urlopen(
                "https://restapi.amap.com" + path + "?" + urllib.parse.urlencode(params), timeout=30
            ).read().decode("utf-8"))
            if r.get("status") == "1":
                return r
            print("retry", i, r.get("info"))
        except Exception as e:
            print("err", e)
        time.sleep(1.5)                                    # 限流保护
    return {"status": "0"}

# ① 地址 → 坐标（location 是 "经度,纬度"，经度在前）
api("/v3/geocode/geo", address="经五路21-5号", city="郑州")["geocodes"][0]["location"]
# ② 真实车程 / 步行（返回 distance 米 + duration 秒）
api("/v3/direction/driving", origin=f"{lon},{lat}", destination=...)   # 或 walking / riding / transfer
```

**两个必踩的坑**：
- ⚠️ **QPS 限流**：连续请求会返回 `status!=1` 且 `info=CUQPS_HAS_EXCEEDED_THE_LIMIT` ——
  这不是"地址错了"。**每次调用之间 `sleep(1.2–1.5)` + 重试 3–4 次**即可（本轮 8 个地址 + 7 条路径顺利跑完）。
- ⚠️ **有的地名 geocode 直接报 `ENGINE_RESPONSE_DATA_ERROR`**（本轮「郑州东站」「二七纪念塔」都报）。
  **换一个更"POI 化"的串**就好：`郑州东站西广场` ✓、`二七广场`/`德化步行街` ✓。
  再做不通就退回 `poi-search.js` 用关键词拿坐标（**店名里带景点名的连锁酒店必须走 POI 搜索**，见 SKILL.md）。

---

## 三、裁决与落地纪律

1. **先跑表再动任何文件**：把「车上/纸上的旧值」与「接口实测值」并排列出来给用户看，**一次给完**，
   不要边改边报（用户要的是"哪个正确"这个结论）。
2. **六个数字全载体统一**：改完必须回到**每个载体**核一遍（手账图 HTML × 2 套（scrapbook + a4 变体）+ Word + xlsx），
   本轮共 8 个 HTML 文件 + 1 docx + 2 xlsx。
   → 「同段多处替换不要 break」的坑见 `travel-deliverable-design/references/word-docx-surgical-edit.md` §八。
3. **改完重渲 + 重新拼装下游**：手账图 5 页重渲 → 桌面 PNG；A4 页 6 页重渲 → 重建 PDF；
   路线图若图上写了里程/日程也要重出（并原位替换 Word 内嵌 `word/media/image1.jpg`）。
4. **多源价差写区间，不写单值**：同类的"票价"问题（汴河游船夜游，问道给 50/25、本地宝 40、
   旅泊网 30、马蜂窝 60）→ 交付物写 **「夜游单程约 40–60 元/人 · 码头随买随用」**，
   不挑一个顺眼的当结论（同 `travel-fact-verification` 铁律二.6）。
5. **数字统一后回写到本技能与距离表**：河南线的定稿值已并入
   `travel-deliverable-design/references/henan-2026-food-and-distances.md` §二，**下次直接取用，别再重测**。
