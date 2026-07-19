#!/usr/bin/env python3
# gen_dachenboard.py — 把 Kimi 画布导出的 dachen-dashboard-v3.json 组装成单页大数据看板。
# 每个 widget 是自包含 HTML,用 iframe(srcdoc) 按 12 列网格摆放,互不污染样式/脚本。
# 布局经内容实测重排(2026-07-19):槽位高度贴合各组件真实 scrollHeight,消除原画布的死空间/裁切。
import html
import json
import sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else '/Users/andy/Documents/kimi/workspace/dachen-dashboard-v3.json')
OUT = Path(__file__).parent / 'index.html'
ROW = 40   # 网格行高(px),槽位高 = 50h-10(含 10px gap)
GAP = 10

# 按标题前缀覆盖布局;nh = 实测内容高度(px),用于窄屏堆叠时的 iframe 高度
OVERRIDES = {
    '标题栏':  dict(x=0, y=0,  w=12, h=2,  nh=68),
    '三平台':  dict(x=0, y=2,  w=3,  h=10, nh=461),   # 原 h9 裁切 21px → h10
    '健康罗盘': dict(x=3, y=2,  w=6,  h=12, nh=620),   # 原 h14 死空间 125px → h12(留 Tab 下钻余量)
    '视频号':  dict(x=9, y=2,  w=3,  h=16, nh=761),   # 原 h21 死空间 280px → h16
    '粉丝画像': dict(x=0, y=12, w=3,  h=10, nh=460),   # 原 h12 → h10,紧贴对比板块
    '流量来源': dict(x=3, y=14, w=6,  h=6,  nh=290),   # 紧贴罗盘下方
    '策略':   dict(x=0, y=22, w=12, h=6,  nh=257),   # 原 h8 → h6,整体上提
}

def layout_for(w):
    for k, v in OVERRIDES.items():
        if w['title'].startswith(k):
            return v
    return dict(**w['placement']['layout'], nh=400)

d = json.loads(SRC.read_text())
period = d['dataSnapshot']['period']
cells = []
for w in sorted(d['widgets'], key=lambda w: (layout_for(w)['y'], layout_for(w)['x'])):
    L = layout_for(w)
    doc = html.escape(w['files']['index.html'], quote=True)
    cells.append(
        f'<div class="cell" style="grid-column:{L["x"]+1}/span {L["w"]};grid-row:{L["y"]+1}/span {L["h"]};--nh:{L["nh"]}px;">'
        f'<iframe title="{html.escape(w["title"])}" srcdoc="{doc}" loading="lazy" scrolling="no"></iframe></div>'
    )

page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>智者大陈 · 大数据看板</title>
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{background:radial-gradient(1200px 700px at 50% -10%, #0d1f4c 0%, #060d24 55%, #04081a 100%);min-height:100vh;padding:14px;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}}
  .board{{display:grid;grid-template-columns:repeat(12,1fr);grid-auto-rows:{ROW}px;gap:{GAP}px;max-width:1440px;margin:0 auto}}
  .cell{{position:relative;min-width:0}}
  .cell iframe{{width:100%;height:100%;border:0;display:block;background:transparent}}
  .foot{{max-width:1440px;margin:10px auto 4px;text-align:center;font-size:10px;color:rgba(150,190,230,.45)}}
  /* 窄屏:纵向堆叠,iframe 高度按各组件实测内容高度给(窄列会回流变高,预留 1.25x) */
  @media (max-width:860px){{
    .board{{display:flex;flex-direction:column;gap:{GAP}px}}
    .cell{{width:100%}}
    .cell iframe{{height:calc(var(--nh) * 1.25 + 24px)}}
  }}
</style>
</head>
<body>
<main class="board">
{chr(10).join(cells)}
</main>
<p class="foot">智者大陈 · 三平台运营大数据看板 · 统计周期 {html.escape(period)} · 静态快照,无密钥无接口</p>
</body>
</html>
'''
OUT.write_text(page)
print(f'wrote {OUT} ({len(page)} bytes, {len(cells)} widgets)')
