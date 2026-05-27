#!/usr/bin/env python3
"""Write MCN handoff content to Feishu Docs and Bitable.

The script uses only Python stdlib so reviewers can run it without installing
dependencies. Dry-run is the default verification path for local checks; live
mode calls Feishu OpenAPI with tenant_access_token.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FEISHU_DIR = ROOT / "feishu"
OUTPUT_DIR = ROOT / "output"
REPORT = ROOT / "report.md"
FINAL_DELIVERY = OUTPUT_DIR / "final_delivery.md"
CREATOR_CANDIDATES = ROOT / "references" / "creator_candidates.json"
API_BASE = "https://open.feishu.cn/open-apis"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def build_document_text() -> str:
    return read_text(FINAL_DELIVERY) + "\n"


def build_bitable_records() -> list[dict[str, Any]]:
    candidates = json.loads(CREATOR_CANDIDATES.read_text(encoding="utf-8"))
    selected_name = max(candidates, key=creator_score)["creator_name"]
    records = []
    for creator in candidates:
        is_selected = creator["creator_name"] == selected_name
        representative = "、".join(creator.get("representative_content", [])[:2])
        compliance = int(creator.get("scores", {}).get("compliance_safety", 0))
        records.append(
            {
                "达人昵称": creator["creator_name"],
                "内容方向": creator.get("content_direction", ""),
                "选择状态": "最终选择" if is_selected else "候选",
                "匹配理由": (
                    f"{creator.get('style_pattern', '')}；"
                    f"代表内容：{representative or '见调研报告'}。"
                ),
                "风险状态": "低" if compliance >= 4 else "中",
                "输出文件": "output/final_script.md" if is_selected else "references/xhs_research.md",
            }
        )
    return records


def creator_score(creator: dict[str, Any]) -> float:
    weights = {
        "persona_fit": 0.2,
        "audience_fit": 0.18,
        "scene_fit": 0.2,
        "natural_insertion": 0.2,
        "execution_feasibility": 0.12,
        "compliance_safety": 0.1,
    }
    scores = creator.get("scores", {})
    return sum(float(scores.get(key, 0)) * weight for key, weight in weights.items())


def request_json(method: str, path: str, token: str | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        API_BASE + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Feishu HTTP {exc.code} {path}: {detail}") from exc


def tenant_token() -> str:
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    if not app_id or not app_secret:
        raise RuntimeError("Missing FEISHU_APP_ID or FEISHU_APP_SECRET. Fill .env first.")
    resp = request_json(
        "POST",
        "/auth/v3/tenant_access_token/internal/",
        payload={"app_id": app_id, "app_secret": app_secret},
    )
    if resp.get("code") != 0:
        raise RuntimeError(f"Failed to get tenant_access_token: {resp}")
    return str(resp["tenant_access_token"])


def create_docx(token: str, markdown: str) -> dict[str, Any]:
    title = f"轻醒酸奶商单脚本交付-{time.strftime('%Y%m%d-%H%M')}"
    payload: dict[str, Any] = {"title": title}
    folder_token = os.environ.get("FEISHU_FOLDER_TOKEN")
    if folder_token:
        payload["folder_token"] = folder_token

    created = request_json("POST", "/docx/v1/documents", token, payload)
    if created.get("code") != 0:
        raise RuntimeError(f"Create docx failed: {created}")

    document = created.get("data", {}).get("document", {})
    document_id = document.get("document_id") or created.get("data", {}).get("document_id")
    if not document_id:
        raise RuntimeError(f"Cannot find document_id in response: {created}")

    write_results = []
    for chunk in chunk_text(markdown, 2500):
        write_results.append(
            request_json(
                "POST",
                f"/docx/v1/documents/{document_id}/blocks/{document_id}/children?document_revision_id=-1",
                token,
                {
                    "index": -1,
                    "children": [
                        {
                            "block_type": 2,
                            "text": {"elements": [{"text_run": {"content": chunk}}]},
                        }
                    ],
                },
            )
        )
        time.sleep(0.4)
    return {"create_document": created, "write_content": write_results}


def chunk_text(text: str, limit: int) -> list[str]:
    chunks: list[str] = []
    current = ""
    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        candidate = paragraph if not current else current + "\n\n" + paragraph
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = ""
        while len(paragraph) > limit:
            chunks.append(paragraph[:limit])
            paragraph = paragraph[limit:]
        current = paragraph
    if current:
        chunks.append(current)
    return chunks


def create_bitable(token: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    app_token = os.environ.get("FEISHU_BITABLE_APP_TOKEN")
    table_id = os.environ.get("FEISHU_TABLE_ID")

    if not app_token:
        app_payload: dict[str, Any] = {
            "name": f"轻醒达人调研-{time.strftime('%Y%m%d-%H%M')}",
            "time_zone": "Asia/Shanghai",
        }
        folder_token = os.environ.get("FEISHU_FOLDER_TOKEN")
        if folder_token:
            app_payload["folder_token"] = folder_token
        app_resp = request_json("POST", "/bitable/v1/apps", token, app_payload)
        if app_resp.get("code") != 0:
            raise RuntimeError(f"Create bitable app failed: {app_resp}")
        app_token = app_resp.get("data", {}).get("app", {}).get("app_token") or app_resp.get("data", {}).get("app_token")
    else:
        app_resp = {"code": 0, "msg": "reuse existing app"}

    if not table_id:
        table_resp = request_json(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables",
            token,
            {
                "table": {
                    "name": "达人调研",
                    "default_view_name": "表格",
                    "fields": [
                        {"field_name": "达人昵称", "type": 1},
                        {"field_name": "内容方向", "type": 1},
                        {"field_name": "选择状态", "type": 3, "property": {"options": [{"name": "候选"}, {"name": "最终选择"}]}},
                        {"field_name": "匹配理由", "type": 1},
                        {"field_name": "风险状态", "type": 3, "property": {"options": [{"name": "低"}, {"name": "中"}, {"name": "高"}]}},
                        {"field_name": "输出文件", "type": 1},
                    ],
                }
            },
        )
        if table_resp.get("code") != 0:
            raise RuntimeError(f"Create bitable table failed: {table_resp}")
        table_id = table_resp.get("data", {}).get("table_id") or table_resp.get("data", {}).get("table", {}).get("table_id")
    else:
        table_resp = {"code": 0, "msg": "reuse existing table"}

    record_resp = request_json(
        "POST",
        f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
        token,
        {"records": [{"fields": row} for row in records]},
    )
    return {"app": app_resp, "table": table_resp, "records": record_resp, "app_token": app_token, "table_id": table_id}


def write_outputs(result: dict[str, Any], markdown: str) -> None:
    FEISHU_DIR.mkdir(exist_ok=True)
    (FEISHU_DIR / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    bitable_url = (
        result.get("bitable", {})
        .get("app", {})
        .get("data", {})
        .get("app", {})
        .get("url")
    )
    document_id = (
        result.get("docx", {})
        .get("create_document", {})
        .get("data", {})
        .get("document", {})
        .get("document_id")
    )
    tenant_host = ""
    if isinstance(bitable_url, str) and "://" in bitable_url:
        tenant_host = bitable_url.split("/base/", 1)[0]
    doc_url = f"{tenant_host}/docx/{document_id}" if tenant_host and document_id else ""
    doc_line = f"- 飞书文档：{doc_url or '请查看 result.json 中的 document_id 字段'}"
    bitable_line = f"- 多维表格：{bitable_url or '请查看 result.json 中的 app_token / table_id 字段'}"
    (FEISHU_DIR / "feishu_links.md").write_text(
        "# 飞书写入结果\n\n" + doc_line + "\n" + bitable_line + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (FEISHU_DIR / "dry_run_document.md").write_text(markdown, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Build payloads without calling Feishu OpenAPI.")
    args = parser.parse_args()

    load_env(ROOT / ".env")
    markdown = build_document_text()
    records = build_bitable_records()

    if args.dry_run:
        result = {"dry_run": True, "document_chars": len(markdown), "records": records}
        write_outputs(result, markdown)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    token = tenant_token()
    result = {
        "dry_run": False,
        "docx": create_docx(token, markdown),
        "bitable": create_bitable(token, records),
    }
    write_outputs(result, markdown)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
