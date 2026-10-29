# Word/docx 外科式改稿（python-docx 路径）

**场景**：手账图改了很多轮之后，Word 攻略里积累了过时内容；或用户说「把图上放不下的内容
都放到 word 里」。**此时不要重写整份 Word**（原文件里嵌了图、样式、章节结构，重写必丢），
而是**在现有 docx 上做定点替换 + 末尾追加**。

---

## 一、先摸清结构（省一半力气）

```powershell
# 1) 大小与最后修改时间
Get-Item "<docx>" | Select-Object Name,@{n='KB';e={[math]::Round($_.Length/1KB,1)}},LastWriteTime

# 2) 解包看内嵌图（后续验证"有没有丢图"的基准）
$tmp="$env:TEMP\docx_probe"; Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory("<docx>", $tmp)
Get-ChildItem "$tmp\word\media" | Select-Object Name,Length
```

读正文用 `read_file <docx>`（工具会自动抽取文本，**但不含图片**）。
抽取出的行号 ≈ 段落索引，可用于定位要改的句子。

**踩坑**：先确认**生成脚本还在不在**。本次 `$HOME\.hermes\tmp\henan\` 里有 74 个 .py，
但 `check_all.py` 只是**复核脚本**（而且里面的行程是早已废弃的旧版），真正生成 docx 的脚本没留下。
→ **发现"没有生成脚本"就直接走外科式改稿**，别花时间考古。

---

## 二、改稿三原则

1. **不改结构，只换文本**：段落数、样式、图片一个都不动。
2. **末尾追加新章节**，不要插进正文中段（插入位置需要遍历 body 元素，风险高、收益低）。
   ```python
   doc.add_page_break()
   doc.add_heading("附录一 · XXX", level=1)
   doc.add_heading("一、小标题", level=2)   # H3 → level=2
   doc.add_paragraph("正文…")
   ```
3. **先备份**：`_备份/<原名>_备份<日期>.docx`（与桌面交付目录并列，用户可随时回滚）。

---

## 三、段落文本替换（保格式的关键写法）

`paragraph.text` 是**只读**的，要改必须落到 run 级：

```python
def set_paragraph_text(p, new_text):
    """整段重写：保留首个 run 的格式，其余 run 清空。"""
    if not p.runs:
        return False
    p.runs[0].text = new_text
    for r in p.runs[1:]:
        r.text = ""
    return True
```

- **好处**：跨 run 的断句（Word 常把一句话拆成多个 run）一并解决。
- **代价**：整段统一用首个 run 的格式 → **对正文段落没问题**；对**标题/混排段落**（段内多种字号）
  会让整段变成一个样式。所以：**只用它改正文段落**，标题不动。
- ⚠️ 段落里含 `<w:drawing>`（内嵌图）时，`r.text = ""` 不会删图（图挂在 run 的其他元素上），
  但为保险，**别对含图片的段落做整段重写**。

---

## 四、必须先跑 dry-run（本次挡住 0 处错改，但它是护栏）

脚本写成双模式：`python update_docx.py --dry` 只打印匹配情况，不带 `--dry` 才落盘。

```python
hit, plan, miss = 0, [], []
for old, new in REPL:                 # REPL = [(锚点串, 新整段文本), ...]
    matched = next((p for p in doc.paragraphs if old in p.text), None)
    if matched:
        hit += 1; plan.append((matched, new)); print("  ✔", old[:46])
    else:
        miss.append(old[:46]);                print("  ✘ 未匹配：", old[:46])
print("命中 %d / %d" % (hit, len(REPL)))
if "--dry" in sys.argv:
    return 0 if not miss else 1
```

**锚点串怎么写**：取**要改的那段里最独特的一小截**（含数字/专名最稳），
不要用整段（read_file 抽取的文本可能与 XML 里的空白/换行有细微差异）。
本次 18 条锚点**全部一次命中**，就是因为每条都带了独有数字或专名
（如 `建议 11:30 从家出发去目的地站站（预留 1 小时到站）`、`龙门石窟 约90×2+儿童半价 ≈ 270元`）。

**`old` 没命中时不要放宽成模糊匹配** —— 那会误改到别处。回去用 read_file 复查那一行的确切文字。

---

## 五、改完的三件套验证（缺一件都不算过）

```python
# ① 图片不能少
with zipfile.ZipFile(NEW) as z:  new_media = [n for n in z.namelist() if n.startswith("word/media/")]
with zipfile.ZipFile(SRC) as z:  old_media = [n for n in z2.namelist() if n.startswith("word/media/")]
assert len(new_media) >= len(old_media)      # 本次：原 11 张 → 新 11 张 ✅

# ② 新内容必须在
for k in ["附录一 · 万岁山门票赠三园", "13:45 出门", "单日票"]:
    assert any(k in p.text for p in doc.paragraphs)

# ③ 旧表述必须清干净（搜"即将被推翻的那句话"）
for bad in ["三日内不限次入园，明天上午还能再刷", "门票为【三日有效】"]:
    assert all(bad not in p.text for p in doc.paragraphs)
