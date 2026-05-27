---
name: mcn-script-assistant
description: Create compliant MCN influencer research, style analysis, Xiaohongshu short-video scripts, storyboards, risk checks, and Feishu-ready handoff materials from brand briefs and creator references. Use when turning a consumer brand brief into reusable达人筛选、商单脚本、分镜、Prompt 或飞书交付内容.
---

# MCN Script Assistant

## Overview

Use this skill to turn a consumer brand brief and creator references into an MCN-ready handoff:达人调研、风格拆解、自然种草脚本、分镜、合规质检和飞书写入材料.

## Inputs

Collect or infer these inputs before generating output:

- Brand brief: brand, product, claims, audience, platform, required CTA.
- Compliance boundaries: prohibited claims, regulated terms, evidence-required claims.
- Creator references: profile link or screenshot, content direction, 2-3 representative posts, visible hooks, scenes, and tone.
- Delivery target: final report, prompt/workflow, script, storyboard, Feishu document, or Bitable table.

If source access is limited, state the limitation and mark any judgement as inference. Do not invent screenshots, metrics, profile data, or recent posts.

## Workflow

1. Decompose the brief into product facts, audience pain points, content scenarios, usable claims, and banned claims.
2. Screen 2-3 creators by persona fit, audience fit, scene fit, natural product insertion, and compliance risk.
3. Choose one creator and explain the choice with persona, scene, tone, and brand fit.
4. Analyze creator style by hook type, first three seconds, shot order, captions, pacing, and CTA.
5. Generate one script with title, opening hook,口播文案, product insertion point, ending CTA, and shooting notes.
6. Produce a storyboard with shot, image,口播/字幕, product exposure, and拍摄备注.
7. Run a risk check and rewrite any risky line before final handoff.
8. Package final content as Markdown and structured records for Feishu.

## Output Format

For full handoff, output these sections:

```markdown
# MCN 商单脚本交付

## Brief 拆解
## 达人候选与筛选
## 最终达人选择理由
## 参考内容拆解
## 最终短视频脚本
## 分镜表
## 合规质检
## 飞书写入字段
```

Use this Bitable record shape:

```json
{
  "creator_name": "",
  "profile_or_source": "",
  "content_direction": "",
  "fit_score": "",
  "selection_status": "",
  "reason": "",
  "risk_status": "",
  "output_file": ""
}
```

## Risk Checklist

Reject or rewrite content that:

- Promises weight loss, treatment, blood sugar control, fat loss, or body-shape change.
- Uses absolute claims such as best, guaranteed, zero burden, no side effects, everyone can eat.
- Implies the product replaces meals unless the brief and evidence explicitly support it.
- Overstates protein, satiety, low sugar, or health benefits beyond packaging facts.
- Copies creator wording too closely instead of borrowing structure and rhythm.
- Creates a scene the creator could not realistically shoot.
- Hides sponsorship in a way that would make compliance review difficult.

Prefer safe expressions:

- Product fact: "0 蔗糖配方", "高蛋白", "希腊酸奶".
- Experience: "口感更厚", "有饱腹感", "适合早餐/运动后/下午茶".
- Lifestyle: "上班日更省事", "不用开火", "搭配燕麦和水果".

## Feishu Handoff

Prepare both:

- Markdown document: brief, creator choice, script, storyboard, risk result.
- Bitable records: one row per creator plus one row for final script status.

Never include API keys, app secrets, cookies, private screenshots, or unpublished creator data in the final handoff.
