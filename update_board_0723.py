#!/usr/bin/env python3
# update_board_0723.py — 把 dachen-dashboard-v3.json 各组件数据更新到 2026-07-16~07-22 周期
# 数据源: dachen-pipeline/output/analytics/dashboard-data.json (07-23 21:30 抓取) + 抖音数据中心总览 (07-23 23:50 抓取)
import json
from datetime import datetime
from pathlib import Path

REPO = Path('/Users/andy/dachenboard-repo')
SRC = REPO / 'dachen-dashboard-v3.json'
d = json.loads(SRC.read_text())
NOW = datetime.now().strftime('%m-%d %H:%M')

def rep(html, old, new, cnt=1):
    n = html.count(old)
    assert n == cnt, f'expected {cnt}, got {n}: {old[:70]!r}'
    return html.replace(old, new)

W = {w['title'][:3]: w for w in d['widgets']}

# ============ w0 标题栏 ============
h = W['标题栏']['files']['index.html']
h = rep(h, '统计周期 2026-07-11 ~ 07-17', '统计周期 2026-07-16 ~ 07-22')
h = rep(h, '更新 07-18 13:30', f'更新 {NOW}')
W['标题栏']['files']['index.html'] = h

# ============ w1 三平台·数据对比 ============
h = W['三平台']['files']['index.html']
h = rep(h, '<span class="mt">07-11 ~ 07-17</span>', '<span class="mt">07-16 ~ 07-22</span>')
# 7日播放: 抖 50,800 / 视 163,900 / 快 331 (归一: 视=100, 抖=31.0, 快=0.2→1)
h = rep(h, '视频号 ≈ 抖音 2.3×', '视频号 ≈ 抖音 3.2×')
h = rep(h, '<div class="bf dy" data-w="43"></div>', '<div class="bf dy" data-w="31"></div>')
h = rep(h, '<span class="bv">77,900</span>', '<span class="bv">50,800</span>')
h = rep(h, '<span class="bv">180,818</span>', '<span class="bv">163,900</span>')
h = rep(h, '<div class="bf ks" data-w="3"></div>', '<div class="bf ks" data-w="1"></div>')
h = rep(h, '<span class="bv">5,325</span>', '<span class="bv">331</span>')
# 粉丝: 抖 1,059(55) / 视 1,925(100) / 快 70(3.6)
h = rep(h, '<span class="bv">1,054</span>', '<span class="bv">1,059</span>')
h = rep(h, '<span class="bv">1,921</span>', '<span class="bv">1,925</span>')
h = rep(h, 'data-w="2"></div></div><span class="bv">33</span>', 'data-w="3.6"></div></div><span class="bv">70</span>')
# 7日净增: 抖 +9 / 视 +585 / 快 +2
h = rep(h, 'data-w="2"></div></div><span class="bv">+10</span>', 'data-w="1.5"></div></div><span class="bv">+9</span>')
h = rep(h, '<span class="bv">+591</span>', '<span class="bv">+585</span>')
h = rep(h, 'data-w="1.5"></div></div><span class="bv">+7</span>', 'data-w="1"></div></div><span class="bv">+2</span>')
# 互动率: 抖 0.30%(12) / 视 1.02%(40.8) / 快 小样本
h = rep(h, '<div class="bf dy" data-w="15.6"></div>', '<div class="bf dy" data-w="12"></div>')
h = rep(h, '<span class="bv">0.39%</span>', '<span class="bv">0.30%</span>')
h = rep(h, '<div class="bf sp" data-w="37.6"></div>', '<div class="bf sp" data-w="40.8"></div>')
h = rep(h, '<span class="bv">0.94%</span>', '<span class="bv">1.02%</span>')
h = rep(h, '<span class="bv dim">≈0（0赞0评）</span>', '<span class="bv dim">6 次互动 · 小样本</span>')
h = rep(h, '<b>读法</b>：前三组按组内最大值归一（组间不可比）；互动率为绝对刻度并标 2% 健康线——三平台均未过线，抖音差约 5×，是最大短板。',
        '<b>读法</b>：前三组按组内最大值归一（组间不可比）；互动率为绝对刻度并标 2% 健康线——抖音 0.30%、视频号 1.02% 均未过线；快手仅 5赞1评，样本太小不参与对比。')
W['三平台']['files']['index.html'] = h

# ============ w2 健康罗盘 ============
h = W['健康罗']['files']['index.html']
h = rep(h, '<div class="datebar"><span id="dateRange">统计周期 2026-07-11 ~ 07-17</span></div>',
        '<div class="datebar"><span id="dateRange">统计周期 2026-07-16 ~ 07-22</span></div>')
