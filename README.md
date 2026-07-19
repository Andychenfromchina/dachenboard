# dachenboard — 智者大陈 · 三平台运营大数据看板

V3 运营罗盘看板(赛车罗盘健康仪 / 平台 Tab 下钻 / 诚实刻度图表 / 玻璃拟态科技风)。

- 在线访问:https://andychenfromchina.github.io/dachenboard/
- 数据:抖音 / 视频号 / 快手 三平台运营指标静态快照(无密钥、无接口)
- 结构:`dachen-dashboard-v3.json`(Kimi 画布导出,7 个自包含 HTML 组件)→ `gen_dachenboard.py` 组装 12 列网格 → `index.html`
- 更新方式:替换 JSON 后运行 `python3 gen_dachenboard.py` 重新生成并推送
