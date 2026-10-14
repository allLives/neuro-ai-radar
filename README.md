# NEURO//AI — Research Radar

面向神经科学 × AI 的论文周报站点，包含 2026 年第 41 周的 25 篇论文与研究追问，并可通过 GitHub Actions 在每周一自动收录新论文、生成可搜索的归档、自动发布 GitHub Pages。

## 预览

直接双击 `index.html`，支持离线浏览。页面不会暴露任何 API 密钥。

## 发布为公开网站（GitHub Pages）

1. 登录 GitHub，新建一个**公开仓库**，建议命名 `neuro-ai-radar`，默认分支选择 **main**。
2. 将本目录**全部文件**上传到该仓库（不必上传 `dist/`，包含隐藏目录 `.github/workflows/weekly.yml`，以及 `assets/`, `data/`, `scripts/`）。可通过 Git 命令进行：

   ```bash
   cd neuro-ai-radar
   git init
   git add .
   git commit -m "Launch NeuroAI Radar"
   git branch -M main
   git remote add origin https://github.com/allLives/neuro-ai-radar.git
   git push -u origin main
   ```
3. 进入仓库 `Settings → Pages → Build and deployment → Source`，选择 **GitHub Actions**。
4. `Actions` 中找到 **Weekly NeuroAI Digest**，点击 **Run workflow** 手动部署一次；也可以在仓库首次推送后检查是否自动启动。发布链接一般为 `https://allLives.github.io/neuro-ai-radar/`。
5. **要启用中文 AI 论文解读**，在 `Settings → Secrets and variables → Actions → New repository secret` 添加 `OPENAI_API_KEY`（你的 OpenAI 平台 API Key）。默认模型 `gpt-4o-mini`，可以在仓库 Variables 或 Secrets 添加 `OPENAI_MODEL` 更换模型（Variables 优先）；所选模型须支持 Chat Completions 的 JSON mode。**ChatGPT 订阅不包含 API 调用额度**，API 会产生独立费用。未经配置时，自动更新仍可尝试收录论文，但只能显示英文摘要摘录和主题索引，不会生成中文研究分析。
6. 可选：OpenAlex 注册免费 API key，配置 `OPENALEX_API_KEY`，有助于提高请求额度；未配置也可以使用小规模匿名查询。

> **注意：** GitHub Actions 定时触发可能延迟或偶发漏跑；公开仓库 60 天没有任何活动时，其定时工作流可能自动停止。建议偶尔检查 Actions 运行记录。系统保留 `workflow_dispatch` 供手动补跑。

## 每周自动流程

- 北京时间**每周一 08:23**，GitHub Actions 自动运行（cron `23 0 * * 1` UTC）。
- 检索**上一个完整的周一至周日**，避免混入正在进行的本周论文。
- 从 OpenAlex、arXiv、Europe PMC 检索期刊、预印本、会议论文与生物医学文献；按文献**发表/公开日、标题、链接、作者、出处**筛选，去重并给出研究关联度排序。
- 正式刊物需有重点来源或索引收录证据，预印本限 arXiv / bioRxiv / medRxiv / Research Square；未知状态的仓库上传材料不自动入选。主题相关性先过门槛，再参考来源质量排序，限制单一主题最多 6 篇；仅有关键词不能证明研究质量。
- 按 DOI、规范化标题和 arXiv ID 跨来源/历史去重，优先保留明确发表状态及完整摘要；保留 DOI、原始摘要、来源 ID、日期依据和各 API 成败记录。
- 默认每期最多 25 篇；如果可核对元数据的论文少于 5 篇，则本次更新失败且**保留旧站点和所有历史周报**，绝不会填充虚构文章。
- 可选：调用配置的 OpenAI API，**仅根据公开摘要**生成中文概览、研究追问和 3–5 个实验构想。**不会声称 AI 已阅读全文**；论文原始标题、链接、日期、来源等元数据禁止由语言模型改写。
- 自动生成新周报采用不可覆盖的原子写入，索引更新失败回滚；移除强制覆盖开关，种子脚本也拒绝覆盖已有归档。生成 `data/weeks/YYYY-Www.json`，更新 `data/index.json`，生成支持离线预览的 `assets/data.js`，打包为干净的 `dist/`，提交数据到仓库并部署到 Pages。

## 内容可信度

- 2026-W41 是之前聊天中整理的**人工精选试刊**，有些条目的元数据尚未全部独立复核；网页显示提示。之后的周报由程序基于公开学术索引收录，文献日期以索引给出的日期为准，不保证捕获所有上线后更新或预印本版本。
- 期刊与会议识别来自索引信息；**没有明确证据证明会议接收时，不得仅因 arXiv 评论区的文字就标为已接收**。
- 所有 AI 分析都只基于题目与摘要，不能替代全文精读、核查原图和实验方法。
- 无法保证每周抓到所有重要论文。特别重要或时间敏感的论文应打开原文核实。

## 本地执行

仅使用 Python 3.10+ 标准库；不需要安装依赖。

