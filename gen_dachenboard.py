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
    'right':  [{'match': '视频号',  'nh': 931}],
    'bottom': {'match': '策略',   'nh': 257},
}
# 注入每个组件(标题栏除外):让最外层面板撑满 iframe 高度,列底不再露出空底色
STRETCH_CSS = ('<style>html,body{height:100%!important}'
               'body{display:flex!important;flex-direction:column!important}'
               'body>:first-child{flex:1 0 auto;display:flow-root}</style>')

# ---- 构建期内容补丁(源 JSON 保持原样) ----

# TOP 榜补第 9、10 条(数据源:output/analytics/wechat-postlist.json,2026-07-19 21:30 抓取;
# √刻度条宽 = sqrt(播放/135322)×100)
TOP_EXTRA_ITEMS = '''    <div class="item"><span class="rank">9</span><div class="ib">
      <p class="t" title="凌晨3点,梅西撞上一条魔咒。2008欧…">凌晨3点，梅西撞上一条魔咒。2008欧…</p>
      <div class="bt"><div class="bf" data-w="5.2"></div></div>
      <div class="stats"><span class="play">365</span><span>赞 0</span><span>评 0</span><span>藏 0</span><span class="dt">07-19</span></div></div></div>
    <div class="item"><span class="rank">10</span><div class="ib">
      <p class="t" title="各位老板,不知道你们有没有发现一个现象:这两…">各位老板，不知道你们有没有发现一个现象…</p>
      <div class="bt"><div class="bf" data-w="4.3"></div></div>
      <div class="stats"><span class="play">254</span><span>赞 0</span><span>评 0</span><span>藏 0</span><span class="dt">07-15</span></div></div></div>
  </section>'''

# 罗盘 KPI 卡片重设计:文字居中、顶部中央光条、径向光晕(覆盖原左侧竖条样式)
SCARD_CSS = ('<style>'
             '.scard{text-align:center;padding:8px 10px 7px;border:1px solid rgba(0,229,255,.3);'
             'border-radius:9px;overflow:hidden;'
             'background:radial-gradient(62% 100% at 50% 0%,rgba(0,229,255,.12),transparent 70%),'
             'linear-gradient(180deg,rgba(0,80,170,.26),rgba(0,40,100,.10));'
             'box-shadow:inset 0 0 14px rgba(0,90,220,.10)}'
             '.scard::before{content:"";position:absolute;top:0;left:50%;transform:translateX(-50%);'
             'width:56%;height:2px;border-radius:2px;'
             'background:linear-gradient(90deg,transparent,#00e5ff,transparent);'
             'box-shadow:0 0 8px rgba(0,229,255,.8)}'
             '.scard::after{content:none}'
             '.sl{display:block;margin:2px 0 1px;letter-spacing:.06em;color:rgba(168,208,240,.78)}'
             '.sv{font-size:16px}'
             '</style>')

# 隐藏各卡片标题栏右上角的 .mt 角标(时间/刻度标示):其定位依赖宿主变量,在本页面全部与标题重叠
HIDE_MT_CSS = '<style>.hd .mt,.mt{display:none!important}</style>'

# 流量来源卡片:面板改纵向 flex、图表区 flex:1 自动长高(柱子为百分比高度,随容器铺满底部空间)
TRAFFIC_CSS = ('<style>'
               '.panel{display:flex!important;flex-direction:column!important;height:100%}'
               '.cols{flex:1;align-items:stretch}'
               '.cols>section{display:flex;flex-direction:column;min-height:0}'
               '.vchart,.duo{flex:1;height:auto;min-height:128px}'
               '.foot{margin-top:auto;padding-top:8px;font-size:9px}'
               '.vval{font-size:9px}.vcats span,.dcats span{font-size:9px}'
               '</style>')

