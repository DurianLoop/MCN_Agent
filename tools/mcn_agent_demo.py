#!/usr/bin/env python3
"""Deterministic demo for the MCN script assistant workflow.

This is not a replacement for an LLM. It demonstrates the tool interface,
data flow, scoring, compliance gate, and final handoff shape reviewers should
expect from the AI workflow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCORE_WEIGHTS = {
    "persona_fit": 0.18,
    "audience_fit": 0.18,
    "scene_fit": 0.22,
    "natural_insertion": 0.20,
    "execution_feasibility": 0.12,
    "compliance_safety": 0.10,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def weighted_score(candidate: dict[str, Any]) -> float:
    scores = candidate["scores"]
    return round(sum(scores[key] * weight for key, weight in SCORE_WEIGHTS.items()), 2)


def select_creator(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = sorted(
        ({**candidate, "weighted_score": weighted_score(candidate)} for candidate in candidates),
        key=lambda item: item["weighted_score"],
        reverse=True,
    )
    return ranked[0]


def compliance_scan(text: str, forbidden: list[str]) -> list[dict[str, str]]:
    findings = []
    for term in forbidden:
        if term in text:
            findings.append(
                {
                    "term": term,
                    "risk": "high",
                    "action": f"删除或改写包含“{term}”的表达，避免功效承诺。",
                }
            )
    safe_checks = [
        ("0 蔗糖", "仅作为产品属性，需以包装为准。"),
        ("高蛋白", "仅作为产品属性，需以营养成分表为准。"),
        ("饱腹感", "仅作为体验表达，不承诺时长或效果。"),
    ]
    for term, action in safe_checks:
        if term in text:
            findings.append({"term": term, "risk": "low", "action": action})
    return findings


def render_script(brief: dict[str, Any], creator: dict[str, Any]) -> str:
    brand = brief["brand"]
    product = brief["product"]
    if "气泡苏打" in creator["creator_name"]:
        return f"""标题：沉浸式蓝莓黄桃星河酸奶碗

开头 3 秒：
今天做一碗可以嚼着吃的蓝莓黄桃星河酸奶碗。

口播/字幕文案：
今天做一碗蓝莓黄桃星河酸奶碗。

先用「{brand}」原味希腊酸奶打底，质地比普通酸奶更厚一点，压开的时候会有很绵密的纹理。

这杯是 0 蔗糖高蛋白配方，拿来做酸奶碗刚好，不会一拌就变得水水的。

蓝莓口味做蓝色层，黄桃口味做一点暖色过渡，再铺上燕麦、蓝莓和黄桃丁。

下午想吃点甜的，或者运动后想补一点蛋白质，我会更愿意做这种低负担的酸奶碗。

CTA：
你们还想看什么颜色的酸奶碗？蓝莓、黄桃，还是做一个薄荷绿色？

产品植入点：
第 2 个镜头短露出「{brand}」原味包装；第 3 个镜头展示厚质地；第 4-5 个镜头用蓝莓/黄桃做颜色层。

风格依据：
参考 {creator["creator_name"]} 的“{creator["style_pattern"]}”结构，只借鉴内容结构和拍摄节奏，不照搬原文。
"""
    return f"""标题：上班日不想空腹，也不想做复杂早餐

开头 3 秒：
早上只剩 5 分钟，我会做这个酸奶燕麦碗再出门。

口播文案：
早上真的不想空腹去上班，但也不想一大早开火做饭。

我最近会把早餐做得很简单：一杯「{brand}」{product}，加一点即食燕麦，再放蓝莓和黄桃。

它是 0 蔗糖配方，蛋白质也比较高，口感比普通酸奶更厚一点，拌燕麦刚好，不会水水的。

如果早上要出门，我会直接装进杯子里，原味做基底比较百搭；想吃清爽一点就加蓝莓，想要甜香一点就加黄桃。

运动后或者下午三四点有点饿的时候，我也会拿一杯当加餐，比随手买甜饮更符合我的加餐习惯。

做法不用记：酸奶打底，燕麦铺一层，水果随便放，最后搅一搅就能吃。

CTA：
经常赶时间的话，先收藏这个搭配。下次我再整理一版不用开火的上班早餐。

产品植入点：
第 2 个镜头冰箱取出「{brand}」；第 3 个镜头展示质地；第 5 个镜头补充蓝莓/黄桃口味。

