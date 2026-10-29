# 00 · 换区县迁移清单（目标：30 分钟出全套）

> 用这份清单把本技能搬到新区县。**不改 SKILL.md 的方法层，只换实例层与 config。**
> 顺序不能乱：先拿 config 里的「标识」跑通抓取，再谈内容。

## 第 0 步 · 抄「三个模板」（20 分钟，卡住就停）

> 换区县真正的门槛不是「知道几个栏目」，而是**抄对三个模板**。抄错任何一个，后面每镇都抓回 0 篇，而且脚本不报错。

| 要找什么 | 在哪找 | 填到哪个字段 |
|---|---|---|
| 政府网站根域名 | 搜「XX县人民政府」官网 | `base_url` |
| **镇街列表页路径模板（到 `{code}` 截断）** | 手工点开任一个镇的页面，抄 URL 到代码之前那段 | **`town_url_tpl`** |
| **镇街页里怎么发现子栏目** | 看镇街页 HTML：<br>· meta refresh `url=./xxgkzn1/` → 用默认 `url=\.?/?([a-z]+\d+)/`<br>· 纯字母栏目码（`xxgkzn`）→ 改成 `url=\.?/?([a-z]+)/`，或去掉 `\d+` | **`chan_regex`** |
| 每个镇街的栏目码 | 打开每个镇页面，URL 里的目录段 | `towns`（`{"镇名": "code"}`；有多栏目用 `{"镇名":{"code":"xx","channels":["gzdt1","tzgg"]}}`） |
| 县级新闻父路径 + 各子栏目 | 政务公开 → 新闻动态 | `county_prefix` + `county_channels` |
| 镇街标准全称清单 | 官网「行政区划」页 | `towns` 的键 + `town_order` |
| 本地支柱行业 | 本地产业常识 | `exclude_words` 要单独看，别把本地主力一刀剔掉 |

🔴 **CHECKPOINT**：`town_url_tpl` 与 `chan_regex` 没实测过就别跑全量。验证方法——用新 config 只跑一个镇：
```bash
python research_pipeline.py crawl --config ../configs/<新区>.json --towns <一个镇> --out D:/tmp/probe
```
`[crawl] 镇街完成：N 篇索引` 里 N > 0 才算通过。N = 0 就是模板不对，回去改模板，**不要在栏目码上来回猜**。

**镇街可能含「乡」**：有的区县是「街道 + 镇 + 乡」三套（例：30+ 个乡镇街道含某乡）。照标准全称写进 `towns`，别只写镇和街道。镇街多（>20 个）时，第 0 步不止 20 分钟，按实际数量估。

## 第 1 步 · 交付验收口径先写下来（3 分钟）

在 config 里写死三样，后面全部围绕它判定：
- `min_year`：数据年份下限（默认 当年-2）
- `exclude_words`：本地要额外剔除的行业词（有的县畜牧/烟花/陶瓷是主力，不能一刀切）
- `foreign_prefixes`：外地地名前缀表（防止把外地企业收进来）

## 第 2 步 · 试跑两个镇（5 分钟）

```bash
python research_pipeline.py all --config ../configs/<新区>.json \
  --towns <镇A>,<镇B> --out D:/tmp/<新区>_smoke
```

**验收（四条全过才算通）**：
1. 三件交付物都生成（xlsx / docx / audit_report.md）
2. `audit_report.md` 的「口径违规」= 0
3. 候选数在 5-20 家（两个中等镇的合理量级）
4. 抽 3 家企业，点开 URL 能看到这个名字

没过就看 `audit_report.md` 的失败项，别急着全量。

## 第 3 步 · 全量抓取（10 分钟，含县级）

```bash
cp $OUT/corpus.json $OUT/corpus.json.bak.$(date +%m%d-%H%M)   # ← 先备份，覆盖不可逆
python research_pipeline.py crawl --config ../configs/<新区>.json            # 镇街
python research_pipeline.py crawl --config ../configs/<新区>.json --county-only  # 县级（宏观/竞争语料）
python research_pipeline.py extract --config ../configs/<新区>.json
python research_pipeline.py build   --config ../configs/<新区>.json
python research_pipeline.py audit   --config ../configs/<新区>.json
```

**验收**：`[crawl] 镇街完成` 那行的篇数 ≥ config 里的 `min_corpus`（默认 300，按本地发文量调）；低于阈值脚本会打 ⚠️ 告警，先查模板再谈内容。8 章报告里宏观/竞争两章各 ≥3 条带出处的原文句。

## 第 4 步 · 人工过一遍（15 分钟，不能省）