# 兜底落位脚本(注入所有组件):渲染时间线被节流时,width/height 过渡可能永远到不了终点
# (2026-07-20 实翻:柱条集体停在 min-width 2px)。1.6s 后强制去过渡、直接定格最终尺寸;
# 流量柱在 flex 容器里百分比基准失效,按容器实高换算 px。
SETTLE_JS = ('<script>setTimeout(function(){'
             'document.querySelectorAll("[data-w]").forEach(function(el){'
             'el.style.transition="none";el.style.width=parseFloat(el.dataset.w)+"%";});'
             'document.querySelectorAll(".vchart,.duo").forEach(function(ch){var H=ch.clientHeight;'
             'ch.querySelectorAll("[data-h]").forEach(function(el){'
             'var lab=el.parentElement.querySelector(".vval");var max=H-(lab?lab.offsetHeight+8:8);'
             'el.style.transition="none";el.style.height=Math.max(2,max*parseFloat(el.dataset.h)/100)+"px";});});'
             '},1600);</script>')

# ---- 全局光线流动动效(2026-07-20,v2 性能重写) ----
# ⚠ 教训(2026-07-20 实翻):v1 用 background-position/box-shadow/filter/border-color 关键帧,
# 全是主线程重绘型动画,98 个叠加把渲染压垮——.bf 宽度过渡时间线冻结,柱条全部消失。
# v2 铁律:动画只准用 transform 和 opacity(合成器线程,零重绘);辉光一律做成静态阴影层+opacity 脉冲。
ANIM_CSS = ('<style>@media (prefers-reduced-motion:no-preference){'
            # 四角准星脉冲(opacity)
            '.cn{animation:cnP 3s ease-in-out infinite}'
            '@keyframes cnP{0%,100%{opacity:.6}50%{opacity:1}}'
            # 卡片标题栏横向扫光(transform)
            '.hd{overflow:hidden}'
            '.hd::after{content:"";position:absolute;top:0;bottom:0;left:0;width:30%;'
            'background:linear-gradient(105deg,transparent,rgba(140,225,255,.15),transparent);'
            'transform:translateX(-140%);animation:hdSweep 5.5s ease-in-out infinite;pointer-events:none}'
            '@keyframes hdSweep{0%{transform:translateX(-140%)}55%,100%{transform:translateX(440%)}}'
            # 横向进度条流光(transform;不动 .bf 的 position——absolute 定位改 relative 会让条塌陷)
            '.bf{overflow:hidden}'
            '.bf::after{content:"";position:absolute;top:0;bottom:0;left:0;width:55%;'
            'background:linear-gradient(100deg,transparent,rgba(255,255,255,.30),transparent);'
            'transform:translateX(-110%);animation:bfX 2.8s linear infinite;pointer-events:none}'
            '@keyframes bfX{0%{transform:translateX(-110%)}100%{transform:translateX(300%)}}'
            # 竖向柱体升腾流光(transform)
            '.vbar,.dbar{position:relative;overflow:hidden}'
            '.vbar::after,.dbar::after{content:"";position:absolute;left:0;right:0;bottom:0;height:45%;'
            'background:linear-gradient(0deg,transparent,rgba(255,255,255,.26),transparent);'
            'transform:translateY(120%);animation:vbY 3.2s linear infinite;pointer-events:none}'
            '@keyframes vbY{0%{transform:translateY(120%)}100%{transform:translateY(-330%)}}'
            # 玻璃 Tab / KPI 卡片斜向扫光(transform,错峰)
            '.tab,.scard{position:relative;overflow:hidden}'
            '.tab::after,.scard::after{content:"";position:absolute;top:-40%;bottom:-40%;left:0;width:24%;'
            'background:linear-gradient(90deg,transparent,rgba(180,235,255,.2),transparent);'
            'transform:translateX(-160%) skewX(-18deg);animation:sheenX 4.8s ease-in-out infinite;pointer-events:none}'
            '@keyframes sheenX{0%{transform:translateX(-160%) skewX(-18deg)}'
            '60%,100%{transform:translateX(560%) skewX(-18deg)}}'
            '.tab:nth-child(2)::after{animation-delay:.6s}.tab:nth-child(3)::after{animation-delay:1.2s}'
            '.tab:nth-child(4)::after{animation-delay:1.8s}'
            '.scard:nth-child(2)::after{animation-delay:.8s}.scard:nth-child(3)::after{animation-delay:1.6s}'
            # 翻牌数字盒霓虹呼吸:静态阴影层 + opacity 脉冲(逐位错峰)
            '.box{position:relative}'
            '.box::after{content:"";position:absolute;inset:-2px;border-radius:6px;pointer-events:none;'
            'box-shadow:0 0 12px rgba(0,229,255,.6);opacity:.15;animation:oP 2.6s ease-in-out infinite}'
            '.box:nth-child(2)::after{animation-delay:.2s}.box:nth-child(3)::after{animation-delay:.4s}'
            '.box:nth-child(4)::after{animation-delay:.6s}.box:nth-child(5)::after{animation-delay:.8s}'
            '.box:nth-child(6)::after{animation-delay:1s}'
            '@keyframes oP{0%,100%{opacity:.15}50%{opacity:1}}'
            # 罗盘表盘/健康分:静态辉光(不做 filter 动画)
            '.compass{filter:drop-shadow(0 0 8px rgba(34,211,238,.35))}'
            # 兴趣圆环:旋转高光弧(transform)
            '.donut{position:relative}'
            '.donut::after{content:"";position:absolute;inset:0;border-radius:50%;pointer-events:none;'
            'background:conic-gradient(from 0deg,transparent 0 72%,rgba(255,255,255,.28) 84%,transparent 96%);'
            '-webkit-mask:radial-gradient(circle,transparent 54%,#000 56% 90%,transparent 92%);'
            'mask:radial-gradient(circle,transparent 54%,#000 56% 90%,transparent 92%);'
            'animation:ringSpin 5.5s linear infinite}'
            '@keyframes ringSpin{to{transform:rotate(360deg)}}'
            '}</style>')