h = rep(h, '<span class="gformula" id="gFormula">（58+45+60）/ 3 = 54</span>',
        '<span class="gformula" id="gFormula">（52+50+40）/ 3 = 47</span>')
i0 = h.index('  var DATA = {')
i1 = h.index('\n  };', i0) + len('\n  };')
NEW_DATA = '''  var DATA = {
    overview: { health: 47, glab: "综合健康分 · 三平台均值", formula: "（52+50+40）/ 3 = 47",
      left: [["抖音 · 粉丝","1,059"],["视频号 · 关注","1,925"],["快手 · 粉丝","70"]],
      right: [["5s完播率 · 抖","40.46%"],["2s跳出率 · 短板","34.92%","warn"],["互动率 · 视","1.02%"]],
      dlab: "7日总播放 · 三平台", digits: "215031", dsub: "合计粉丝 3,054 · <b>净增 +596</b> · 投稿 30 条",
      diag: [["策略 · 两平台分治","视频号按中老年男性盘定制（怀旧/纪录/稳重口吻）；抖音流量款挂 AI/经营角度纠偏受众；快手保持同步分发、暂不作主战场。","g"],
             ["新风险 · 审核","07-23 新片「不要再去学AI」三平台集体下架（疑炒股台词触发金融内容审核）——脚本先过敏感词，理财承诺类表述一律不写。",""]] },
    douyin: { health: 52, glab: "平台健康分 · 抖音", formula: "粉丝 1,059 · 7日 +9",
      left: [["粉丝","1,059"],["7日播放","50,800"],["7日投稿","11 条"]],
      right: [["5s完播率","40.46%"],["2s跳出率","34.92%","warn"],["互动指数","0.30%","bad"]],
      dlab: "7日播放 · 抖音", digits: "50800", dsub: "净增 <b>+9</b> · 条均时长 9.39s",
      diag: [["根因","热点退潮：TOP 片 7,479 → 最新 542/284，播放环比 -35%；泛娱乐受众 70%（二次元27/随拍22/游戏21）与「中小企业老板」目标错配未解。",""],
             ["杠杆","流量款必挂 AI/经营视角纠偏标签；前 3 秒强钩子压 2 秒跳出；热点借势不丢老板人设。","g"]] },
    shipinhao: { health: 50, glab: "平台健康分 · 视频号", formula: "关注 1,925 · 7日 +585",
      left: [["关注者","1,925"],["7日播放","163,900"],["7日赞/评","737/934"]],
      right: [["互动率 · 北极星","1.02%","warn"],["推荐流量占比","77%"],["40+占比","91.7%","gd"]],
      dlab: "7日播放 · 视频号", digits: "163900", dsub: "净增 <b>+585</b> · ≈ 抖音 3.2×",
      diag: [["根因","爆款断层：上期单条 13.5 万，本期 TOP1 仅 3,017；但基本盘稳——净增 +585、互动率 1.02% 微升。",""],
             ["杠杆","怀旧/历史纪录母题继续跑量；CTA 改稳重问句冲互动率 0.5%；广东 TOP1 地域可试粤味案例。","g"]] },
    kuaishou: { health: 40, glab: "平台健康分 · 快手", formula: "粉丝 70 · 播放崩塌",
      left: [["粉丝","70"],["7日播放","331"],["7日完播","5.9%"]],
      right: [["播放分位","90 分位","gd"],["7日互动","5赞1评"],["播放环比","-94%","bad"]],
      dlab: "7日播放 · 快手", digits: "331", dsub: "净增 <b>+2</b> · 互动 6 次",
      diag: [["根因","播放 5,325 → 331 崩塌，冷启动未过；精选/发现页仍有分发但承接不住，0 转发。",""],
             ["杠杆","钩子+中段兑现双段重做；定位降为同步分发渠道，不投入单独创作资源。","g"]] }
  };'''
h = h[:i0] + NEW_DATA + h[i1:]
W['健康罗']['files']['index.html'] = h

