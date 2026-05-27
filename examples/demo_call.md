# MCN Script Assistant 调用示例

这个示例展示如何把「轻醒」brief 输入到本地 MCN Agent demo，经过达人评分、风格拆解、脚本生成、分镜生成、合规扫描，得到可写入飞书的交付内容。

注意：这个 demo 的重点是展示工具调用方式和数据流。近期站内笔记已经通过用户本机登录态小红书做只读复核，结论见 `references/xhs_recent_verification.md`；demo 会消费复核后的结构化达人资料库。

## 1. 输入材料

- Brief：`examples/qingxing_brief.json`
- 达人资料库：`references/creator_candidates.json`
- Prompt v2：`prompts/advanced_agent_prompt.md`
- 飞书写入脚本：`feishu/write_to_feishu.py`

## 2. 本地调用

```powershell
python .\tools\mcn_agent_demo.py `
  --brief .\examples\qingxing_brief.json `
  --creators .\references\creator_candidates.json `
  --out .\examples\demo_result.md `
  --trace .\examples\demo_trace.json
```

## 3. 实现流程

1. `load_brief`：读取品牌 brief、目标人群、禁用表达。
2. `load_creator_candidates`：读取候选达人结构化资料。
3. `score_creators`：按人设、受众、场景、植入自然度、可拍性、合规安全打分。
4. `select_creator`：选择加权分最高的达人。
5. `generate_script`：基于达人结构生成标题、钩子、口播、植入点和 CTA。
6. `generate_storyboard`：输出镜头、画面、口播/字幕、拍摄备注。
7. `compliance_scan`：扫描禁用词和需要证据支撑的表达。
8. `prepare_feishu_payload`：形成飞书文档 Markdown 和多维表格 records。

## 4. 最终成果

- Demo 输出：`examples/demo_result.md`
- 流程 trace：`examples/demo_trace.json`
- 正式脚本：`output/final_script.md`
- 正式分镜：`output/storyboard.md`
- 正式质检：`output/risk_check.md`
- 飞书文档：https://pcn395m6qii3.feishu.cn/docx/LebhdCoMaoW3vGxasF2cpubPnzd
- 飞书多维表格：https://pcn395m6qii3.feishu.cn/base/A1cdbMGxVaRRU5sCB6UciR5ondh

## 5. 和真实 LLM Agent 的关系

`tools/mcn_agent_demo.py` 是可复现演示层，用确定性逻辑展示工作流和数据结构。真实使用时，把 `prompts/advanced_agent_prompt.md` 交给 LLM，并把搜索、资料库、合规扫描、飞书写入作为工具接入即可。

如果要做泛化测试，应新增一个不在当前候选列表中的近期活跃达人，重新生成 `creator_candidates.json`、`demo_result.md` 和 `demo_trace.json`，再比较最终脚本是否仍能保持自然植入。