# 标题栏专属(只用 opacity):翼展光线游走、信号点错峰闪烁;标题辉光改静态
TITLE_ANIM_CSS = ('<style>@media (prefers-reduced-motion:no-preference){'
                  '.wing i{animation:wingP 3.2s ease-in-out infinite}'
                  '.wing i:nth-child(2){animation-delay:.4s}.wing i:nth-child(3){animation-delay:.8s}'
                  '@keyframes wingP{0%,100%{opacity:.45}50%{opacity:1}}'
                  '.dots i{animation:dotP 2.2s ease-in-out infinite}'
                  '.dots i:nth-child(2){animation-delay:.4s}.dots i:nth-child(3){animation-delay:.8s}'
                  '@keyframes dotP{0%,100%{opacity:.4}50%{opacity:1}}'
                  '}</style>')

def apply_patches(title, doc):
    if title.startswith('标题栏'):
        doc = doc.replace('新媒体运营数据驾驶舱', '百商AI新媒体运营飞轮', 1)
        doc = doc.replace('</head>', TITLE_ANIM_CSS + '</head>', 1)
    else:
        doc = doc.replace('</head>', HIDE_MT_CSS + ANIM_CSS + '</head>', 1)
        doc = doc.replace('</body>', SETTLE_JS + '</body>', 1)
    if title.startswith('视频号'):
        doc = doc.replace('  </section>', TOP_EXTRA_ITEMS, 1)
    if title.startswith('健康罗盘'):
        doc = doc.replace('</head>', SCARD_CSS + '</head>', 1)
    if title.startswith('流量来源'):
        doc = doc.replace('</head>', TRAFFIC_CSS + '</head>', 1)
    return doc

d = json.loads(SRC.read_text())
period = d['dataSnapshot']['period']
by_prefix = {w['title'][:3]: w for w in d['widgets']}

def widget(match, stretch=True):
    w = next(w for w in d['widgets'] if w['title'].startswith(match))
    doc = apply_patches(w['title'], w['files']['index.html'])
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
