# 飞书写入尝试记录

## 已完成

- 已确认应用开通并发布以下权限：
  - `bitable:app`
  - `docs:document:import`
  - `docx:document`
  - `docx:document.block:convert`
  - `drive:drive`
- 已完成 `python .\feishu\write_to_feishu.py --dry-run`。
- dry-run 已生成文档 Markdown 和多维表格 records payload。
- 已确认真实 `App Secret` 未写入仓库文件。

## 早期环境限制

在 Codex 当前沙箱中直接访问 `open.feishu.cn` 时，命令行请求返回连接拒绝；按流程申请外网提权后，自动权限审核两次超时，未能完成 live 写入。

使用当前可用的 Lark MCP 文档导入与多维表格创建工具时，也遇到同类权限审核超时。因此本仓库保留可复现脚本和 dry-run 结果，待在有外网权限的本地环境中执行：

```powershell
python .\feishu\write_to_feishu.py
```

## 最终结果

用户提供本地代理端口 `127.0.0.1:7897` 后，已通过以下环境变量完成 live 写入：

```powershell
$env:HTTP_PROXY='http://127.0.0.1:7897'
$env:HTTPS_PROXY='http://127.0.0.1:7897'
$env:ALL_PROXY='http://127.0.0.1:7897'
python .\feishu\write_to_feishu.py
```

首次成功创建：

- 飞书文档：`https://pcn395m6qii3.feishu.cn/docx/E4ZDdDZCro2dONxO8CPcmsHLn4b`
- 多维表格：`https://pcn395m6qii3.feishu.cn/base/MmCebbXtYaxOX3scvn1c0RoQnRc`

登录态复核小红书近期内容后，最终达人由「阿浪的早餐铺」调整为「气泡苏打%」，并再次写入新版飞书：

- 飞书文档：`https://pcn395m6qii3.feishu.cn/docx/FKQndr57Oo9Do8xuy66c14KMngh`
- 多维表格：`https://pcn395m6qii3.feishu.cn/base/WS50bKM4PaQ3jAsutMZc2hEfnGb`

最终质检文案修正后，再次写入最终版：

- 飞书文档：`https://pcn395m6qii3.feishu.cn/docx/GJCBdIxeHoiKEDx1qtbcI7SHnZe`
- 多维表格：`https://pcn395m6qii3.feishu.cn/base/HadpbLwUGa1DbHsyjJmcv0Uunre`

为避免飞书正文直接显示 Markdown 的 `#` 标题和 `|` 表格符号，已将写入脚本调整为阅读版纯文本格式：标题使用分隔线和编号，候选达人、分镜、合规检查表转为分层条目。阅读版最终链接：

- 飞书文档：`https://pcn395m6qii3.feishu.cn/docx/LebhdCoMaoW3vGxasF2cpubPnzd`
- 多维表格：`https://pcn395m6qii3.feishu.cn/base/A1cdbMGxVaRRU5sCB6UciR5ondh`

按“转换后的 Markdown 交付版”要求，新增 `output/final_delivery.md`，使用 Markdown 下划线标题、重点块、分层清单和分镜条目卡片，不再使用 `#` 标题或 Markdown 表格。新版飞书链接：

- 飞书文档：`https://pcn395m6qii3.feishu.cn/docx/Vx8TdSaAxoGPnlxZ1nNcBCKVnUc`
- 多维表格：`https://pcn395m6qii3.feishu.cn/base/TuSBbiasta94GfscIcJcB72QnYe`

最终按飞书富文本块格式写入：`output/final_delivery.md` 作为源 Markdown，脚本将下划线标题解析为飞书 H1/H2，将粗体小节解析为 H3，将 `-` 列表解析为飞书无序列表块，将行内代码解析为 inline code。最终链接：

- 飞书文档：`https://pcn395m6qii3.feishu.cn/docx/V78bdIMy2os1iLxpzxPcDugtnpd`
- 多维表格：`https://pcn395m6qii3.feishu.cn/base/GvGcbAQzFap1d7s7rE1cTLpdnAM`

## 成功输出

成功后脚本会生成：

- `feishu/result.json`
- `feishu/feishu_links.md`

其中会包含新建文档和多维表格的返回信息；如飞书返回空间权限错误，补充 `FEISHU_FOLDER_TOKEN` 或将应用加入目标文件夹协作者后重试。
