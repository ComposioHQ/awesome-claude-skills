#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dandelion 商业链路诊断打分计算器（严格版）| Scoring calculator (strict).

用法 Usage:
    python scoring.py <scores.json> [--json]

输入 JSON 格式 Input JSON schema:
{
  "product": "可选 optional",
  "mode": "selfcheck | inspection 可选 optional",
  "ownership": "own | other 可选 optional",
  "evidence": {            # 可选 optional: "strong" | "weak" | "none"（兼容 verified/partial）
    "acquisition": "none"
  },
  "scores": {
    "market_research": 7,
    "real_demand": 8,
    "value_proposition": 7,
    "acquisition": 4,
    "paid_conversion": 5,
    "delivery": 6,
    "retention_referral": 2
  }
}

深度封顶 Depth caps（与 references/framework.md 一致；evidence 字段含义 = 定义深度与核对强度 definition depth & cross-checking strength）:
- strong/verified：深度对齐 + 已外部核对，不封顶 no cap，可评 7-10
- weak/partial：定义清晰但未核对，最高 6 分 cap at 6
- none：模糊/未对齐，最高 3 分 cap at 3（未标注 evidence 的环节按 none 处理 stages without evidence default to none）

规则 Rules:
- market_research 的 evidence 含义: strong=已联网/填表完成调研且证据充分; weak=已调研但证据少; none=未做调研（按深度封顶处理）
  For market_research, evidence means: strong=research done (live or agent-filled) with solid evidence; weak=research done but thin; none=no research (depth caps apply)
- 市场调研环节分建议（详见 references/framework.md）：先跑 market_research.py，环节分 = round(机器总体证据分)，再按覆盖率封顶——
  8 项指标全部有证据且与产品主张一致 → evidence=strong，可 7-10；覆盖率不足一半或未调研 → evidence=none，≤3；其余 → evidence=weak，≤6。
  Suggested market_research stage score (see references/framework.md): run market_research.py, stage = round(machine overall), then cap by coverage:
  all 8 metrics evidenced and consistent with claims → strong, 7-10; less than half covered or not researched → none, ≤3; otherwise weak, ≤6.
