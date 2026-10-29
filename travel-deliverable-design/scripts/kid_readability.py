# -*- coding: utf-8 -*-
"""儿童版行程页前的可读性诊断：汉字量 / 成人向术语数 / 注音数。

用途：用户说「行程能不能改得更合适小学生看的」时，**先量再改**。
  实测基准（河南线家长版手账，某日）：716-1146 字/页、5-13 个成人术语、0 注音
  -> 结论：那是给家长的执行手册，二年级读不动 -> 另开一套儿童版（见 references/kid-version-pages.md）

用法：
  python kid_readability.py <页面目录> [页面文件1 页面文件2 ...]
  python kid_readability.py "$HOME/.hermes/tmp/henan/scrapbook" d1.html d2_v4.html d3.html

⚠️ 只看「汉字量 / 术语数 / 注音数」三个准指标。
   脚本里的「最长句/平均句长」在本项目**不可用** —— 手账页是标签式短语（`🏠 13:45 出门 · 打车 20 分钟`）
   而非完整句子，按标点切句会把整块当成一句。
"""
import io
import os
import re
import sys

# 二年级/四年级都读不动的行程执行术语（改版时按新页面补充）
JARGON = ['检票口', '接驳', '兜底', '候客点', '预约', '换乘', '出站', '进站',
          '已付', '备选', '耗时', '区间', '单次入园', '不限次', '优待票', '分时',
          '费用', '预估', '存包', '寄存', '寄存处', '接驳车', '网约车', '错峰',
          '实名', '票面', '作废', '返程', '动线', '节点']


def strip_html(path):
    h = io.open(path, encoding='utf-8').read()
    h = re.sub(r'<style.*?</style>', '', h, flags=re.S)
    return re.sub(r'<[^>]+>', '\n', h)


def report(path):
    txt = '\n'.join(l.strip() for l in strip_html(path).split('\n') if l.strip())
    chars = len(re.sub(r'[\s\W]', '', txt))
    hits = {w: txt.count(w) for w in JARGON if w in txt}
    pinyin = len(re.findall(r'[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]', txt))
    return chars, sum(hits.values()), pinyin, hits


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    base = sys.argv[1]
    files = sys.argv[2:]
    if not files:
        files = sorted(f for f in os.listdir(base)
                       if f.endswith('.html') and not f.startswith('_bak'))
    print('%-16s %8s %9s %8s  %s' % ('页面', '汉字量', '成人术语', '注音', '术语明细'))
    print('-' * 84)
    tot_j = 0
    for fn in files:
        p = fn if os.path.isabs(fn) else os.path.join(base, fn)
        if not os.path.exists(p):
            print('%-16s  (缺文件) %s' % (fn, p))
            continue
        c, n, py, hits = report(p)
        tot_j += n
        detail = ', '.join('%s×%d' % (k, v) for k, v in sorted(hits.items(), key=lambda x: -x[1])[:6])
        print('%-16s %8d %9d %8d  %s' % (fn[:16], c, n, py, detail))
    print('-' * 84)
    print('判据：汉字量 >600 / 成人术语 >3 / 注音 =0 的页面 = 家长版，孩子读不动')
    print('      -> 走 references/kid-version-pages.md 另做儿童版（约 260 字/页、0 术语、ruby 注音）')
    print('本次合计成人术语 %d 个' % tot_j)
    return 0


if __name__ == '__main__':
    sys.exit(main())
