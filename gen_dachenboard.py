#!/usr/bin/env python3
# gen_dachenboard.py — 把 Kimi 画布导出的 dachen-dashboard-v3.json 组装成单页大数据看板。
# 布局 V3(2026-07-19):真实三列 flex 布局,列内卡片按实测内容高度排布、每列最后一张卡拉伸补满,
# 并向各组件注入"面板撑满 iframe"样式 → 三列上下沿对齐、零空隙。
import html
import json
import sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else '/Users/andy/Documents/kimi/workspace/dachen-dashboard-v3.json')
OUT = Path(__file__).parent / 'index.html'
GAP = 10

# 实测内容高度(px)。nh=自然高;列内最后一张卡 flex 拉伸,其余固定 nh。
PLAN = {
    'title':  {'match': '标题栏',  'nh': 68},
    'left':   [{'match': '三平台',  'nh': 461}, {'match': '粉丝画像', 'nh': 460}],
    'center': [{'match': '健康罗盘', 'nh': 565}, {'match': '流量来源', 'nh': 290}],
    'right':  [{'match': '视频号',  'nh': 761}],
    'bottom': {'match': '策略',   'nh': 257},
}
# 注入每个组件(标题栏除外):让最外层面板撑满 iframe 高度,列底不再露出空底色
STRETCH_CSS = ('<style>html,body{height:100%!important}'
               'body{display:flex!important;flex-direction:column!important}'
               'body>:first-child{flex:1 0 auto;display:flow-root}</style>')

d = json.loads(SRC.read_text())
period = d['dataSnapshot']['period']
by_prefix = {w['title'][:3]: w for w in d['widgets']}

def widget(match, stretch=True):
    w = next(w for w in d['widgets'] if w['title'].startswith(match))
    doc = w['files']['index.html']
    if stretch:
        doc = doc.replace('</head>', STRETCH_CSS + '</head>', 1)
    return w['title'], html.escape(doc, quote=True)

def cell(match, nh, last=False, stretch=True):
    t, doc = widget(match, stretch)
    style = f'flex:1 1 {nh}px;min-height:{nh}px' if last else f'flex:0 0 {nh}px;height:{nh}px'
    return (f'<div class="cell" style="{style};--nh:{nh}px">'
            f'<iframe title="{html.escape(t)}" srcdoc="{doc}" scrolling="no"></iframe></div>')

def column(key, span):
    items = PLAN[key]
    inner = '\n'.join(cell(it['match'], it['nh'], last=(i == len(items) - 1)) for i, it in enumerate(items))
    return f'<div class="col" style="grid-column:span {span}">\n{inner}\n</div>'

tt, tdoc = widget(PLAN['title']['match'], stretch=False)
bt = PLAN['bottom']
btitle, bdoc = widget(bt['match'], stretch=True)
title_cell = (f'<div class="cell trow" style="--nh:{PLAN["title"]["nh"]}px">'
              f'<iframe title="{html.escape(tt)}" srcdoc="{tdoc}" scrolling="no"></iframe></div>')
bottom_cell = (f'<div class="cell brow" style="--nh:{bt["nh"]}px">'
               f'<iframe title="{html.escape(btitle)}" srcdoc="{bdoc}" scrolling="no"></iframe></div>')

page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>智者大陈 · 大数据看板</title>
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{background:radial-gradient(1200px 700px at 50% -10%, #0d1f4c 0%, #060d24 55%, #04081a 100%);min-height:100vh;padding:14px;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}}
  .wrap{{max-width:1440px;margin:0 auto;display:flex;flex-direction:column;gap:{GAP}px}}
  .grid{{display:grid;grid-template-columns:repeat(12,1fr);gap:{GAP}px;align-items:stretch}}
  .col{{display:flex;flex-direction:column;gap:{GAP}px;min-width:0}}
  .cell{{position:relative;min-width:0}}
  .cell iframe{{width:100%;height:100%;border:0;display:block;background:transparent}}
  .trow{{height:{PLAN['title']['nh']}px}}
  .brow{{height:{bt['nh'] + 8}px}}
  .foot{{text-align:center;font-size:10px;color:rgba(150,190,230,.45)}}
  @media (max-width:860px){{
    .grid{{display:flex;flex-direction:column}}
    .cell{{height:auto!important;flex:none!important}}
    .cell iframe{{height:calc(var(--nh) * 1.25 + 24px)}}
    .trow iframe{{height:110px}}
  }}
</style>
</head>
<body>
<div class="wrap">
{title_cell}
<main class="grid">
{column('left', 3)}
{column('center', 6)}
{column('right', 3)}
</main>
{bottom_cell}
<p class="foot">智者大陈 · 三平台运营大数据看板 · 统计周期 {html.escape(period)} · 静态快照,无密钥无接口</p>
</div>
</body>
</html>
'''
OUT.write_text(page)
print(f'wrote {OUT} ({len(page)} bytes)')