- 每环节 Per stage: >=7 健康 healthy, 5-6.9 薄弱 weak, <5 断裂 broken
- 链路打通 Loop Closed: 全部 >=7 且平均分 >=7.5 all stages >=7 and average >=7.5
- 接近打通 Nearly Closed: 无环节 <5 且平均分 >=7 no stage <5 and average >=7
- 未打通 Not Closed: 任一环节 <5 或平均分 <7 any stage <5 or average <7
"""

import json
import sys

__version__ = "1.2.0"

STAGES = [
    ("market_research", "市场调研 Market Research"),
    ("real_demand", "真实需求 Real Demand"),
    ("value_proposition", "价值主张 Value Proposition"),
    ("acquisition", "获客 Acquisition"),
    ("paid_conversion", "付费转化 Paid Conversion"),
    ("delivery", "交付与体验 Delivery & Experience"),
    ("retention_referral", "复购与传播 Retention & Referral"),
]

EVIDENCE_CAP = {"none": 3, "weak": 6, "partial": 6, "verified": None, "strong": None}


def main(argv):
    if len(argv) < 1 or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    path = argv[0]
    as_json = "--json" in argv[1:]

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:  # noqa: BLE001
        print("错误 Error: 无法读取 JSON cannot read JSON - %s" % e)
        return 1

    scores = data.get("scores")
    if not isinstance(scores, dict):
        scores = {k: data[k] for k, _ in STAGES if k in data}

    missing = [k for k, _ in STAGES if k not in scores]
    if missing:
        print("错误 Error: 缺少环节 missing stages: %s" % ", ".join(missing))
        return 1

    evidence = data.get("evidence") or {}
    warnings = []
    normalized = {}
    for key, label in STAGES:
        raw = scores[key]
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            print("错误 Error: %s 分数不是数字 score not numeric: %r" % (label, raw))
            return 1
        value = float(raw)
        if not (0.0 <= value <= 10.0):
            print("错误 Error: %s 分数不是有效的 0-10 数字（NaN/无穷/越界）invalid number: %r" % (label, raw))
            return 1
        ev = evidence.get(key)
        if ev not in EVIDENCE_CAP:
            ev = "none"  # 缺省视为无验证 default to none
        cap = EVIDENCE_CAP[ev]
        if cap is not None and value > cap:
            warnings.append("%s：证据档 %s，%g 分封顶为 %d (score capped)" % (label, ev, value, cap))
            value = float(cap)
        normalized[key] = value

    values = [normalized[k] for k, _ in STAGES]
    average = sum(values) / len(values)

    statuses = {}
    broken = []
    weak = []
    for i, (key, label) in enumerate(STAGES):
        v = normalized[key]
        if v < 5:
            st = "断裂 Broken"
            broken.append((key, v, i, label))
        elif v < 7:
            st = "薄弱 Weak"
            weak.append((key, v, i, label))
        else:
            st = "健康 Healthy"
        statuses[key] = {"score": v, "status": st, "label": label}

    if not broken and not weak and average >= 7.5:
        verdict_key, verdict = "loop_closed", "链路打通 Loop Closed"
    elif not broken and average >= 7:
        verdict_key, verdict = "nearly_closed", "接近打通 Nearly Closed"
    else:
        verdict_key, verdict = "not_closed", "未打通 Not Closed"

    note = "（基于公开证据 based on public evidence）" if data.get("ownership") == "other" else ""

    priority = sorted(broken, key=lambda t: (t[1], t[2])) + sorted(weak, key=lambda t: (t[1], t[2]))
    if not broken and not weak:
        priority = [(k, 0, 0, label) for k, label in STAGES if k == "retention_referral"]

    if as_json:
        out = {
            "product": data.get("product", ""),
            "mode": data.get("mode", ""),
            "ownership": data.get("ownership", ""),
            "scores": {k: normalized[k] for k, _ in STAGES},
            "average": round(average, 2),
            "verdict": verdict_key,
            "verdict_text": verdict + note,
            "statuses": statuses,
            "priority": [k for k, _, _, _ in priority],
            "warnings": warnings,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    print("=== Dandelion 商业链路诊断 Scoring Calculator (strict) ===")
    if data.get("product"):
        print("产品 Product : %s" % data["product"])
    meta = []
    if data.get("mode"):
        meta.append("模式 Mode: %s" % data["mode"])
    if data.get("ownership"):
        meta.append("归属 Ownership: %s" % data["ownership"])
    if meta:
        print(" | ".join(meta))
    print()
    print("%-30s %5s  %s" % ("环节 Stage", "分数", "状态 Status"))
    print("-" * 64)
    for key, label in STAGES:
        s = statuses[key]
        print("%-30s %5.1f  %s" % (label, s["score"], s["status"]))
    print("-" * 64)
    print("平均分 Average : %.2f" % average)
    print("结论 Verdict   : %s%s" % (verdict, note))
    if warnings:
        print()
        print("警告 Warnings（证据封顶 evidence caps applied）:")
        for w in warnings:
            print("  - %s" % w)
    print()
    print("提示 Hint：未标注 evidence 的环节一律按 none（≤3）处理；若与报告分数不符，说明 evidence 漏填。")
    print("Stages without an evidence field default to none (≤3); a mismatch with the report means the field was omitted.")
    print()
    print("行动优先级 Action priority（断裂 → 薄弱 → 增长杠杆，分低者先）:")
    if not broken and not weak:
        print("  1. %s (增长杠杆 growth lever)" % priority[0][3])
    else:
        for n, (_, v, _, label) in enumerate(priority, 1):
            tag = "断裂 Broken" if v < 5 else "薄弱 Weak"
            print("  %d. %s (%g) — %s" % (n, label, v, tag))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


