# MCN_Agent

小红书达人调研 + 商单脚本生成助手。项目围绕轻食酸奶品牌「轻醒」完成达人筛选、内容风格拆解、商单短视频脚本、分镜设计、合规质检、可复用 Skill 和飞书自动写入方案。

## 交付物

- 调研与方案报告：[report.md](report.md)
- 转换后 Markdown 交付版：[output/final_delivery.md](output/final_delivery.md)
- 最终脚本：[output/final_script.md](output/final_script.md)
- 分镜设计：[output/storyboard.md](output/storyboard.md)
- 合规质检：[output/risk_check.md](output/risk_check.md)
- Prompt 与工作流：[prompts/](prompts/)
- 可复用 Skill：[skills/mcn-script-assistant/SKILL.md](skills/mcn-script-assistant/SKILL.md)
- 飞书接入脚本：[feishu/write_to_feishu.py](feishu/write_to_feishu.py)
- 端到端调用示例：[examples/demo_call.md](examples/demo_call.md)

## Brief 摘要

- 品牌：轻食酸奶「轻醒」
- 产品：0 蔗糖高蛋白希腊酸奶，原味、蓝莓、黄桃
- 卖点：高蛋白、饱腹感、低负担，适合早餐、运动后、下午茶
- 人群：22-35 岁城市女性，关注健身、控糖、轻食和上班族效率生活
- 平台：小红书短视频
- 合规边界：不承诺减肥、治疗、降糖等功效，不夸大效果，脚本需适合真实达人拍摄

## AI 工作流

1. Brief 拆解：把品牌、产品、人群、场景、禁用表达拆成结构化输入。
2. 达人筛选：从内容方向、粉丝画像、场景适配、商业自然度筛选 2-3 位候选达人。
3. 风格拆解：拆出钩子、镜头结构、口播语气、字幕表达、产品植入位置。
4. 脚本生成：输出标题、开头钩子、口播、植入点、CTA 和可拍摄分镜。
5. 风险质检：检查功效承诺、夸大表达、硬广感、拍摄可执行性。
6. 飞书写入：把最终脚本和达人调研自动写入飞书文档与多维表格。

核心 Prompt 见 [prompts/workflow_prompts.md](prompts/workflow_prompts.md)。升级版 Agent Prompt 见 [prompts/advanced_agent_prompt.md](prompts/advanced_agent_prompt.md)，增加了工具调用、结构化 JSON 输出、达人评分矩阵、合规守卫和飞书写入 payload。

## 一键示例

本仓库提供一个本地可运行 demo，用来展示“如何调用这个工具、内部如何执行、最终输出什么”。它不依赖外部 LLM，使用确定性逻辑复现完整 Agent 数据流；真实业务中可把同样的输入和输出结构交给 LLM + 工具调用。

```powershell
python .\tools\mcn_agent_demo.py `
  --brief .\examples\qingxing_brief.json `
  --creators .\references\creator_candidates.json `
  --out .\examples\demo_result.md `
  --trace .\examples\demo_trace.json
```

运行后生成：

- 示例结果：[examples/demo_result.md](examples/demo_result.md)
- 流程 trace：[examples/demo_trace.json](examples/demo_trace.json)
- 调用说明：[examples/demo_call.md](examples/demo_call.md)

Demo 实现了 8 个步骤：读取 brief、读取达人资料库、加权评分、选择达人、生成脚本、生成分镜、合规扫描、准备飞书写入 payload。

## 增强设计

为了让交付不只是“文案生成”，本项目增加了几类必要工具层：

- 结构化资料库：`references/creator_candidates.json` 把达人来源、内容方向、代表内容、风格结构和评分拆成机器可读数据。
- 达人评分矩阵：按人设适配、受众适配、场景适配、植入自然度、拍摄可执行性、合规安全加权排序。
- 合规守卫：`tools/mcn_agent_demo.py` 和 `output/risk_check.md` 都包含禁用表达与证据需求检查。
- 飞书自动化：`feishu/write_to_feishu.py` 将 Markdown 文档与 Bitable records 写入飞书，而不是手动复制。
- 可追踪过程：`examples/demo_trace.json` 记录每一步和最终选择，方便复盘与复现。

## 飞书接入

本项目使用飞书自建应用的应用身份调用 OpenAPI。所需权限：

- `bitable:app`
- `docs:document:import`
- `docx:document`
- `docx:document.block:convert`
- `drive:drive`

配置本地环境变量：

```powershell
Copy-Item .\feishu\.env.example .\.env
```

在 `.env` 中填入：

```env
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=xxxxx
FEISHU_FOLDER_TOKEN=
```

先执行 dry-run，确认将写入内容：

```powershell
python .\feishu\write_to_feishu.py --dry-run
```

实际写入飞书：

```powershell
python .\feishu\write_to_feishu.py
```

脚本会：

- 获取 `tenant_access_token`
- 创建或导入一份最终 Markdown 文档
- 创建多维表格，写入候选达人、最终选择、脚本状态和质检结论
- 输出结果到 `feishu/result.json` 和 `feishu/feishu_links.md`

> 密钥只放在本地 `.env`，不要提交到 GitHub。交付完成后建议在飞书开放平台重置一次 App Secret。

## 调研说明

小红书网页端公开访问经常受登录、反爬和地区策略影响。本项目先使用公开可访问页面、搜索结果和第三方公开引用进行初筛；随后在用户本机已登录小红书的 Chrome 中做只读复核，不进行点赞、收藏、评论、关注、私信或发布。

登录态复核后，原候选「阿浪的早餐铺」因近期本人内容不足，不再作为最终选择；正式脚本改为参考近期活跃达人「气泡苏打%」。核验路径、近期笔记和结论见 [references/xhs_recent_verification.md](references/xhs_recent_verification.md)，公开访问限制和初筛过程见 [references/xhs_research.md](references/xhs_research.md)。

## 使用的 AI 工具

- Codex：项目结构、调研整理、Prompt、Skill、脚本、分镜、合规质检和飞书脚本生成。
- 飞书开放平台：自动写入最终文档与多维表格。
- 公开搜索：查找小红书达人公开资料与可复核链接。

## 最终飞书链接

已通过 `feishu/write_to_feishu.py` 使用飞书 OpenAPI 自动写入：

- 飞书文档：https://pcn395m6qii3.feishu.cn/docx/V78bdIMy2os1iLxpzxPcDugtnpd
- 多维表格：https://pcn395m6qii3.feishu.cn/base/GvGcbAQzFap1d7s7rE1cTLpdnAM

运行结果保存在本地 `feishu/result.json` 和 `feishu/feishu_links.md`，这两个文件包含租户内资源 token，默认不提交到 GitHub。

本次曾遇到沙箱直连外网失败，随后通过本地代理 `127.0.0.1:7897` 完成写入。排查记录见 [feishu/attempt_log.md](feishu/attempt_log.md)。