# ============ w3 视频号·TOP榜 ============
h = W['视频号']['files']['index.html']
h = rep(h, '<span class="tv2">180,818 <small>▲ +591 关注</small></span>', '<span class="tv2">163,900 <small>▲ +585 关注</small></span>')
h = rep(h, '<span class="tv2">77,900 <small>▲ +10 粉丝</small></span>', '<span class="tv2">50,800 <small>▲ +9 粉丝</small></span>')
import math
TOP = 3017
items = [
    ('十年了，还是这座球场。2016年美洲…', 3017, 1, 0, 2, '07-18', 'r1', True),
    ('冠军和公司，是一个道理。西班牙这五座…', 2662, 4, 1, 3, '07-21', 'r2', False),
    ('这事是真的。2007年那本巴萨慈善日…', 2526, 1, 3, 2, '07-16', 'r3', False),
    ('凌晨3点，梅西撞上一条魔咒。2008…', 1637, 1, 0, 4, '07-19', '', False),
    ('凌晨3点，魔咒又赢了。常规时间0比0…', 927, 0, 0, 3, '07-20', '', False),
    ('周日凌晨5点，季军赛法国对英格兰先开…', 701, 0, 0, 0, '07-17', '', False),
    ('一百条内容，抵不上被AI答出来的那一…', 327, 0, 0, 0, '07-21', '', False),
    ('这事我见过太多回了。一家开了几十年的…', 313, 0, 0, 0, '07-22', '', False),
]
rows = []
for rank, (t, plays, likes, comments, favs, dt, rcls, hot) in enumerate(items, 1):
    w = round(math.sqrt(plays / TOP) * 100, 1)
    item_cls = 'item hot' if hot else 'item'
    rank_cls = f'rank {rcls}' if rcls else 'rank'
    rows.append(
        f'    <div class="{item_cls}"><span class="{rank_cls}">{rank}</span><div class="ib">\n'
        f'      <p class="t" title="{t}">{t}</p>\n'
        f'      <div class="bt"><div class="bf" data-w="{w}"></div></div>\n'
        f'      <div class="stats"><span class="play">{plays:,}</span><span>赞 {likes}</span><span>评 {comments}</span><span>藏 {favs}</span><span class="dt">{dt}</span></div></div></div>')
NEW_SECTION = '  <section aria-label="视频号近7天单篇视频播放榜">\n' + '\n'.join(rows) + '\n  </section>'
s0 = h.index('  <section aria-label="视频号近7天单篇视频播放榜">')
s1 = h.index('  </section>', s0) + len('  </section>')
h = h[:s0] + NEW_SECTION + h[s1:]
h = rep(h, '<b>√ 压缩刻度</b>：条宽 = √(播放/榜首播放)，小量级名次不再消失。榜首单条占 7 日总播放 <b>74.8%</b>，TOP8 合计占 <b>87.5%</b> —— 爆款集中度极高。',
        '<b>√ 压缩刻度</b>：条宽 = √(播放/榜首播放)，小量级名次不再消失。榜首单条仅占 7 日总播放 <b>1.8%</b>，TOP8 合计 <b>7.4%</b> —— 13.5 万爆款退潮后分布扁平，亟待下一个爆款母题。')
W['视频号']['files']['index.html'] = h

# ============ w4 粉丝画像 ============
h = W['粉丝画']['files']['index.html']
h = rep(h, '<span class="mt">07-11 ~ 07-17</span>', '<span class="mt">07-16 ~ 07-22</span>')
h = rep(h, '合计 100% · 粉丝 1,054', '合计 100% · 粉丝 1,059')
h = rep(h, 'aria-label="抖音兴趣分布：二次元28、随拍22、游戏21、亲子14、剧情9、美食2、其他4"',
        'aria-label="抖音兴趣分布：二次元27、随拍22、游戏21、亲子14、剧情9、美食2、其他5"')
