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

## 当前环境限制

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

成功创建：

- 飞书文档：`https://pcn395m6qii3.feishu.cn/docx/E4ZDdDZCro2dONxO8CPcmsHLn4b`
- 多维表格：`https://pcn395m6qii3.feishu.cn/base/MmCebbXtYaxOX3scvn1c0RoQnRc`

## 成功输出

成功后脚本会生成：

- `feishu/result.json`
- `feishu/feishu_links.md`

其中会包含新建文档和多维表格的返回信息；如飞书返回空间权限错误，补充 `FEISHU_FOLDER_TOKEN` 或将应用加入目标文件夹协作者后重试。