脚本给的是**候选池**，不是终稿。逐条看三样：
1. **关键数据是不是这家公司的**（同段提两家时可能错配）
2. **名称是不是全称**（页面写简称的标出来，别自己补行政区划前缀）
3. **行业对不对**（`待分类` 的要人工归位）

过完把确认版存成 `<新区>_picks.json`（**结构必须同 `keep.json`，6 个键一个都不能少：镇街 / 企业 / 行业 / 关键数据 / 认定 / 来源**；`镇街` 漏了脚本直接 KeyError。完整字段清单见 `configs/_SCHEMA.md` 末节），重跑 build 时用 `--picks` 传入。

## 第 5 步 · 建实例目录（3 分钟）

```
references/instances/<新区>-<年份>/
├── INDEX.md            # 10 行：这个区县覆盖了什么、数据截止日、已知缺口
├── 00-宏观与产业.md     # 第 1-2 层产出
├── 01-镇街地图.md       # 第 3 层产出（可按片区拆多个文件）
└── 02-重点企业清单.md   # 第 4 层产出（含更正与待核附录）
```

**规则**：实例层只放**数据与这次怎么做的**，方法一律回 `00-METHOD.md`，不要复制。

## 第 6 步 · 更新 SKILL.md 的索引（3 分钟）

在「九、支持文件」里加一行指向新实例目录，并在 INDEX.md 里写清「覆盖 X 个镇街 / 数据截止 YYYY-MM / 缺口在哪」。

## 常见卡点（按出现频率排）

| 症状 | 原因 | 处理 |
|---|---|---|
| 抓回 0 篇 | 栏目代码猜错 / 网站改版 | 手工点开一次列表页，从 URL 里抄代码；改版就要改 `ART` 正则 |
| **抓回 0 篇（每镇都是）** | **`town_url_tpl` 抄错**——这是换区县第一坑，照抄参考实例的路径必 404 | 点开一个镇页面，抄 URL 到代码前那段重填模板，再单跑一个镇验证 |
| **栏目发现为空** | `chan_regex` 不匹配：该县栏目码是纯字母（如 `xxgkzn`），默认正则要求带数字 | 把 `chan_regex` 改成 `url=\.?/?([a-z]+)/`（**注意 `\.?/?` 要保留**——meta 常写成 `url=./xxgkzn/`），或在 `towns` 里直接写死 `channels` 列表 |
| **https 打不开（SSL 握手失败）** | 有的区县政府网只支持 http，或本地 OpenSSL 握手被拒 | `base_url` 改 `http://`；实测某县级市 https 报 `SSLV3_ALERT_HANDSHAKE_FAILURE`、http 正常 |
| **有索引但正文 0 篇** | 正文容器正则只取「第一个匹配」，命中了标题/元信息那种小块 | 已内置「取最长匹配」，一般不会再犯；仍不行就配 `body_regex`（如 `<div[^>]*class="[^"]*article-body[^"]*"[^>]*>(.*?)</div>`） |
| **正文只有几十字** | 同上，抓到的是 article-meta 而不是 article-body | 配 `body_regex` 或先人工打开一篇确认正文容器 class |
| **整站不是这套 CMS** | 有的区县用统一平台（如省政务云），路径与文章 URL 规律全不同 | 放弃脚本抓取，改走 `site:` 党报检索 + 人工录入；报告里写明数据来源与局限 |
| **该镇没有「工作动态」栏目** | 只有概况/机构设置页 | 该镇标“公开信息不足”，用党报专题补；不要用邻镇数据凑 |
| **语料上千篇但候选 0 家** | `exclude_words` 把本地支柱行业剔光了（花炮/危化/陶瓷这类） | 逐条看剔除表，把本地主力行业从剔除词里拿出来，重跑 extract（不用重抓） |
| **只有招标公告，没有企业新闻** | 该镇不披露经营信息 | 换党报专题检索；仍无就写「该镇公开信息不足」，不凑数 |
| **候选全是村集体/合作社** | `exclude_words` 没带全 | 补词后重跑 extract（不用重抓） |
| **宏观章全是「未检到」** | 没跑 `--county-only` | 补抓县级频道再 build |
| **报告章数不足 8** | 只跑了 build 没跑过县级 | 同上；或语料确实空，报告里写明原因 |
| **报错 `KeyError: '镇街'`** | `--picks` 里的对象缺 `镇街` 键 | 照 `keep.json` 补齐 6 个键（见 `configs/_SCHEMA.md` 末节） |
| **`!! 缺 openpyxl`** | 环境没装库 | `pip install openpyxl python-docx`；不装就只能出 md，验收第 1 条过不了 |
| **名单 200+ 家跑不完** | 没做行业闸/价值闸排序 | 用认定字段优先排，取前 60-80 家进路线图 |
