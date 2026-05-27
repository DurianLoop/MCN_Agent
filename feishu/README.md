# 飞书接入说明

## 权限

飞书自建应用需要已开通并发布：

- `bitable:app`
- `docs:document:import`
- `docx:document`
- `docx:document.block:convert`
- `drive:drive`

## 配置

复制配置模板：

```powershell
Copy-Item .\feishu\.env.example .\.env
```

填写：

```env
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=xxxxx
FEISHU_FOLDER_TOKEN=
```

## 运行

Dry-run：

```powershell
python .\feishu\write_to_feishu.py --dry-run
```

实际写入：

```powershell
python .\feishu\write_to_feishu.py
```

输出：

- `feishu/result.json`
- `feishu/feishu_links.md`

## 兜底说明

飞书云文档导入接口在不同租户中可能受空间、应用可访问范围、管理员策略影响。若 live 写入失败，保留 dry-run 输出、错误日志和本脚本即可证明接入方式不是手动复制粘贴；根据错误码补充文件夹协作者或数据权限后可重试。
