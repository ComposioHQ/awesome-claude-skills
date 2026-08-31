#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dandelion 单位经济学测算器 | Unit Economics Calculator

计算数字产品的单位经济学指标：毛利率、客户终身价值 LTV、LTV/CAC、回本周期。
Computes unit economics: gross margin, customer lifetime value (LTV), LTV/CAC, payback period.

用法 Usage:
    python economics.py <economics.json> [--json]
    python economics.py --interactive [--json]

输入 JSON schema (economics.json):
{
  "product": "产品名 optional",
  "price": 19.9,           # 每期价格 price per period (必填 required)
  "period": "month",       # month | year | one_time (默认 default: month)
  "unit_cost": 3.0,        # 每期变动成本 COGS per period (可选 optional, 默认 0)
  "cac": 150.0,            # 获客成本 acquisition cost per paying customer (必填 required)
  "monthly_churn": 0.05,   # 月流失率 0-1（可选；与 annual_churn 二选一）
  "annual_churn": 0.4,     # 年流失率 0-1（可选）
  "gross_margin_pct": 0.8  # 毛利率覆盖（可选；给出则忽略 unit_cost）
}

指标与判定 Metrics & verdict:
- 毛利率 Gross margin = (price - unit_cost) / price
- 客户生命周期 Customer lifetime (订阅制) = 1 / monthly_churn（月）
- LTV = 每期毛利 × 生命周期期数（订阅制）；买断制 LTV = 单笔毛利
- LTV/CAC：>=3 健康 healthy；1-3 需优化 needs work；<1 断裂信号 broken signal
- 回本周期 Payback = CAC / 每期毛利（期）
- 数据不足（缺 price 或 cac）→ 输出「数据不足 insufficient data」，不臆测。
"""

import json
import sys

__version__ = "1.2.0"

VALID_PERIODS = ("month", "year", "one_time")


def _num(value):
    """Coerce int/float/str to float; None stays None."""
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate(data):
    price = _num(data.get("price"))
    cac = _num(data.get("cac"))
    period = data.get("period", "month")
    if period not in VALID_PERIODS:
        period = "month"

    result = {"product": data.get("product", ""), "period": period}

    if price is None or price <= 0:
        result["error"] = "缺 price 价格"
        result["verdict"] = "insufficient"
        result["verdict_text"] = "数据不足 Insufficient data——不臆测，补齐 price 后再运行"
        return result
    if cac is None or cac <= 0:
        result["error"] = "缺 cac 获客成本"
        result["verdict"] = "insufficient"
        result["verdict_text"] = "数据不足 Insufficient data——不臆测，补齐 cac 后再运行"
        return result

    margin_pct = _num(data.get("gross_margin_pct"))
    if margin_pct is not None:
        margin_pct = max(0.0, min(1.0, margin_pct))
        margin = price * margin_pct
    else:
        cost = _num(data.get("unit_cost")) or 0.0
        margin = price - cost
        margin_pct = margin / price if price else 0.0
    result["gross_margin_per_unit"] = round(margin, 2)
    result["gross_margin_pct"] = round(margin_pct, 4)
    result["cac"] = round(cac, 2)

    if period == "one_time":
        result["ltv"] = round(margin, 2)
        result["payback"] = None
    else:
        monthly_churn = _num(data.get("monthly_churn"))
        if monthly_churn is None:
            annual_churn = _num(data.get("annual_churn"))
            if annual_churn is not None:
                monthly_churn = 1.0 - (1.0 - max(0.0, min(1.0, annual_churn))) ** (1.0 / 12.0)
        margin_monthly = margin if period == "month" else margin / 12.0
        if monthly_churn is not None and 0.0 < monthly_churn < 1.0:
            months = 1.0 / monthly_churn
            result["customer_lifetime_months"] = round(months, 1)
            result["ltv"] = round(margin_monthly * months, 2)
        else:
            result["ltv"] = None
            result["note"] = "缺少流失率 churn，无法计算有限 LTV；请提供 monthly_churn 或 annual_churn。"
        result["payback"] = round(cac / margin_monthly, 1) if margin_monthly > 0 else None

    ltv = result.get("ltv")
    if ltv is not None:
        ratio = ltv / cac
        result["ltv_cac"] = round(ratio, 2)
        if ratio >= 3.0:
            result["verdict"] = "healthy"
            result["verdict_text"] = "单位经济健康 Unit economics healthy（LTV/CAC >= 3）"
        elif ratio >= 1.0:
            result["verdict"] = "needs_work"
            result["verdict_text"] = "需优化 Needs work（1 <= LTV/CAC < 3）"
        else:
            result["verdict"] = "broken"
            result["verdict_text"] = "断裂信号 Broken signal（LTV/CAC < 1）：获客成本高于客户终身价值，付费转化环节按断裂处理"
    else:
        result["verdict"] = "insufficient"
        result["verdict_text"] = "数据不足 Insufficient data——不臆测，补齐 price / cac / churn 后再判"

    return result


def render_text(result):
    lines = ["=== Dandelion 单位经济学 Unit Economics ==="]
    if result.get("product"):
        lines.append("产品 Product : %s" % result["product"])
    if result.get("error"):
        lines.append("数据不足 Insufficient data : %s" % result["error"])
        lines.append("不臆测 No guessing：补齐 price 与 cac 后再运行。")
        return "\n".join(lines)
    lines.append("计费周期 Period : %s" % result["period"])
    lines.append("单期毛利 Gross margin/unit : %s（毛利率 %s%%）"
                 % (result["gross_margin_per_unit"], round(result["gross_margin_pct"] * 100, 1)))
    lines.append("获客成本 CAC : %s" % result["cac"])
    if "customer_lifetime_months" in result:
        lines.append("客户生命周期 Lifetime : %s 个月 months" % result["customer_lifetime_months"])
    if result.get("ltv") is not None:
        lines.append("客户终身价值 LTV : %s" % result["ltv"])
    if result.get("ltv_cac") is not None:
        lines.append("LTV/CAC : %s" % result["ltv_cac"])
    if result.get("payback") is not None:
        lines.append("回本周期 Payback : %s 期 periods" % result["payback"])
    if result.get("note"):
        lines.append("注意 Note : %s" % result["note"])
    lines.append("结论 Verdict : %s" % result["verdict_text"])
    return "\n".join(lines)


def interactive():
    data = {}
    data["product"] = input("产品名 product name（可选 optional）: ").strip()
    raw_price = input("每期价格 price per period（必填 required，如 19.9）: ").strip()
    data["price"] = _num(raw_price) if raw_price else None
    period = input("计费周期 period（month/year/one_time，默认 month）: ").strip() or "month"
    data["period"] = period
    raw_cost = input("每期变动成本 unit_cost（可选，默认 0）: ").strip()
    data["unit_cost"] = _num(raw_cost) if raw_cost else 0
    raw_cac = input("获客成本 cac（必填 required，如 150）: ").strip()
    data["cac"] = _num(raw_cac) if raw_cac else None
    raw_churn = input("月流失率 monthly_churn 0-1（可选，如 0.05）: ").strip()
    data["monthly_churn"] = _num(raw_churn) if raw_churn else None
    return data


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    as_json = "--json" in argv
    if "--interactive" in argv or "-i" in argv:
        data = interactive()
    else:
        path = [a for a in argv if not a.startswith("-")][0]
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:  # noqa: BLE001
            print("错误 Error: 无法读取 JSON cannot read JSON - %s" % exc)
            return 1
    result = calculate(data)
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))