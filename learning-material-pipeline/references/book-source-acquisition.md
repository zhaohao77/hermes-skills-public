# 书 / 长文的原文获取链路（实测）

> 实战经验：把整本书的 PDF 放进网盘目录，直接从云盘取原文，比在阅读器里翻更快更干净。
> 结论：**网盘 PDF 文字版是最快最干净的来源**；微信读书网页版只能当降级通道。

## 一、百度网盘：先搜，别递归扫

`xpan` 有搜索接口，直接按文件名捞，比递归列目录快一个量级：

```python
# bdpan_api.api(method, params, token) 已封装好 token 与 UA
api("search", dict(key="关键跃升", dir="/", recursion=1, web=1, num=100), token)
# 返回 list[]：path / server_filename / fs_id / size / server_mtime
```

- 先搜**最独特的书名关键词**，再降级搜更短词。实测一次命中两个版本（62MB 与 16.79MB）。
- **同一个书常有多个版本**：先下**最小的那个**（大概率是文字版），验证文字层后再决定要不要下大的。

## 二、按 fs_id 直下（按路径下会 errno=2）

```python
m = api("filemetas", dict(dlink=1, fsids=json.dumps([fs_id])), token)
dlink = m["info"][0]["dlink"]
url = dlink + ("&" if "?" in dlink else "?") + "access_token=" + quote(token)
# 带 UA 请求，stream 写盘，最后比对本地字节 == 云端 size
```

- 字段名是 **`fs_id`**（不是 `fsid`）。写错不会报错，只会静默“待下载 0 个”。
- **必做字节校验**：`got == size` 才算下完。实测 17,607,984 == 17,607,984。
- 非会员限速约 85 KB/s：十几 MB 可前台等，上百 MB 必须 `background=true` + `notify_on_complete=true`。

## 三、PDF → 纯文本，先判文字版

```python
import fitz
d = fitz.open(pdf)
print(d.page_count, sum(len(p.get_text()) for p in d))
```

- 全书 0 字 / 单页 0 字但 1 张图 = **扫描版**，先找更小的文字版，别直接 OCR。
- 抽出 txt 后规范化：`\r\n|\r → \n`、压缩空行、去行首尾空格（不规范化会毁掉行号定位）。
- 建章节目录：正则抓 `^第[一二三四五六七八九十]+章`、`^小结$`，打印「章名 + 行号」当骨架，后续按行区间取章。
- 报三个数：页数 / 字符数 / 汉字数。与出版社标称字数对得上（标 13.1 万字 → 11.3 万汉字）才算拿到真全本。

## 四、微信读书网页版（降级通道）

**硬事实：正文不是 DOM 文本。** 实测某本微信读书上架书籍：`.readerChapterContent` 的 `innerHTML` 有 1.2MB，但 `innerText` 只有 25 字；`svg text` = 0，`svg path` = 450，另有两块 canvas。→ 文本节点被画成图形，必须截图 + 视觉模型转录。

可用的钩子：

| 用途 | 选择器 / 做法 |
|:--|:--|
| 当前章节名 | `.renderTargetPageInfo_header_chapterTitle`（唯一可靠；不要用 body 文本按行号猜） |
| 翻页 | `page.mouse.click(内容区)` 拿焦点 → `keyboard.press("ArrowRight")` / `ArrowLeft` |
| 目录 | `.readerCatalog_list_item`（共 43 项，但**矩形全为 0**，虚拟列表点不动） |
| 登录态判断 | body 里有「我的书架」且无「登录」按钮 = 已登录 |

流程（**必须单进程一次跑完**——同一账号另一端翻页会覆盖进度）：

1. 打开 reader URL → 等 4–6s；
2. 用 ArrowLeft 回翻并监测 `.renderTargetPageInfo_header_chapterTitle`，直到命中目标节名；
3. 目标节内循环：截图 → ArrowRight → 再读章节名，**变了就丢弃最后一张**（说明越界）；
4. 每屏过视觉模型（SiliconFlow `Qwen/Qwen3-VL-8B-Instruct` 够用），提示词要求“只转录正文、不转录导航/按钮/页码、不总结、模糊处标〔？〕”。

实测：目标节 6 屏 ≈ 3600 字，与后来拿到的 PDF 文字版相似度 0.891（差值全在导航文字），引文全部命中。

## 五、交叉核（有两条来源时必做）

- `difflib.SequenceMatcher(None, OCR文本, PDF文本).ratio()`：> 0.85 说明 OCR 可用；差得离谱先查是不是抓错了节。
- 用 PDF 当基准重跑引文核验（`scripts/verify_quotes.py`），全绿才把课交出去。

## 六、边界

- 只读、只为用户自己学：**不整本导出分发、不挂在公共位置**。
- 用户自己划的线只用来排“先讲哪节”，不当原文引用。
- 官方从不公开主观题真题之类的东西，同理：**找不到就说找不到，不编来源**。
