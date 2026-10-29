#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
research_pipeline.py —— 区域企业调研一键流水线（配 bank-region-economy-research 使用）

一条命令跑完：抓政务原文 → 抽企业主体 → 口径过滤 → 出三件交付物 → 跑四层自检

用法
  # 1) 换区县：先写一份 config（参照 configs/example.json）
  python research_pipeline.py crawl   --config configs/example.json
  python research_pipeline.py extract --config configs/example.json
  python research_pipeline.py build   --config configs/example.json [--picks picks.json]
  python research_pipeline.py audit   --config configs/example.json
  # 或一步到底
  python research_pipeline.py all     --config configs/example.json [--picks picks.json]

  # 只跑几个镇街（试跑/补跑）
  ... --towns 镇A,镇B --out D:/tmp/testrun

产物（默认写到 config.out_dir）
  corpus.json           政务原文全文（带 url/date/zhen）
  candidates.json/.txt  候选企业（带证据句）
  keep.json             过闸后的名单
  drop.json             被剔除的（附原因，供核对）
  目标客户名单.xlsx      6 页签：名单/分布/剔除/待核/市场载体/核实卡
  调研报告.docx/.md      与 xlsx 同源
  拜访路线图.xlsx        按天排的拜访路线
  audit_report.md       四层自检结果

设计原则（与技能里的口径一致）
  · 时间闸：只留数据年份 ≥ min_year（默认 2024）
  · 主体闸：只留公司制主体（*有限公司/股份/合伙/个体户）
  · 行业闸：命中 exclude_words 的一律剔除（4S/汽修贸/餐饮/物流/地产/家具/航空/整车/景区…）
  · 来源闸：每条必须带 URL；查不到写"未查到"
  · 审计：名单逐条回原文核名字、核每个数字、核认定，报告正文数字与数据对账
