# Hermes Skills Collection

> 一个精选的 [Hermes Agent](https://hermes-agent.nousresearch.com/docs) 技能合集 —— 文档处理、网页采集、桌面自动化、工程方法与写作表达。

共 **21 个技能**，全部经过实测可用、逐条脱敏，不含任何个人数据。

## 这是什么

Hermes 的「技能」就是一个带 `SKILL.md` 的文件夹。Agent 启动时只读 frontmatter 里的 `name` 和 `description`，
判断当前任务相关时才加载正文和 `references/`、`scripts/` 里的深料。所以技能库可以很大，代价只有一行描述。

## 安装

```bash
# 克隆到 Hermes 技能目录
git clone <this-repo> /tmp/skills-public
cp -r /tmp/skills-public/* <hermes-home>/skills/
```

`<hermes-home>` 通常是 `~/.hermes` 或 `%APPDATA%/cn.org.hermesagent.desktop/runtime/hermes-home`。
拷完重启 Hermes 即可，无需注册。

## 技能清单

### 文档处理

| 技能 | 用途 | 来源 | 文件 |
|---|---|---|---|
| [`docx-formatter`](docx-formatter/SKILL.md) | Use when 生成公文、报告、总结、方案等正式 Word 文档，需符合中国公文格式规范（含述职报告、民主生活会等党政材料），或需要批量套用公文字体字号与版式。 | 本仓库 / MIT | 6 |
| [`pdf`](pdf/SKILL.md) | PDF files: create, read, merge, fill, OCR, edit text. | Nous Research / MIT | 23 |
| [`xlsx`](xlsx/SKILL.md) | Create, read, edit Excel .xlsx workbooks and CSVs. | Nous Research / MIT | 11 |

### 网页与采集

| 技能 | 用途 | 来源 | 文件 |
|---|---|---|---|
| [`blocked-page-recovery`](blocked-page-recovery/SKILL.md) | Use when a fetch fails: 403/429, paywall, WAF, bot wall. | Hermes Age / MIT | 2 |
| [`browser-skill`](browser-skill/SKILL.md) | Automate the user's logged-in Chromium browser: read pages, fill forms, scrape data, ope… | 本仓库 / MIT | 12 |
| [`scrapling-skill`](scrapling-skill/SKILL.md) | Scrape web pages using Scrapling with anti-bot bypass (like Cloudflare Turnstile), steal… | Karim Shoair / BSD-3-Clause | 27 |
| [`web-tools-guide`](web-tools-guide/SKILL.md) | MANDATORY before calling web_search, web_fetch, browser, or opencli. Contains required e… | 本仓库 / MIT | 6 |

### 桌面与系统

| 技能 | 用途 | 来源 | 文件 |
|---|---|---|---|
| [`computer-use`](computer-use/SKILL.md) | Drive the user's desktop in the background — clicking, typing, scrolling, dragging — wit… | 本仓库 / MIT | 1 |
| [`image-edit-local`](image-edit-local/SKILL.md) | 本地改图（离线、零 API、零成本）。 | 本仓库 / MIT | 2 |
| [`long-image-slicer`](long-image-slicer/SKILL.md) | 长图自动切割+并行OCR工具。 | 本仓库 / MIT | 3 |
| [`storage-analyzer`](storage-analyzer/SKILL.md) | macOS / Windows 只读存储分析助手（自动识别系统）。 | 本仓库 / MIT | 7 |

### 工程方法

| 技能 | 用途 | 来源 | 文件 |
|---|---|---|---|
| [`domain-modeling`](domain-modeling/SKILL.md) | Build and sharpen a project's domain model. Use when discussing codebase terminology, wr… | 本仓库 / MIT | 4 |
| [`grill-me`](grill-me/SKILL.md) | 苏格拉底式追问——在执行任何计划前，彻底追问你的思维漏洞，直到达成共识再动手。 | 本仓库 / MIT | 2 |
| [`grill-with-docs`](grill-with-docs/SKILL.md) | A relentless interview to sharpen a plan or design, which also creates docs (ADR's and g… | 本仓库 / MIT | 2 |
| [`to-spec`](to-spec/SKILL.md) | Turn the current conversation into a spec and publish it to the project issue tracker: n… | 本仓库 / MIT | 2 |
| [`writing-skills`](writing-skills/SKILL.md) | Use when 新建或修改技能，或验证技能真能约束 agent。 | 本仓库 / MIT | 10 |

### 写作与表达

| 技能 | 用途 | 来源 | 文件 |
|---|---|---|---|
| [`help-me-understand`](help-me-understand/SKILL.md) | 【日常默认生效】所有回答都按"说人话"标准输出：一词一义、一句话一件事、先给结论再给依据、保留不确定性与条件范围、不说死不说满。 | 本仓库 / MIT | 8 |
| [`humanizer-zh`](humanizer-zh/SKILL.md) | 通用中文文本润色与 AI 痕迹去除工具。 | 歸藏 / MIT | 4 |
| [`learning-material-pipeline`](learning-material-pipeline/SKILL.md) | 把书/长文变成可教材料时用：取原文、验引文、沉淀卡片。 | 本仓库 / MIT | 3 |

### 分析方法

| 技能 | 用途 | 来源 | 文件 |
|---|---|---|---|
| [`al-brooks-price-action`](al-brooks-price-action/SKILL.md) | Analyze charts, OHLC bars, candlestick sequences, and trading context using Al Brooks st… | 本仓库 / MIT | 7 |

### 业务调研

| 技能 | 用途 | 来源 | 文件 |
|---|---|---|---|
| [`region-economy-research`](region-economy-research/SKILL.md) | Use when 要调研某区县/镇街/园区经济、做产业地图、出重点企业名单（含纳税或营收前N）、专精特新名单、普惠或对公业务拓展的区域摸底。 | 本仓库 / MIT | 7 |

## 目录约定

```
<skill-name>/
├── SKILL.md          # 入口：frontmatter(name/description) + 正文
├── references/       # 深料：查表、备忘、踩坑库
├── scripts/          # 可执行脚本
└── templates/        # 模板文件
```

SKILL.md 的 `description` 决定触发。第一句要能独立说清「什么时候用」，
否则 agent 不会加载 —— 这是写技能最容易踩的坑。

## 许可

本仓库为**混合许可**，以各技能目录内的许可证为准：

| 技能 | 版权方 | 许可 | 说明 |
|---|---|---|---|
| `blocked-page-recovery` | Hermes Age | MIT | 抓取失败时的恢复策略 |
| `humanizer-zh` | 歸藏 | MIT | 译自 blader/humanizer，参考 hardikpandya/stop-slop |
| `pdf` | Nous Research | MIT | Hermes Agent 内置技能 |
| `scrapling-skill` | Karim Shoair | BSD-3-Clause | 智能网页采集，基于 Scrapling 框架 |
| `xlsx` | Nous Research | MIT | Hermes Agent 内置技能 |

未在上述列表中的技能，由本仓库维护者以 **MIT** 许可证提供，见 [LICENSE](LICENSE)。

## 致谢

- [Hermes Agent](https://github.com/NousResearch) —— 技能系统与内置技能
- [Scrapling](https://github.com/D4Vinci/Scrapling) —— 反检测抓取框架
- [歸藏](https://github.com/op7418) —— 中文写作去 AI 味方法论
- Al Brooks —— 价格行为分析体系