# donut（周长 276.5）: 27/22/21/14/9/2/5
h = rep(h, 'stroke-dasharray="77.4 276.5"', 'stroke-dasharray="74.7 276.5"')
h = rep(h, 'stroke-dasharray="60.8 276.5" stroke-dashoffset="-77.4"', 'stroke-dasharray="60.8 276.5" stroke-dashoffset="-74.7"')
h = rep(h, 'stroke-dasharray="58.1 276.5" stroke-dashoffset="-138.2"', 'stroke-dasharray="58.1 276.5" stroke-dashoffset="-135.5"')
h = rep(h, 'stroke-dasharray="38.7 276.5" stroke-dashoffset="-196.3"', 'stroke-dasharray="38.7 276.5" stroke-dashoffset="-193.6"')
h = rep(h, 'stroke-dasharray="24.9 276.5" stroke-dashoffset="-235.0"', 'stroke-dasharray="24.9 276.5" stroke-dashoffset="-232.3"')
h = rep(h, 'stroke-dasharray="5.5 276.5" stroke-dashoffset="-259.9"', 'stroke-dasharray="5.5 276.5" stroke-dashoffset="-257.2"')
h = rep(h, 'stroke-dasharray="11.1 276.5" stroke-dashoffset="-265.4"', 'stroke-dasharray="13.8 276.5" stroke-dashoffset="-262.7"')
h = rep(h, '<div class="dc"><b>72%</b><span>泛娱乐占比</span></div>', '<div class="dc"><b>70%</b><span>泛娱乐占比</span></div>')
h = rep(h, '<div><i style="background:#22d3ee"></i>二次元<b>28%</b></div>', '<div><i style="background:#22d3ee"></i>二次元<b>27%</b></div>')
h = rep(h, '<div><i style="background:#64748b"></i>其他<b>4%</b></div>', '<div><i style="background:#64748b"></i>其他<b>5%</b></div>')
# 视频号年龄/性别
h = rep(h, '<span>共 1,921 人</span>', '<span>共 1,924 人</span>')
h = rep(h, '<div class="brow"><span class="bn">40-49</span><div class="bt"><div class="bf sp" data-w="20.2"></div></div><span class="bv">15.4%</span></div>',
        '<div class="brow"><span class="bn">40-49</span><div class="bt"><div class="bf sp" data-w="20"></div></div><span class="bv">15.3%</span></div>')
h = rep(h, 'aria-label="视频号性别：男65.4，女33.2"', 'aria-label="视频号性别：男65.3，女33.3"')
h = rep(h, '<div class="m" style="width:65.4%"></div><div class="f" style="width:33.2%"></div>',
        '<div class="m" style="width:65.3%"></div><div class="f" style="width:33.3%"></div>')
h = rep(h, '<span>男 65.4%</span><span>女 33.2%</span>', '<span>男 65.3%</span><span>女 33.3%</span>')
h = rep(h, '<b>⚠ 受众错配：</b>抖音泛娱乐盘 ≠ 目标（中小企业老板）；视频号 40+ 男性占 91.8% —— 选题与 CTA 应按中老年男性口味定制。',
        '<b>⚠ 受众错配：</b>抖音泛娱乐盘（70%）≠ 目标（中小企业老板）；视频号 40+ 占 91.7% —— 选题与 CTA 应按中老年男性口味定制。')
W['粉丝画']['files']['index.html'] = h

# ============ w5 流量来源 ============
h = W['流量来']['files']['index.html']
h = rep(h, '<span class="mt">07-11 ~ 07-17</span>', '<span class="mt">07-16 ~ 07-22</span>')
# 视频号来源（√刻度）: 推荐125,357(100) 分享27,114(46.5) 订阅号6,947(23.5) 朋友♡2,145(13.1) 其他985(8.9) 主页569(6.7)
h = rep(h, '<span class="vval">139,225</span>', '<span class="vval">125,357</span>')
h = rep(h, '<span class="vval">29,012</span><div class="vbar" data-h="45.6"></div>', '<span class="vval">27,114</span><div class="vbar" data-h="46.5"></div>')
h = rep(h, '<span class="vval">7,643</span><div class="vbar" data-h="23.4"></div>', '<span class="vval">6,947</span><div class="vbar" data-h="23.5"></div>')
h = rep(h, '<span class="vval">2,614</span><div class="vbar" data-h="13.7"></div>', '<span class="vval">2,145</span><div class="vbar" data-h="13.1"></div>')
h = rep(h, '<span class="vval">890</span><div class="vbar" data-h="7.7"></div>', '<span class="vval">985</span><div class="vbar" data-h="8.9"></div>')
h = rep(h, '<span class="vval">579</span><div class="vbar" data-h="6.4"></div>', '<span class="vval">569</span><div class="vbar" data-h="6.7"></div>')
# 母题反差: 避坑 8条 均5,524 vs GEO获客 4条 均614 → 9.0×
h = rep(h, '<div class="sec-t"><b>母题 · 均播放</b><span>反差 37.8×</span></div>', '<div class="sec-t"><b>母题 · 均播放</b><span>反差 9.0×</span></div>')
h = rep(h, '<span class="vval" style="color:#22d3ee">4,767</span>', '<span class="vval" style="color:#22d3ee">5,524</span>')
h = rep(h, '<span class="vval" style="color:#f87171">126</span><div class="dbar b" data-h="4"></div>', '<span class="vval" style="color:#f87171">614</span><div class="dbar b" data-h="11"></div>')
h = rep(h, '<span>避坑 · 57条</span><span>GEO获客 · 11条</span>', '<span>避坑 · 8条</span><span>GEO获客 · 4条</span>')
h = rep(h, '避坑条均评论 0.95，GEO 获客 <b>0 评论</b>——商业目标内容被世界杯流量款挤到边缘，亟待回插止血。',
        '避坑条均评论 1.8，GEO 获客 <b>0 评论</b>——均播放差从 37.8× 收窄到 9.0×，但商业内容互动仍为零。')