"""

import argparse, json, os, re, sys, time, csv
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

try:
    from urllib.request import Request, urlopen
    import socket
except Exception:
    print("需要标准库 urllib"); sys.exit(2)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
HDR = {"User-Agent": UA}


# ---------------------------------------------------------------- 基础
def cfg_path(p):
    """相对路径优先按 cwd，再按脚本同目录的上级（技能根）找；顺手容错 MSYS 的 /c/... 写法"""
    if re.match(r"^/[a-zA-Z]/", p):
        p = p[1].upper() + ":" + p[2:]
    if os.path.isabs(p) and os.path.exists(p):
        return p
    cands = [os.path.abspath(p),
             os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), p)]
    for c in cands:
        if os.path.exists(c):
            return c
    return os.path.abspath(p)


def load_cfg(p):
    with open(cfg_path(p), encoding="utf-8") as f:
        cfg = json.load(f)
    cfg.setdefault("min_year", 2024)
    cfg.setdefault("max_pages", 8)
    cfg.setdefault("sleep", 0.12)
    cfg.setdefault("workers", 8)
    cfg.setdefault("exclude_words", [])
    cfg.setdefault("keep_words", [])
    cfg.setdefault("out_dir", "out")
    cfg["out_dir"] = os.path.abspath(cfg["out_dir"])
    os.makedirs(cfg["out_dir"], exist_ok=True)
    return cfg


def http_get(url, timeout=25, retry=1):
    for i in range(retry + 1):
        try:
            with urlopen(Request(url, headers=HDR), timeout=timeout) as r:
                raw = r.read()
            for enc in ("utf-8", "gbk", "gb18030"):
                try:
                    return raw.decode(enc)
                except Exception:
                    continue
            return raw.decode("utf-8", "ignore")
        except Exception:
            if i >= retry:
                return ""
            time.sleep(1.2)


def html2text(h):
    if not h:
        return ""
    h = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<br\s*/?>", "\n", h, flags=re.I)
    h = re.sub(r"</(p|div|tr|h\d|li|section)>", "\n", h, flags=re.I)
    h = re.sub(r"<[^>]+>", "", h)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&#39;", "'"), ("&ldquo;", "“"), ("&rdquo;", "”")):
        h = h.replace(a, b)
    h = re.sub(r"[ \t\u3000]+", " ", h)
    return "\n".join(l.strip() for l in h.split("\n") if l.strip())


# ---------------------------------------------------------------- 1 crawl
ART = re.compile(r'href="(?:\./)?(\d{6})/t(\d{8})_(\d+)\.html"[^>]*>(.*?)</a>', re.S)
BODY = re.compile(r'<div[^>]+(?:class="[^"]*(?:content|article|TRS_Editor|view)[^"]*")[^>]*>(.*?)</div>\s*(?:</div>|<div)', re.S)


def extract_body(cfg, h):
    """正文提取：把候选容器全部试一遍，取**最长**的那块。
    为什么不取第一个——实测某县级市页里 "article-meta" 排在 "article-body" 前面，
    取首个会拿到 59 字的元信息块，整篇文章变成空。取最长是通吃各站结构的稳妥做法。
    config.body_regex 可显式指定（某些站点要精确到 id）。"""
    pats = []
    if cfg.get("body_regex"):
        pats.append(cfg["body_regex"])
    pats.append(r'<div[^>]+(?:class|id)="[^"]*(?:content|article|TRS_Editor|view|zoom|detail)[^"]*"[^>]*>(.*?)</div>\s*(?:</div>|<div)')
    best = ""
    for p in pats:
        for m in re.finditer(p, h, re.S):
            t = html2text(m.group(1))
            if len(t) > len(best):
                best = t
    return best or html2text(h)

def town_root(cfg, base, code):
    """镇街列表页根地址模板可配（各区县政务网路径不同，换区县必改这一项）"""
    tpl = cfg.get("town_url_tpl") or "/zwgk/zjdxxgkml/{code}/"
    return base + tpl.format(code=code)


def discover_channels(cfg, base, code):
    """镇街站点结构不一：先读目录页里的跳转/栏目链接找到子栏目。
    —— 参考实例是 meta refresh（url=./xxgkznN/，栏目码带数字）；
    —— 有的区县是纯字母栏目码（如 xxgkzn），正则要可配。"""
    root = http_get(town_root(cfg, base, code))
    pat = cfg.get("chan_regex") or r"url=\.?/?([a-z]+\d+)/"
    m = re.search(pat, root or "")
    if not m:
        return []
    h = http_get(town_root(cfg, base, code) + m.group(1) + "/")
    return sorted(set(re.findall(r"\.\./([a-z]+\d*)/", h or "")))


def crawl(cfg, towns=None):
    base = cfg["base_url"].rstrip("/")
    min_year = cfg["min_year"]
    index = []
    for zhen, meta in cfg["towns"].items():
        if towns and zhen not in towns:
            continue
        code = meta["code"] if isinstance(meta, dict) else meta
        chans = meta.get("channels") if isinstance(meta, dict) else None
        if not chans:
            chans = discover_channels(cfg, base, code)
        use = [c for c in chans if c.startswith(("gzdt", "tzgg", "ghjh"))] or chans
        print(f"[crawl] {zhen} {code} 栏目 {use}", flush=True)
        seen, got = set(), 0
        for chan in use:
            for p in range(cfg["max_pages"]):
                url = f"{town_root(cfg, base, code)}{chan}/" + ("" if p == 0 else f"index_{p}.html")
                h = http_get(url)
                if not h:
                    break
                found = 0
                for ym, ymd, aid, title in ART.findall(h):
                    u = f"{town_root(cfg, base, code)}{chan}/{ym}/t{ymd}_{aid}.html"
                    if u in seen:
                        continue
                    seen.add(u)
                    d = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"
                    if d < f"{min_year}-01-01":
                        continue
                    index.append({"zhen": zhen, "url": u, "date": d,
                                  "title": html2text(title).replace("\n", " ").strip()})
                    found += 1
                if found == 0 and p > 0:
                    break
                time.sleep(cfg["sleep"])
        print(f"[crawl] {zhen} 收录 {len([x for x in index if x['zhen']==zhen])} 篇", flush=True)

    json.dump(index, open(os.path.join(cfg["out_dir"], "index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    def work(it):
        h = http_get(it["url"])
        if not h:
            return None
        body = extract_body(cfg, h)
        if len(body) < 120:
            return None
        d = dict(it); d["text"] = body
        return d

    out = []
    with ThreadPoolExecutor(max_workers=cfg["workers"]) as ex:
        for i, r in enumerate(ex.map(work, index)):
            if r:
                out.append(r)
            if (i + 1) % 100 == 0:
                print(f"[crawl] 正文 {i+1}/{len(index)}", flush=True)
    if out:
        json.dump(out, open(os.path.join(cfg["out_dir"], "corpus.json"), "w", encoding="utf-8"),
                  ensure_ascii=False)
    else:
        print("[crawl] 镇街 0 篇 → 不覆盖已有 corpus.json（防丢语料）", flush=True)
    mc = cfg.get("min_corpus", 300)
    if towns and towns != ["__none__"] and len(out) < mc:
        print(f"⚠️  语料仅 {len(out)} 篇，低于 min_corpus={mc}——先确认 town_url_tpl / chan_regex 是否匹配该区县的网站结构，别急着当‘已跑通’", flush=True)
    print(f"[crawl] 镇街完成：{len(index)} 篇索引，{len(out)} 篇正文", flush=True)

    # 县级频道：宏观/竞争两章的语料来源（政务要闻/部门动态/镇街动态）
    cc = cfg.get("county_channels") or {}
    if cc and (not towns or towns == ["__none__"]):
        prefix = cfg.get("county_prefix", "/zwgk/zfxxgkml/gzdt75")
        cidx, seen2 = [], set()
        for label, chan in cc.items():
            for p in range(cfg["max_pages"]):
                url = f"{base}{prefix}/{chan}/" + ("" if p == 0 else f"index_{p}.html")
                h = http_get(url)
                if not h:
                    break
                found = 0
                for ym, ymd, aid, title in ART.findall(h):
                    u = f"{base}{prefix}/{chan}/{ym}/t{ymd}_{aid}.html"
                    if u in seen2:
                        continue
                    seen2.add(u)
                    d = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"
                    if d < f"{cfg['min_year']}-01-01":
                        continue
                    cidx.append({"zhen": "县级", "url": u, "date": d,
                                 "title": html2text(title).replace("\n", " ").strip()})
                    found += 1
                if found == 0 and p > 0:
                    break
                time.sleep(cfg["sleep"])
        cout = []
        with ThreadPoolExecutor(max_workers=cfg["workers"]) as ex:
            for r in ex.map(work, cidx):
                if r:
                    cout.append(r)
        json.dump(cout, open(os.path.join(cfg["out_dir"], "corpus_county.json"), "w", encoding="utf-8"),
                  ensure_ascii=False)
        print(f"[crawl] 县级完成：{len(cidx)} 篇索引，{len(cout)} 篇正文", flush=True)
    return out


# ---------------------------------------------------------------- 2 extract
CORE = r"[\u4e00-\u9fa5A-Za-z0-9（）()·]"
NAME = re.compile(CORE + r"{2,24}?(?:股份有限公司|有限责任公司|有限公司)")
EV = re.compile(r"(亿元|万元|产值|营收|营业收入|销售收入|纳税|税收|订单|产能|专利|小巨人|专精特新|"
                r"高新技术企业|单项冠军|龙头|上市|扩产|扩能|投产|增资|技改|摘牌|亩产)")


def clean_name(n):
    n = re.sub(r"^(?:了|的|是|与|和|及|为|在)", "", n)
    for _ in range(5):
        m = re.search(r"(的|是|了|与|和|及|为|在|由|把|被|对|向|深入|走进|走访|调研|考察|成立|落款|"
                      r"引进|招引|落户|支持|服务|企业|公司|集团|商会|一行|负责人|总经理|董事长|"
                      r"包括|其中|记者|来到|探访|代表|首批|另有|分别|以及|先后|共计|约有|据悉|此外|"
                      r"引导|推动|助力|协助|协调|组织|带领|陪同|检查|督导|帮扶|培育|扶持|指导|鼓励)", n)
        if m and len(n) - m.end() >= 6:
            n = n[m.end():]
        else:
            break
    return n.strip("，。、 　:：")


def best_sentence(ctx, limit=110):
    """挑出最有信息量的那一句，分两档：
    ① 有金额/数量 + 经营词（最优）
    ② 有经营/认定词但无金额（次优，注明无金额）
    ③ 都没有 → 明说“原文无经营数据”，不许硬截句首充数。
    负面/无关句（亏损、倒闭、处罚、招聘、天气…）一律跳过。"""
    NEG = re.compile(r"(亏损|倒闭|破产|处罚|失信|关停|投诉|事故|火灾|纠纷|诉讼|辞职|离职|招工|招聘|天气|游客)")
    parts = [p.strip() for p in re.split(r"(?<=[。；！？])", ctx) if len(p.strip()) > 8]
    tier1, tier2 = [], []
    for p in parts:
        if NEG.search(p):
            continue
        evn, numn = len(EV.findall(p)), len(re.findall(r"\d", p))
        if evn and numn:
            tier1.append((evn * 10 + numn, p))
        elif evn:
            tier2.append((evn, p))
    if tier1:
        tier1.sort(key=lambda x: -x[0])
        return tier1[0][1][:limit]
    if tier2:
        tier2.sort(key=lambda x: -x[0])
        return tier2[0][1][:limit] + "（无金额数据，待补）"
    return "（原文无经营数据，待核）"


IND_MAP = [
    (("机械", "装备", "重工", "机床", "机电", "模具", "铸", "零部件", "液压", "轴承", "泵", "电机", "钢结构", "钣金", "智造"), "装备制造"),
    (("新材料", "复合材料", "铝", "钢", "陶瓷", "玻璃", "涂料", "管材"), "新材料"),
    (("电子", "半导体", "芯片", "光电", "传感", "软件", "数字", "智能", "机器人"), "电子信息/智能装备"),
    (("医药", "生物", "医疗", "器械", "制药"), "生物医药"),
    (("食品", "饲料", "茶", "食用菌", "果蔬", "粮油", "肉", "预制"), "食品与农产品加工"),
    (("种业", "种苗", "繁育", "农业", "农牧", "种植"), "农业/种业"),
    (("包装", "印刷", "纸", "塑"), "包装印刷"),
    (("电力", "电缆", "电气", "能源"), "电力电气"),
]


def guess_industry(name, ctx):
    blob = f"{name} {ctx}"
    for kws, label in IND_MAP:
        if any(k in blob for k in kws):
            return label
    return "待分类"


def extract(cfg):
    p = os.path.join(cfg["out_dir"], "corpus.json")
    corpus = json.load(open(p, encoding="utf-8"))
    foreign = cfg.get("foreign_prefixes", [])
    ents = defaultdict(lambda: {"zhen": set(), "n": 0, "ev": [], "dates": set()})
    for art in corpus:
        t = art.get("text") or ""
        for m in NAME.finditer(t):
            nm = clean_name(m.group(0))
            if len(nm) < 7:
                continue
            # “A联合B公司”“A携手B科技有限公司”会把两家黏成一家 → 只留 A；A 太短就整条丢
            for sep in ("联合", "携手", "合作", "与", "、", "和"):
                if sep in nm:
                    head = nm.split(sep)[0].strip()
                    nm = head if len(head) >= 8 else ""
                    break
            if not nm:
                continue
            # 名称必须以组织形式结尾，否则说明前缀没剥干净 → 宁可漏，不可错
            if not nm.endswith(("有限公司", "有限责任公司", "股份有限公司")):
                continue
            if any(w in nm for w in cfg["exclude_words"]):
                continue
            if foreign and any(nm.startswith(f) for f in foreign):
                continue
            # 村集体/社区/股份经济合作社成立的主体，不作为授信主体
            win = t[max(0, m.start() - 12):m.start()]
            if re.search(r"(村|社区|股份经济合作社|村集体)", win):
                continue
            e = ents[nm]
            e["zhen"].add(art["zhen"]); e["n"] += 1; e["dates"].add(art["date"])
            s, x = max(0, m.start() - 110), min(len(t), m.end() + 160)
            ctx = re.sub(r"\s+", " ", t[s:x])
            if EV.search(ctx) and len(e["ev"]) < 4:
                e["ev"].append({"date": art["date"], "url": art["url"], "ctx": ctx})

    cands = []
    for nm, e in ents.items():
        if not e["ev"]:
            continue
        cands.append({"name": nm, "zhen": sorted(e["zhen"]), "latest": max(e["dates"]),
                      "mentions": e["n"],
                      "ind": guess_industry(nm, e["ev"][0]["ctx"]),
                      "ev": [{"date": v["date"], "url": v["url"], "ctx": v["ctx"][:220],
                              "key": best_sentence(v["ctx"])} for v in e["ev"][:3]]})
    cands.sort(key=lambda c: (c["zhen"][0] if c["zhen"] else "", -c["mentions"]))
    json.dump(cands, open(os.path.join(cfg["out_dir"], "candidates.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(cfg["out_dir"], "candidates.txt"), "w", encoding="utf-8") as f:
        cur = None
        for c in cands:
            z = c["zhen"][0] if c["zhen"] else "?"
            if z != cur:
                cur = z
                f.write(f"\n===== {z} =====\n")
            f.write(f"- {c['name']} [{c['latest']}]x{c['mentions']}\n")
            for v in c["ev"]:
                f.write(f"    {v['date']} {v['ctx'][:170]}\n")
    print(f"[extract] 候选 {len(cands)} 家 → candidates.json/.txt", flush=True)
    return cands


# ---------------------------------------------------------------- 3 gate
def gate(cfg, cands, picks=None):
    keep, drop = [], []
    min_year = cfg["min_year"]
    for c in cands:
        blob = c["name"]
        if any(w in blob for w in cfg["exclude_words"]):
            drop.append({"name": c["name"], "why": "命中剔除词"}); continue
        y = re.search(r"(20\d\d)", c["latest"])
        if not y or int(y.group(1)) < min_year:
            drop.append({"name": c["name"], "why": f"数据年份 <{min_year}"}); continue
        if not c["ev"]:
            drop.append({"name": c["name"], "why": "无证据句"}); continue
        keep.append({"镇街": c["zhen"][0] if c["zhen"] else "",
                     "企业": c["name"], "行业": c.get("ind", "待分类"),
                     "关键数据": f"{c['latest']} {c['ev'][0].get('key') or c['ev'][0]['ctx'][:120]}",
                     "数据年份": c["latest"][:4],
                     "认定": "无", "业务线": "—",
                     "来源": c["ev"][0]["url"], "可信度": "A",
                     "名称核验": "全称命中"})
    if picks:
        pp = picks if isinstance(picks, list) else picks.get("items", [])
        have = {k["企业"] for k in keep}
        for p in pp:
            if p["企业"] in have:
                for k in keep:
                    if k["企业"] == p["企业"]:
                        k.update({kk: vv for kk, vv in p.items() if vv})
                continue
            keep.append({"名称核验": "全称命中", "可信度": "A", **p})
    json.dump(keep, open(os.path.join(cfg["out_dir"], "keep.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(drop, open(os.path.join(cfg["out_dir"], "drop.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"[gate] 过闸 {len(keep)} 家，剔除 {len(drop)} 家", flush=True)
    return keep, drop


# ---------------------------------------------------------------- 4b macro / rival（半自动，附原文句）
MACRO_PAT = {
    "GDP/地区生产总值": r"(地区生产总值|GDP)[^。；]{0,40}?\d[\d,\.]*\s*(亿元|亿)",
    "一般公共预算收入": r"一般公共预算收入[^。；]{0,40}?\d[\d,\.]*\s*(亿元|亿)",
    "规模工业/规上工业": r"(规模以上工业|规上工业)[^。；]{0,40}?\d[\d,\.]*\s*(亿元|亿|%)",
    "固定资产投资": r"(固定资产投资)[^。；]{0,40}?\d[\d,\.]*\s*(亿元|亿|%)",
    "市场主体": r"(市场主体|企业数量)[^。；]{0,30}?\d[\d,\.]*\s*(万户|万家|户|家)",
    "专精特新/小巨人": r"(专精特新|小巨人)[^。；]{0,30}?\d+\s*家",
    "百强/排名": r"(百强|第\s*\d+\s*位|排名)[^。；]{0,30}",
}
RIVAL_PAT = {
    "农商行投放/授信": r"(农商|农商银行|农商行)[^。；]{0,60}",
    "金融专员/驻村": r"(金融专员|驻村|金融村官)[^。；]{0,60}",
    "本行/同业竞争": r"(同业|他行|竞争|市场份额)[^。；]{0,60}",
}


def evidence_scan(cfg, pats, title, fname):
    """从已抓语料里扫出指标相关原文句 + 出处，输出“待人工校定”的证据表。
    只抽句子不改写：宏观/竞争数字的口径必须人工定，脚本不替你拍板。"""
    p = os.path.join(cfg["out_dir"], "corpus.json")
    corpus = []
    for f in ("corpus.json", "corpus_county.json"):
        fp = os.path.join(cfg["out_dir"], f)
        if os.path.exists(fp):
            corpus.extend(json.load(open(fp, encoding="utf-8")))
    if not corpus:
        return []
    hits = {k: [] for k in pats}
    for art in corpus:
        t = (art.get("text") or "").replace("\n", " ")
        for name, pat in pats.items():
            for m in re.finditer(pat, t):
                # 按句子边界切，不按字数硬截——硬截会把上半句的营销话术带进来
                lo = max(t.rfind(c, 0, m.start()) for c in "。；！？\n") + 1
                hi_c = [t.find(c, m.end()) for c in "。；！？\n"]
                hi_c = [x for x in hi_c if x != -1]
                hi = min(hi_c) + 1 if hi_c else min(len(t), m.end() + 40)
                sent = re.sub(r"\s+", " ", t[lo:hi]).strip()
                if not (12 <= len(sent) <= 200):
                    continue
                if len(hits[name]) < 6:
                    hits[name].append({"句": sent, "日期": art["date"], "URL": art["url"]})
    lines = [f"# {title}（自动抽取，待人工校定口径）\n",
             "> 下表每行都是**原文原句**，脚本没有改写任何数字。口径（镇本级/含园区、年度/季度）必须人工判断后再进报告正文。\n"]
    for name in pats:
        lines.append(f"\n## {name}\n")
        if not hits[name]:
            lines.append("- 未在语料中检到，需另行检索\n")
            continue
        lines.append("| 原文句 | 日期 | 出处 |")
        lines.append("|---|---|---|")
        for h in hits[name]:
            lines.append(f"| {h['句'][:120]} | {h['日期']} | [原文]({h['URL']}) |")
    fp = os.path.join(cfg["out_dir"], fname)
    open(fp, "w", encoding="utf-8").write("\n".join(lines))
    print(f"[{title[:2]}] 证据表 → {fp}（各指标命中 {', '.join(f'{k}:{len(v)}' for k, v in hits.items())}）", flush=True)
    return lines
def build(cfg, keep, drop):
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except Exception as e:
        print(f"!! 缺 openpyxl（{e}）→ Excel 不会生成。装库：pip install openpyxl", flush=True)
        openpyxl = None

    out = cfg["out_dir"]
    order = cfg.get("town_order") or sorted({k["镇街"] for k in keep})
    keep.sort(key=lambda k: (order.index(k["镇街"]) if k["镇街"] in order else 99, k["企业"]))

    if openpyxl:
        wb = openpyxl.Workbook(); ws = wb.active; ws.title = "目标客户名单"
        HF = PatternFill("solid", fgColor="2F5496"); HFONT = Font(color="FFFFFF", bold=True, size=10)
        BD = Font(size=9); TH = Border(*[Side(style="thin", color="BFBFBF")] * 4)
        ALT = PatternFill("solid", fgColor="D6E4F0")
        cols = ["序号", "镇街", "企业全称", "行业", "关键数据（带年份）", "数据年份", "认定",
                "名称核验", "建议产品", "可信度", "来源URL"]
        ws.append(cols)
        for i, k in enumerate(keep, 1):
            ws.append([i, k.get("镇街", ""), k.get("企业", ""), k.get("行业", ""), k.get("关键数据", ""),
                       k.get("数据年份", ""), k.get("认定", ""), k.get("名称核验", ""),
                       k.get("业务线", ""), k.get("可信度", ""), k.get("来源", "")])
        for i, w in enumerate([6, 12, 34, 22, 62, 10, 14, 24, 18, 8, 66], 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
        for c in ws[1]:
            c.fill = HF; c.font = HFONT; c.alignment = Alignment(horizontal="center", wrap_text=True)
        for ri in range(2, ws.max_row + 1):
            for c in ws[ri]:
                c.font = BD; c.border = TH; c.alignment = Alignment(vertical="top", wrap_text=True)
            if ri % 2 == 0:
                for c in ws[ri]:
                    c.fill = ALT
        ws.freeze_panes = "D2"; ws.auto_filter.ref = ws.dimensions

        ws2 = wb.create_sheet("镇街分布")
        ws2.append(["镇街", "家数", "A级", "B级", "C级"])
        cnt = Counter(k["镇街"] for k in keep)
        for z in order:
            sub = [k for k in keep if k["镇街"] == z]
            ws2.append([z, len(sub), *(sum(1 for x in sub if x.get("可信度") == g) for g in "ABC")])
        ws2.append(["合计", len(keep), *(sum(1 for x in keep if x.get("可信度") == g) for g in "ABC")])

        ws3 = wb.create_sheet("已剔除")
        ws3.append(["企业", "剔除原因"])
        for d in drop:
            ws3.append([d["name"], d["why"]])

        # 路线图（一天 ≤5 家，3 天/周）
        ws4 = wb.create_sheet("拜访路线")
        ws4.append(["周次", "天", "镇街", "企业全称", "关键数据", "来源"])
        days = []
        for z in order:
            sub = [k for k in keep if k["镇街"] == z]
            for i in range(0, len(sub), 5):
                days.append((z, sub[i:i + 5]))
        for wi, start in enumerate(range(0, len(days), 3), 1):
            for di, (z, chunk) in enumerate(days[start:start + 3], 1):
                for k in chunk:
                    ws4.append([f"第{wi}周", f"Day{di}", z, k.get("企业", ""),
                                k.get("关键数据", ""), k.get("来源", "")])
        for i, w in enumerate([8, 7, 12, 34, 62, 66], 1):
            ws4.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

        for sh in (ws2, ws3, ws4):
            for c in sh[1]:
                c.fill = HF; c.font = HFONT
            for ri in range(2, sh.max_row + 1):
                for c in sh[ri]:
                    c.font = BD
        xp = os.path.join(out, "目标客户名单.xlsx")
        wb.save(xp)
        print(f"[build] Excel → {xp}", flush=True)

    # 宏观 / 竞争 证据表（半自动，附原文句）
    macro_lines = evidence_scan(cfg, MACRO_PAT, "宏观底盘证据", "macro_evidence.md")
    rival_lines = evidence_scan(cfg, RIVAL_PAT, "竞争格局证据", "rival_evidence.md")

    top = sorted(keep, key=lambda k: (0 if any(t in k.get("认定", "") for t in ("小巨人", "专精特新", "龙头", "上市", "高企")) else 1))
    md = [f"# {cfg.get('region','区域')} 区域调研报告（{time.strftime('%Y-%m-%d')}）\n",
          f"> 口径：数据年份 ≥ {cfg['min_year']}；仅公司制主体；每条带可点开的原文。\n",
          f"> 本报告由 research_pipeline 生成：第二、三章为**自动抽取的原文证据句，口径待人工校定**；第四至六章为可执行名单。\n"]

    md.append(f"## 一、摘要（四句话）\n")
    def _tag(k):
        v = (k.get("认定") or "").strip()
        return "" if v in ("无", "待核", "—", "-", "none", "None") else v

    if not keep:
        n_art = 0
        for _f in ("corpus.json", "corpus_county.json"):
            _fp = os.path.join(cfg["out_dir"], _f)
            if os.path.exists(_fp):
                n_art += len(json.load(open(_fp, encoding="utf-8")))
        md.append(f"1. 本轮 **0 家**目标客户。语料 {n_art} 篇，正文里没有出现「有限公司/股份公司」这类公司制主体。\n")
        md.append("2. 常见原因：① 抓到的是社区活动/会议/通知类（街道级动态最典型）；② 该镇确实没有规上企业；③ `min_year` 卡太紧或语料太少。\n")
        md.append("3. 下一步按此顺序试：换抓县级频道与党报专题（`site:<党报域名> <镇名> 企业 签约`）→ 放宽 `min_year` → 找镇经发办要规上企业名录。\n")
        md.append("4. **不要在语料不足时硬凑名单**：0 家也是一份可交付的结论，写清为什么比编 5 家强。\n")
        _mp = os.path.join(out, "调研报告.md")
        open(_mp, "w", encoding="utf-8").write("\n".join(md))
        print(f"[build] 0 家：已出说明版报告 → {_mp}（不生成 Excel/Word，因为没有可列的行）", flush=True)
        return
    top_a = [k for k in keep if _tag(k)]
    top = top_a if top_a else keep
    md.append(f"1. 本轮从 {cfg.get('region','本区县')} 政务原文中筛出 **{len(keep)} 家**目标客户，"
              f"覆盖 {len({k['镇街'] for k in keep})} 个镇街，另有 {len(drop)} 家按口径剔除。\n")
    first = top[0]
    first_tag = f"，{_tag(first)}" if _tag(first) else ""
    md.append(f"2. 最优先跑的是：**{first['企业']}**（{first.get('镇街','')}{first_tag}）。\n")
    if len(top) > 1:
        md.append(f"3. 第二梯队：{'、'.join(x['企业'] for x in top[1:4])}。\n")
    md.append("4. 第二、三章的数字为原文抽取、口径未定，**引用前必须回原文核**；第四至六章可直接拿出去跑。\n")

    md.append("## 二、宏观底盘（自动抽取，待人工校定口径）\n")
    md.extend([l for l in macro_lines if l.strip()][2:] if macro_lines else ["- 未生成，检查 corpus.json\n"])
    md.append("\n> 口径纪律：镇本级 vs 含园区口径常差 20 倍，年度 vs 季度也不同；进正文前必须标清来源年份与口径。\n")

    md.append("## 三、竞争格局（自动抽取，待人工校定）\n")
    md.extend([l for l in rival_lines if l.strip()][2:] if rival_lines else ["- 未生成，检查 corpus.json\n"])

    md.append(f"\n## 四、结果：{len(keep)} 家\n")
    md.append("| 镇街 | 家数 | 代表企业 |\n|---|---|---|")
    for z in order:
        sub = [k for k in keep if k["镇街"] == z]
        if sub:
            md.append(f"| {z} | {len(sub)} | {sub[0]['企业']} |")
    md.append(f"| 合计 | {len(keep)} | — |\n")

    md.append("## 五、18 镇街目标客户明细\n")
    cur = None
    for k in keep:
        if k["镇街"] != cur:
            cur = k["镇街"]
            md.append(f"\n### {cur}\n")
            md.append("| 企业全称 | 关键数据 | 认定 | 来源 |\n|---|---|---|---|")
        md.append(f"| {k['企业']} | {k.get('关键数据','')} | {k.get('认定','')} | [原文]({k.get('来源','')}) |")

    md.append("\n## 六、本地行信息与待核项\n")
    md.append("| 项 | 说明 |\n|---|---|")
    md.append("| 工商存续状态 | 未批量核验（公示系统需验证码）；贷前必须用工商+征信过 |\n")
    md.append("| 经营数据 | 仅公开报道口径；营收/纳税/参保需现场三问 |\n")
    md.append("| 名称 | 页面为简称的已标“页面为简称”，全称以工商为准 |\n")

    md.append("\n## 七、剔除清单\n")
    md.append("| 企业 | 原因 |\n|---|---|")
    for d in drop[:300]:
        md.append(f"| {d['name']} | {d['why']} |")

    md.append("\n## 八、数据纪律\n")
    md.append("- 每个数字都带年份，没有年份的不进表。\n"
              "- 每条来源都要能点开看到这个名字。\n"
              "- 数字对不上就删数字，不删企业；名称对不上就换来源，换不到进待核。\n"
              "- 宏观与竞争两章只给原文句，不给结论——结论由人下。\n")

    mp = os.path.join(out, "调研报告.md")
    open(mp, "w", encoding="utf-8").write("\n".join(md))
    print(f"[build] 报告 → {mp}", flush=True)

    # md → docx（复用技能内脚本；缺就跳过）
    docx_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "md2docx_compact.py")
    if os.path.exists(docx_script):
        try:
            import subprocess
            subprocess.run([sys.executable, docx_script, mp, os.path.join(out, "调研报告.docx")],
                           check=False, timeout=300)
            print(f"[build] Word → {os.path.join(out, '调研报告.docx')}", flush=True)
        except Exception as e:
            print("[build] Word 生成失败:", e)
    return keep


# ---------------------------------------------------------------- 5 audit
NUM = re.compile(r"(\d+(?:\.\d+)?)\s*(亿元|万元|亿|万|%|项|平方米|㎡|亩|人)")


def audit(cfg, keep):
    out = cfg["out_dir"]
    lines, probs = [], []

    def p(s=""):
        print(s); lines.append(s)

    p(f"# 审计报告（{time.strftime('%Y-%m-%d %H:%M')}）\n")
    p(f"名单条数：{len(keep)}\n")

    # ① 口径
    bad = [k for k in keep if any(w in k.get("企业", "") for w in cfg["exclude_words"])]
    p(f"① 口径违规：{len(bad)}")
    for b in bad:
        p(f"   ✗ {b['企业']}")
    # ② 年份/URL
    noy = [k for k in keep if not re.search(rf"20({cfg['min_year']%100:02d}|{cfg['min_year']%100+1:02d}|{cfg['min_year']%100+2:02d})", str(k.get("数据年份", "")) + k.get("关键数据", ""))]
    nourl = [k for k in keep if not str(k.get("来源", "")).startswith("http")]
    p(f"② 年份不足 {len(noy)} / 无 URL {len(nourl)}")
    for x in noy[:10]:
        p(f"   ✗ 年份 {x['企业']}")
    for x in nourl[:10]:
        p(f"   ✗ URL {x['企业']}")
    # ③ 名称回源 + 数字回原文
    def page(u):
        return html2text(http_get(u)) if u.startswith("http") else ""

    badname, badnum, notag = [], [], []
    for k in keep[:400]:
        t = page(k.get("来源", ""))
        if not t:
            badname.append((k["企业"], "抓取失败")); continue
        core = re.sub(r"(有限公司|股份有限公司|有限责任公司|集团)", "", k["企业"])[:5]
        if k["企业"] not in t and core not in t:
            badname.append((k["企业"], "页面无此名"))
        miss = []
        for n in NUM.findall(k.get("关键数据", "")):
            v = n[0] if isinstance(n, tuple) else n
            if v not in t:
                miss.append(v)
        if miss:
            badnum.append((k["企业"], miss))
        for kw in ("专精特新", "小巨人", "高新技术企业", "单项冠军"):
            if kw in k.get("认定", "") and kw not in t and kw not in k.get("关键数据", ""):
                notag.append((k["企业"], kw)); break
    p(f"③ 名称对不上 {len(badname)} / 关键数字原文找不到 {len(badnum)} / 认定无出处 {len(notag)}")
    for x in badname[:15]:
        p(f"   ✗ 名称 {x[0]}（{x[1]}）")
    for x in badnum[:15]:
        p(f"   ✗ 数字 {x[0]} 缺 {x[1]}")
    for x in notag[:15]:
        p(f"   ✗ 认定 {x[0]} 缺「{x[1]}」")
    p("\n> 数字对不上就删数字，不删企业；名称对不上就换来源，换不到进待核。")

    rp = os.path.join(out, "audit_report.md")
    open(rp, "w", encoding="utf-8").write("\n".join(lines))
    print(f"\n[audit] → {rp}", flush=True)
    return {"口径违规": len(bad), "年份不足": len(noy), "无URL": len(nourl),
            "名称不符": len(badname), "数字不符": len(badnum), "认定无出处": len(notag)}


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="区域企业调研一键流水线")
    ap.add_argument("step", choices=["crawl", "extract", "build", "audit", "all"])
    ap.add_argument("--config", required=True)
    ap.add_argument("--picks", help="人工确认过的名单 JSON（可选，覆盖/补充自动结果）")
    ap.add_argument("--towns", help="只跑这些镇街，逗号分隔")
    ap.add_argument("--out", help="覆盖输出目录")
    ap.add_argument("--county-only", action="store_true", help="只抓县级频道（宏观/竞争语料），不动镇街")
    a = ap.parse_args()

    cfg = load_cfg(a.config)
    if a.out:
        cfg["out_dir"] = os.path.abspath(a.out); os.makedirs(cfg["out_dir"], exist_ok=True)
    towns = [t.strip() for t in a.towns.split(",")] if a.towns else None
    if a.county_only:
        towns = ["__none__"]
    picks = json.load(open(cfg_path(a.picks), encoding="utf-8")) if a.picks else None

    print(f"=== 区县：{cfg.get('region')} ｜ 输出：{cfg['out_dir']} ===", flush=True)
    if a.step in ("crawl", "all"):
        crawl(cfg, towns)
    if a.step in ("extract", "all"):
        cands = extract(cfg)
    if a.step in ("build", "all"):
        cands = json.load(open(os.path.join(cfg["out_dir"], "candidates.json"), encoding="utf-8"))
        keep, drop = gate(cfg, cands, picks)
        build(cfg, keep, drop)
    if a.step in ("audit", "all"):
        keep = json.load(open(os.path.join(cfg["out_dir"], "keep.json"), encoding="utf-8"))
        audit(cfg, keep)


if __name__ == "__main__":
    main()
