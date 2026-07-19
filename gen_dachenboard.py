#!/usr/bin/env python3
# gen_dachenboard.py — 把 Kimi 画布导出的 dachen-dashboard-v3.json 组装成单页大数据看板。
# 每个 widget 是自包含 HTML,用 iframe(srcdoc) 按 12 列网格摆放,互不污染样式/脚本。
import html
import json
import sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else '/Users/andy/Documents/kimi/workspace/dachen-dashboard-v3.json')
OUT = Path(__file__).parent / 'index.html'
ROW = 40  # 网格行高(px);列宽由 12 列自适应

d = json.loads(SRC.read_text())
period = d['dataSnapshot']['period']
cells = []
for w in sorted(d['widgets'], key=lambda w: (w['placement']['layout']['y'], w['placement']['layout']['x'])):
    L = w['placement']['layout']
    doc = html.escape(w['files']['index.html'], quote=True)
    cells.append(
        f'<div class="cell" style="grid-column:{L["x"]+1}/span {L["w"]};grid-row:{L["y"]+1}/span {L["h"]};">'
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
  .board{{display:grid;grid-template-columns:repeat(12,1fr);grid-auto-rows:{ROW}px;gap:10px;max-width:1440px;margin:0 auto}}
  .cell{{position:relative;min-width:0}}
  .cell iframe{{width:100%;height:100%;border:0;display:block;background:transparent}}
  .foot{{max-width:1440px;margin:10px auto 4px;text-align:center;font-size:10px;color:rgba(150,190,230,.45)}}
  @media (max-width:820px){{
    .board{{display:flex;flex-direction:column;gap:10px}}
    .cell{{width:100%}}
    .cell iframe{{height:70vh;min-height:320px}}
    .cell:first-child iframe{{height:110px;min-height:0}}
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