```

**⚠️ `doc.paragraphs` 不含表格内的段落**。段落总数比 `read_file` 抽出的行数少是**正常的**
（本次 204 段 vs 258 行，差的是标题映射与空段）。
先 `len(doc.tables)` 确认有没有表格 —— **有表格就必须单独遍历 `table.rows[].cells[].paragraphs`**，
否则"表格里的旧数据"会被漏掉。

---

## 六、落盘与交付

```powershell
Copy-Item "<tmp>\xxx_updated.docx" "<桌面>\xxx.docx" -Force
Get-Item "<桌面>\xxx.docx" | Select-Object Name,@{n='KB';e={[math]::Round($_.Length/1KB,1)}},LastWriteTime
```

- **先生成到临时目录、验证通过再覆盖桌面**（避开"Word 正开着无法覆盖"）。
- 覆盖后**再读一次**（`read_file` 或 python-docx 抽段落）确认关键章节在位 —— 本次覆盖后又
  抽了附录一（段 177–194）+ 附录二 逐条打印，才敢说"改好了"。
- 交付话术里**点名"改了哪几处 + 图片零丢失 + 备份路径"**，用户会据此判断要不要重开文件。

---

## 七、本次实战样本（河南 6 日行程，某日）

- 原文件：`河南6日旅行攻略.docx`（3270 KB，11 张内嵌配图，258 行正文）
- 改动：**18 处定点替换 + 2 个附录**（附录一三园介绍 / 附录二换乘兜底）
- 结果：18/18 命中、图片 11→11、旧表述全清、3270 KB 不变
- 脚本：`$HOME\.hermes\tmp\henan\update_docx.py`（`--dry` 双模式，可直接改 REPL 复用）

---

## 八、段落级增删的四个新坑（某日 实战：加 3 段「课本连线」+ 删附录二/三 26 段）

本轮一次跑完「定点替换 16 处 + 插 3 段 + 删 2 个附录」，四个坑全部踩到：

### 坑 1｜**同一段里有多处要改时，别在首个命中就 `break`**（最隐蔽）

写「一段一条 fix、命中即 `break`」的循环 → **同一段里的第 2、3 处永远改不到**，
而脚本会打印「改 16 处 ✅」，看着全部成功。本轮真实残留：`P026` 里三条距离
（步行 1.2 km / 11.6 km / 5.0 km）只改了第一条，另两条活到了交付前。
→ **正确写法**：对每个段落遍历**全部** FIXES（不要 break），并**收尾再扫一遍旧串计数**：
```python
for i, p in enumerate(doc.paragraphs):
    for old, new in FIXES:
        if old in p.text:
            rep(p, old, new)          # 不要 break
...
after = "\n".join(x.text for x in doc.paragraphs)
for k in ["38.6", "11.6 km", "12.0 km", "5.0 km", "680–1200"]:
    print(k, after.count(k))          # 必须是 0，非 0 就再补一轮
```
**判据：改完按旧串逐条计数，任一 >0 就是没改干净**（这比"改了 N 处"这句自报有用得多）。

### 坑 2｜删整章：从标题段一路删到文末，**图片数下降是预期结果**

```python
start = next(i for i, p in enumerate(doc.paragraphs) if p.text.strip().startswith("附录二"))
for p in doc.paragraphs[start:]:                 # 含标题段本身
    p._element.getparent().remove(p._element)    # 段落连带其中的 <w:drawing> 一起消失
```
- 删前**先确认它到文末之间没有别的内容**（本轮打印每个非空段落 + 是否含图，确认附录三就是最后一节）。
  ⚠️ **上一轮可能刚把某节标记成「已取消·仅作备查」** —— 用户说"删"就整节删，别只删正文留标题。
- 删完 **`inline_shapes` 会掉**（本轮 12→8，4 张洛阳配图随段落消失）——
  **这与前几轮"图片数不能减"的验收标准相反**，要在报告里**主动说明"本次是删内容，图数按预期减少"**，
  否则用户会以为又丢图了。`word/media/` 里的文件会变成未引用残留（无害，不必清）。
- 删完**顺手查"有没有别处还在引用这节"**（目录/TOC、正文里的「详见文末附录二」）——
  本轮正文无引用，故未连坐；有引用就必须一起改。

### 坑 3｜插段落用「标题段锚点 + `addnext`」，**别用索引**

```python
import copy, docx
newp = copy.deepcopy(anchor._element)          # 复制同款段（继承样式）
para = docx.text.paragraph.Paragraph(newp, anchor._parent)
for r in list(para.runs):                      # 清掉复制来的旧文字（留格式）
    r._element.getparent().remove(r._element)
para.add_run(新文本)
anchor._element.addnext(newp)
```
- 锚点用**标题段前缀**匹配（本轮 `p.text.strip().startswith("第3天")`），不要用段落索引 ——
  **插入会让后面所有索引漂移**。
- **动作顺序固定为：① 定点替换 → ② 插入 → ③ 删除**，或**先记录锚点串、每一步重新定位**；
  本轮按此顺序（替换 16 → 插 3 → 删 23）才没有互相踩。

### 坑 4｜Word/xlsx 也会**整体落后一个行程版本**，动手前先"验版本"

本轮接手时 docx/xlsx 还停在**已作废的洛阳版**（D5=龙门石窟、D6=G406），而手账图早已是新版 ——
F 清单里有 4 项"没找到落点"就是因为它根本不在这一版里。
→ **动作**：改之前先对主文档做**旧地名/旧车次计数**（`洛阳`/`龙门`/`G2207`/`G406`），
计数 >0 且伴随新版地标为 0 ⇒ **这是旧版**，先决定"整段搬走还是就地改"（本轮：旧版内容整体搬进
「附录三·已取消（留档）」，用户后来直接叫删），再动手；**不要在小改清单里假装它是当前版**。
→ 与 SKILL.md 铁律 23 ①（HTML 变体页漂移）同源：**任何载体动手前先验版本，别假设上游改了它就跟着改**。

### 落盘后的双份一致性

本次同时维护「桌面成品」与 `~/.hermes/tmp/henan/` 镜像两份 docx，收尾用 **md5 比对**：
```python
import hashlib; hashlib.md5(Path(d).read_bytes()).hexdigest()[:12]
```
两处 md5 不一致 = 有一次 `save()` 只写了一边（本轮两次替换各 `save` 一次，靠这行确认同步）。