```bash
python -m unittest discover -s tests -v  # 不联网的日期、去重、归档安全和模型降级测试
python scripts/update_digest.py          # 读取网络，生成上一个完整周报；有 OPENAI_API_KEY 才会生成中文分析
python scripts/build.py                  # 验证历史数据并生成干净的 dist/
python scripts/update_digest.py --check  # 实际 API 检索，不写入数据、不调用 OpenAI
python -m http.server 8000               # 打开 http://localhost:8000
```

执行完成后可直接打开 `index.html` 进行离线预览。

## 目录

```text
index.html                   响应式站点
assets/styles.css             样式
assets/app.js                 搜索、过滤与历史周切换
assets/data.js                自动生成的浏览数据
scripts/update_digest.py      文献检索、初筛和分析
scripts/build.py              整合历史周报，并生成 dist/ 网站部署目录
scripts/seed.py               W41 试刊数据生成（仅首次使用）
data/index.json               归档目录
data/weeks/2026-W41.json      上周文献
.github/workflows/weekly.yml  GitHub 每周自动执行和部署
```

## 数据安全

公开 GitHub Pages 站点，所有归档文章和解读对外可见。**API Key 必须写入 GitHub Actions Secrets，不要直接放入前端或数据 JSON。**

源码可按需私有化或更换发布平台。

## 手动部署、验证和补录

在 [Actions](https://github.com/allLives/neuro-ai-radar/actions/workflows/weekly.yml) 的 **Run workflow** 中选择：

- `update`（默认）：检索上一完整周；该周已归档时跳过，仍验证并部署。
- `verify`：实际检索各 API 和筛选，但不写入周报、不调用 OpenAI；日志列出来源成败和筛选结果。用于避免把“已有周报跳过”误认为实际检索验证。
- `deploy`：只测试、构建和部署当前数据。

`report_date` 可选参考日期：例如 `2026-10-05` 将补录 2026-09-28 至 2026-10-04（2026-W40）。归档日期记录实际执行日，自动更新不覆盖已有报告。上线前人工复核修正必须用明确的 Git 提交记录，并完整保留原始记录。平时留空，按北京时间计算上周范围。

构建会校验全部周报及索引，清理旧 `dist/`，仅发布首页、4 个指定前端资源、历史 JSON 与 `.nojekyll`。源码、工作流和本地配置不进入发布产物。

## 检索覆盖与失败行为

每个检索词/来源最多取 3 页，每页最多 100 条，以限制运行时间和请求费用；达到上限标为 `source_status.truncated`，因此不保证穷尽检索。arXiv 使用 UTC 首次提交日期，期刊使用数据库发表日期，不用索引日期替代。

请求遇到暂时性错误会退避重试；单一来源失败继续使用其他来源，OpenAlex 鉴权/额度错误会停止该来源的剩余请求。最终少于 5 篇时整个更新失败，无新数据提交或部署，旧站和历史保持可用。成功但部分来源失败/截断会在周报说明中标识。

未配置 `OPENAI_API_KEY`、无摘要或调用失败时，只保存真实元数据与英文摘要摘录，并显示“尚未生成 AI 解读”；保留来源摘要以便核查。AI 响应只能填写解读字段，不能改写书目信息；模型猜想及实验建议独立标识。默认 `gpt-4o-mini`，其 JSON 输出接口要求以 [OpenAI 官方文档](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=chat) 为准。

会议接收不能通过预印本评论核实；只有会议论文集元数据才显示会议发表。当前不接入会议官方接收名单，可能漏收仅有接收通知的论文。2026-W41 试刊保留原始内容及未完全复核提示，不代表自动检索的核查结果。

## 上线验证（2026-10-13）

- GitHub 仓库：[allLives/neuro-ai-radar](https://github.com/allLives/neuro-ai-radar)。Pages 来源已通过 API 设置为 GitHub Actions；仅上传 `dist/`。
- [完整文献更新运行](https://github.com/allLives/neuro-ai-radar/actions/runs/38404879407) 实际调用 OpenAlex、arXiv、Europe PMC，生成 W40、自动提交并成功部署。OpenAlex 部分请求遇到额度限制，其他来源继续完成；页数截断及来源状态保留在周报。
- W40 原始收录 25 篇，上线前进一步复核来源/相关性后保留 17 篇；完整原始版本在 `data/reviews/2026-W40-before-review.json`，此目录不进入网站发布产物。
- W41 保留原始 25 篇及 5 项追问，SHA-256 `bb469dd4516fb099e56bd9dbbea6eb5722873504bcd94b2ba7ad07b10bc9700b` 未变。
- 未配置 OpenAI API Key；新期刊只有真实英文摘要摘录和元数据，没有生成 AI 中文解读。真实 OpenAI 调用尚未验证。
- 定时工作流为 active；下一次计划运行是北京时间 2026-10-19 08:23。未来定时触发及长期 API 可用性仍需实际运行确认。

## 阅读主题

右上角 **设置 → 外观主题** 可即时切换：

- **编辑式杂志**（默认）：纸白底色、衬线标题、网格对齐的论文列表。
- **Frutiger Aero**：蓝绿自然景观、玻璃面板、高光按钮和论文卡片。

主题选择保存在当前浏览器，刷新或再次访问会保留；浏览器禁用存储时，本次访问仍能切换。更换主题保留当前周报与筛选条件。插图为本地 SVG，离线预览和 GitHub Pages 子路径均可使用。