风格依据：
参考 {creator["creator_name"]} 的“{creator["style_pattern"]}”结构，只借鉴内容结构和拍摄节奏，不照搬原文。
"""


def render_storyboard() -> list[dict[str, str]]:
    return [
        {"shot": "1", "visual": "白碗里一勺原味酸奶被压开", "line": "蓝莓黄桃星河酸奶碗", "note": "沉浸式极近景"},
        {"shot": "2", "visual": "轻醒原味包装短暂入画", "line": "0 蔗糖高蛋白希腊酸奶打底", "note": "自然露出包装"},
        {"shot": "3", "visual": "勺子铺平厚质地酸奶", "line": "质地厚一点", "note": "属性表达，不说功效"},
        {"shot": "4", "visual": "蓝莓口味/蓝莓酱淋成蓝色层", "line": "蓝莓做星河蓝", "note": "颜色主题"},
        {"shot": "5", "visual": "黄桃丁形成暖色点缀", "line": "黄桃加一点暖色", "note": "带出口味"},
        {"shot": "6", "visual": "撒燕麦、坚果、蓝莓，轻压", "line": "慢慢混在一起", "note": "沉浸式压拌"},
        {"shot": "7", "visual": "勺子挖开横截面", "line": "下午茶或运动后加餐", "note": "场景表达"},
        {"shot": "8", "visual": "成品 close-up，字幕提问", "line": "想看什么颜色？", "note": "轻 CTA"},
    ]


def markdown_table(rows: list[dict[str, str]], headers: list[str]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def run(brief_path: Path, creators_path: Path, out_path: Path, trace_path: Path) -> None:
    brief = load_json(brief_path)
    candidates = load_json(creators_path)
    ranked = [{**item, "weighted_score": weighted_score(item)} for item in candidates]
    ranked.sort(key=lambda item: item["weighted_score"], reverse=True)
    selected = select_creator(candidates)
    script = render_script(brief, selected)
    storyboard = render_storyboard()
    risks = compliance_scan(script, brief["forbidden_claims"])

    markdown = [
        "# MCN Agent Demo Result",
        "## 1. 调用输入",
        f"- Brief: `{brief_path}`",
        f"- 达人资料库: `{creators_path}`",
        "## 2. 达人评分",
        markdown_table(
            [
                {
                    "达人": item["creator_name"],
                    "方向": item["content_direction"],
                    "加权分": item["weighted_score"],
                    "选择": "最终选择" if item["creator_name"] == selected["creator_name"] else "候选",
                }
                for item in ranked
            ],
            ["达人", "方向", "加权分", "选择"],
        ),
        "## 3. 最终达人",
        f"选择 **{selected['creator_name']}**，因为其近期内容、视觉风格和酸奶碗场景与轻醒酸奶的自然植入最匹配。",
        "## 4. 生成脚本",
        script,
        "## 5. 分镜",
        markdown_table(storyboard, ["shot", "visual", "line", "note"]),
        "## 6. 合规扫描",
        markdown_table(risks, ["term", "risk", "action"]),
        "## 7. 飞书写入摘要",
        "将本 Markdown 与达人评分 records 交给 `feishu/write_to_feishu.py`，由 OpenAPI 写入飞书文档和多维表格。",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n\n".join(markdown) + "\n", encoding="utf-8", newline="\n")
    trace_path.write_text(
        json.dumps(
            {
                "steps": [
                    "load_brief",
                    "load_creator_candidates",
                    "score_creators",
                    "select_creator",
                    "generate_script",
                    "generate_storyboard",
                    "compliance_scan",
                    "prepare_feishu_payload",
                ],
                "selected_creator": selected["creator_name"],
                "ranked_scores": [
                    {"creator_name": item["creator_name"], "weighted_score": item["weighted_score"]}
                    for item in ranked
                ],
                "risk_findings": risks,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", type=Path, default=Path("examples/qingxing_brief.json"))
    parser.add_argument("--creators", type=Path, default=Path("references/creator_candidates.json"))
    parser.add_argument("--out", type=Path, default=Path("examples/demo_result.md"))
    parser.add_argument("--trace", type=Path, default=Path("examples/demo_trace.json"))
    args = parser.parse_args()
    run(args.brief, args.creators, args.out, args.trace)
    print(f"Wrote {args.out}")
    print(f"Wrote {args.trace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