W['流量来']['files']['index.html'] = h

# ============ w6 策略·风险·下一条 ============
h = W['策略 ']['files']['index.html']
h = rep(h, '<span class="mt">画像洞察版 · 复盘 07-18</span>', '<span class="mt">画像洞察版 · 复盘 07-23</span>')
NEW_STRATEGY = '''  <section class="strategy" aria-label="一句话策略">
    <span class="st">策略</span>
    <p><b>两平台分治</b>：视频号按中老年男性盘定制（怀旧 / 历史纪录 / 稳重口吻，冲互动率 0.5%），抖音流量款必挂 AI/经营角度纠偏受众，快手降为同步分发渠道、不投单独创作资源。</p>
    <span class="conf">信心 75</span>
  </section>'''
s0 = h.index('  <section class="strategy"')
s1 = h.index('  </section>', s0) + len('  </section>')
h = h[:s0] + NEW_STRATEGY + h[s1:]
NEW_CARDS = '''  <section class="cards" aria-label="核心风险与行动">
    <article class="card">
      <div class="ck"><span class="ico">!</span><div><div class="ct">新片三平台下架</div><div class="cv">最高优先级</div></div></div>
      <p>07-23 新片「不要再去学AI」<b>抖音/视频号/快手集体消失</b>（疑炒股台词触金融内容审核）——脚本先过敏感词库，理财承诺类表述一律不写，再补发重剪版。</p>
    </article>
    <article class="card">
      <div class="ck"><span class="ico">×</span><div><div class="ct">爆款断层</div><div class="cv">视频号主场告急</div></div></div>
      <p>上期 13.5 万爆款退潮，本期 TOP1 仅 <b>3,017</b>；基本盘尚稳（净增 +585、互动率 1.02%）——怀旧/纪录母题需立刻续上第二个爆款。</p>
    </article>
    <article class="card">
      <div class="ck"><span class="ico">↯</span><div><div class="ct">受众错配未解</div><div class="cv">商业内容边缘化</div></div></div>
      <p>抖音泛娱乐受众仍占 70%；GEO 获客款均播放 614、<b>0 评论</b>——流量款必须挂 AI/经营钩子，把泛流量往老板向筛。</p>
    </article>
    <article class="card next">
      <div class="ck"><span class="ico">→</span><div><div class="ct">下一条 · 落地稿</div><div class="cv">热点借势（流量款）</div></div></div>
      <p>按指令走「热点借势」+ 互动型 CTA（站队/押注式）；前 3 秒强钩子压 2 秒跳出，标题避开近 10 条已发母题。</p>
      <div class="tagrow"><span class="tag">领取物：老板AI获客5步清单</span><span class="tag">KPI：视频号互动率→0.5% / 每周加微数</span></div>
    </article>
  </section>'''
s0 = h.index('  <section class="cards"')
s1 = h.index('  </section>', s0) + len('  </section>')
h = h[:s0] + NEW_CARDS + h[s1:]
W['策略 ']['files']['index.html'] = h

# ============ dataSnapshot ============
d['dataSnapshot'] = {
    'source': 'https://andychenfromchina.github.io/dachen-dashboard/',
    'period': '2026-07-16 ~ 2026-07-22',
    'platforms': {
        'douyin':    {'name': '抖音',   'color': '#25d6e6', 'fans': 1059, 'plays': 50800,  'health': 52},
        'shipinhao': {'name': '视频号', 'color': '#a855f7', 'fans': 1925, 'plays': 163900, 'health': 50},
        'kuaishou':  {'name': '快手',   'color': '#fb923c', 'fans': 70,   'plays': 331,    'health': 40},
    },
    'totals': {'fans': 3054, 'plays': 215031, 'health': 47},
    'notes': '数据为静态页烘焙快照，无 JSON API；综合健康 47 = (52+50+40)/3。本期事件：07-23 新片「不要再去学AI」三平台集体下架（疑金融内容审核）。数据源：三平台创作者后台 07-23 晚抓取。'
}

SRC.write_text(json.dumps(d, ensure_ascii=False, indent=2))
print('v3.json updated OK,', SRC.stat().st_size, 'bytes; 更新时点', NOW)
