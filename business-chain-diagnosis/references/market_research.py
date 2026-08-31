#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dandelion 市场调研引擎 | Market Research Engine

对数字产品做全网桌面研究，输出 8 个市场指标的证据与 0-10 分数。
Runs desk research on the web for a digital product and outputs evidence and
0-10 scores for 8 market indicators.

用法 Usage:
    python market_research.py --product "产品描述 product description" [options]
    python market_research.py product.json [options]

产品描述 JSON schema (product.json):
{
  "product": "产品一句话描述 one-line description (必填 required)",
  "target_user": "目标用户 target users (可选 optional)",
  "market": "目标市场 target market, 默认 全球/中国 (可选 optional)",
  "lang": "zh | en (可选 optional, 默认 auto)"
}

选项 Options:
    --out <path>            输出 JSON 路径 (默认 market_research_report.json)
    --format json|md|both   输出格式 (默认 both)
    --score-only <path>     不联网，仅用已填写的证据表单计算分数
    --calibrate <path>      用人工校准 JSON {metric_id: score} 覆盖机器分
    --no-search             不联网，仅生成检索计划与证据表单
    --force                 覆盖已有的已填证据表单（默认保留；产品不同时拒绝覆盖）
    --target-user <text>    目标用户描述 target users (可选 optional)
    --market <text>         目标市场 target market (可选 optional)
    --lang zh|en|auto       语言 language (可选 optional, 默认 auto)

搜索后端 Search backends (按顺序自动选择，读环境变量):
    TAVILY_API_KEY   https://tavily.com            (推荐 recommended)
    SERPER_API_KEY   https://serper.dev            (Google 搜索)
    BING_API_KEY     https://bing.com 搜索 API      (微软 Bing)

没有配置任何 key 时: 程序生成每个指标的搜索词清单和 evidence_fill_form.json，
由 agent 用自己的联网搜索补完证据，再用 --score-only 计算分数；流程自动降级，不中断。
社区直抓 Community: 检索计划包含 site:reddit.com / news.ycombinator.com / zhihu.com 等
定向查询，报告输出「社区信号 Community Signals」板块；无 key 时社区直查清单写进
evidence_fill_form.json 的 community_plan 字段，由 agent 补查后回填 community_signals。
无 key 时还会自动直抓 Hacker News（免费公开接口，无需 key）。
When no API key is configured: the program generates a search plan (query
list per metric) and evidence_fill_form.json; the agent completes the evidence
with its own web search, then runs --score-only to compute scores.
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

__version__ = "1.2.0"

# ---------------------------------------------------------------------------
# 指标定义 Metrics
# ---------------------------------------------------------------------------
METRICS = [
    ("user_persona", "用户画像 User Persona",
     "目标人群是否真实存在、活跃、有公开讨论；画像能否精确到人群+状态+场景"),
    ("market_scope", "群体范围 Market Scope",
     "目标群体规模能否界定与估算；覆盖全球还是特定地区/人群"),
    ("pain_point", "痛点与需求 Pain Points",
     "痛点是否被公开讨论；场景、频率是否具体；是否区分想要与愿意付费"),
    ("willingness_to_pay", "付费意愿 Willingness to Pay",
     "同类产品是否有人付费、定价基准、社区里的付费讨论"),
    ("payment_habit", "付费习惯 Payment Habits",
     "目标群体的付费方式、订阅习惯、价格敏感度"),
    ("competitors", "竞品分析 Competitors",
     "竞品数量、头部玩家、差异化空间、替代方案"),
    ("market_size", "市场规模 Market Size",
     "TAM/SAM/SOM 等公开数据与趋势报告"),
    ("channels", "渠道分布 Channels",
     "目标用户聚集的平台/社区/渠道，可触达性"),
]

CREDIBLE_DOMAINS = (
    "wikipedia.org", ".gov", ".edu", "reuters.com", "bloomberg.com",
    "forbes.com", "techcrunch.com", "producthunt.com", "gartner.com",
    "statista.com", "crunchbase.com", "similarweb.com", "g2.com",
    "capterra.com", "trustpilot.com", "github.com", "ycombinator.com",
    "indiehackers.com", "reddit.com", "quora.com", "zhihu.com", "36kr.com",
    "ithome.com", "sspai.com", "play.google.com", "apps.apple.com",
    "buildin.ai", "a16z.com", "sequoiacap.com", "indexventures.com",
    "wsj.com", "ft.com", "economist.com", "nytimes.com", "theinformation.com",
    "mckinsey.com", "bcg.com", "deloitte.com", "idc.com",
    "oecd.org", "imf.org", "worldbank.org",
    "jiemian.com", "thepaper.cn", "caixin.com", "tmtpost.com",
    "sensortower.com", "semrush.com", "ahrefs.com",
)

COMMUNITY_DOMAINS = (
    "reddit.com", "news.ycombinator.com", "ycombinator.com", "zhihu.com",
    "quora.com", "indiehackers.com", "v2ex.com", "producthunt.com", "sspai.com",
)


def is_community(url):
    """True if the URL host belongs to a user community (Reddit/HN/知乎 etc.)."""
    host = _host_of(url)
    if not host:
        return False
    return any(host == d or host.endswith("." + d) for d in COMMUNITY_DOMAINS)

SPECIFIC_RE = re.compile(
    r"(\d+(\.\d+)?\s*(%|万|亿|k|m|b|美元|人民币|元|\$|€|£|users|million|billion|人|家|款))"
    r"|([一二三四五六七八九两]\s*成)"
    r"|(\$|¥|￥)\s?\d+|(\d+\s*元)|(订阅|月费|年费|定价|pricing|price|paid|付费|免费)"
)


def _host_of(url):
    """Extract lowercase hostname from a URL; returns '' on failure."""
    try:
        return (urllib.parse.urlparse(url or "").netloc or "").lower()
    except Exception:
        return ""


def is_credible(url):
    """Hostname-based credibility check (no substring false positives)."""
    host = _host_of(url)
    if not host:
        return False
    if host.endswith(".gov") or host.endswith(".edu"):
        return True
    return any(host == d or host.endswith("." + d) for d in CREDIBLE_DOMAINS)


def is_specific(text):
    return bool(SPECIFIC_RE.search(text or ""))


CJK_STOPCHARS = "的了是在有和与及等对为从到个之一不也很就都还要再又跟向同中上下于以可要"


def query_keywords(text, limit=48):
    """把长产品/用户描述压缩成紧凑检索词（保留 CJK 短语，丢弃纯停用字段）。"""
    parts = re.split(r"[^\w一-鿿]+", text or "")
    out, seen, size = [], set(), 0
    for part in parts:
        if not part:
            continue
        if re.fullmatch(r"[一-鿿]+", part):
            if len(part) >= 2 and not set(part) <= set(CJK_STOPCHARS) and part not in seen:
                out.append(part)
                seen.add(part)
                size += len(part)
        else:
            w = part.lower()
            if len(w) >= 3 and w not in seen:
                out.append(w)
                seen.add(w)
                size += len(w)
        if size >= limit:
            break
    return " ".join(out)


def default_queries(product, target_user, lang):
    kw = query_keywords(product)
    kw_en = query_keywords(product)
    q = []
    if lang == "zh":
        q = [
            ("user_persona", [f"{kw} 目标用户 人群 画像", f"{kw} 用户 是谁 场景"]),
            ("market_scope", [f"{kw} 目标市场 规模 用户数", f"{kw} 群体 范围 覆盖"]),
            ("pain_point", [f"{kw} 痛点 问题 用户 抱怨", f"{kw} 需求 场景 频率"]),
            ("willingness_to_pay", [f"{kw} 价格 定价 付费 多少钱", f"{kw} 用户 愿意 付费"]),
            ("payment_habit", [f"{kw} 订阅 付费习惯 支付方式", f"{kw} 价格敏感 续费"]),
            ("competitors", [f"{kw} 竞品 替代 对比", f"{kw} 同类 产品 有哪些"]),
            ("market_size", [f"{kw} 市场规模 TAM SAM 报告", f"{kw} 行业 数据 趋势"]),
            ("channels", [f"{kw} 社区 论坛 用户 聚集", f"{kw} 渠道 获客 平台"]),
        ]
    elif lang == "en":
        q = [
            ("user_persona", [f"{kw_en} target user persona audience", f"{kw_en} who uses this"]),
            ("market_scope", [f"{kw_en} market size users", f"{kw_en} addressable market"]),
            ("pain_point", [f"{kw_en} problem pain point users complain", f"{kw_en} reviews feedback"]),
            ("willingness_to_pay", [f"{kw_en} pricing price subscription cost", f"{kw_en} willing to pay"]),
            ("payment_habit", [f"{kw_en} subscription payment habits SaaS spend", f"{kw_en} churn price sensitivity"]),
            ("competitors", [f"{kw_en} competitors alternatives compare", f"{kw_en} similar products"]),
            ("market_size", [f"{kw_en} TAM SAM market report forecast", f"{kw_en} market size growth"]),
            ("channels", [f"{kw_en} community forum where users discuss", f"{kw_en} distribution channels"]),
        ]
    else:
        q = default_queries(product, target_user, "zh")
        en = default_queries(product, target_user, "en")
        q = [(mid, list(zh) + en_queries) for (mid, zh, en_queries) in
             [(m[0], zhq, dict(en)[m[0]]) for m, zhq in q]]
    if target_user:
        t = query_keywords(target_user)
        q[0][1].insert(0, f"{t} 痛点 讨论")
        q[2][1].insert(0, f"{t} problems community")
    return q


COMMUNITY_METRICS = ("user_persona", "pain_point", "willingness_to_pay", "competitors", "channels")

COMMUNITY_SITES_ZH = "site:zhihu.com OR site:reddit.com OR site:quora.com"
COMMUNITY_SITES_EN = "site:reddit.com OR site:news.ycombinator.com OR site:indiehackers.com"


def community_queries(product, target_user, lang):
    """社区定向检索词（site: 操作符），用于直抓目标用户的真实讨论。

    覆盖 5 个与社区证据最相关的指标；无 key 降级时作为 agent 的直查清单。
    """
    kw = query_keywords(product)
    t = query_keywords(target_user) if target_user else kw
    if lang == "en":
        return {
            "user_persona": [f"{t} {COMMUNITY_SITES_EN}"],
            "pain_point": [f"{kw} problems complaints {COMMUNITY_SITES_EN}"],
            "willingness_to_pay": [f"{kw} pricing paid {COMMUNITY_SITES_EN}"],
            "competitors": [f"{kw} alternatives {COMMUNITY_SITES_EN}"],
            "channels": [f"{kw} {COMMUNITY_SITES_EN}"],
        }
    return {
        "user_persona": [f"{t} 讨论 {COMMUNITY_SITES_ZH}"],
        "pain_point": [f"{kw} 痛点 抱怨 吐槽 {COMMUNITY_SITES_ZH}"],
        "willingness_to_pay": [f"{kw} 付费 价格 值不值 {COMMUNITY_SITES_ZH}"],
        "competitors": [f"{kw} 替代 推荐 对比 {COMMUNITY_SITES_ZH}"],
        "channels": [f"{kw} {COMMUNITY_SITES_ZH}"],
    }


# ---------------------------------------------------------------------------
# 搜索后端 Search backends (标准库 urllib only)
# ---------------------------------------------------------------------------
def _post_json(url, payload, headers, timeout=20):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url, headers, timeout=20):
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_tavily(query, api_key, max_results=5):
    data = _post_json("https://api.tavily.com/search",
                      {"api_key": api_key, "query": query,
                       "search_depth": "basic", "max_results": max_results},
                      {"Content-Type": "application/json"})
    return [{"title": r.get("title", ""), "url": r.get("url", ""),
             "snippet": r.get("content", "")}
            for r in data.get("results", [])[:max_results]]


def search_serper(query, api_key, max_results=5):
    data = _post_json("https://google.serper.dev/search",
                      {"q": query, "num": max_results},
                      {"Content-Type": "application/json", "X-API-KEY": api_key})
    return [{"title": r.get("title", ""), "url": r.get("link", ""),
             "snippet": r.get("snippet", "")}
            for r in data.get("organic", [])[:max_results]]


def search_bing(query, api_key, max_results=5):
    url = ("https://api.bing.microsoft.com/v7.0/search?q=" +
           urllib.parse.quote(query) + "&count=%d" % max_results)
    data = _get_json(url, {"Ocp-Apim-Subscription-Key": api_key})
    return [{"title": r.get("name", ""), "url": r.get("url", ""),
             "snippet": r.get("snippet", "")}
            for r in data.get("webPages", {}).get("value", [])[:max_results]]


def parse_hn_response(data, max_results=5):
    """把 Hacker News Algolia 响应转成统一 evidence 条目（community_source=hn）。"""
    items = []
    for h in (data.get("hits") or [])[:max_results]:
        title = h.get("title") or h.get("story_title") or ""
        if not title:
            continue
        url = h.get("url") or ("https://news.ycombinator.com/item?id=" + str(h.get("objectID", "")))
        snippet = (h.get("comment_text") or h.get("story_text") or "")
        snippet = snippet.replace("<!-- -->", " ").strip()[:300]
        items.append({"title": title, "url": url, "snippet": snippet,
                      "community_source": "hn", "source": "hn"})
    return items


def search_hn(query, max_results=5, timeout=12):
    """Hacker News 免费公开接口（Algolia，无需 key）。网络失败静默返回空列表。"""
    if not query:
        return []
    url = ("https://hn.algolia.com/api/v1/search?query=" +
           urllib.parse.quote(query) + "&hitsPerPage=%d" % max_results)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "dandelion-market-research/1.2"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
        return parse_hn_response(data, max_results)
    except Exception:
        return []


BACKENDS = [
    ("tavily", "TAVILY_API_KEY", search_tavily),
    ("serper", "SERPER_API_KEY", search_serper),
    ("bing", "BING_API_KEY", search_bing),
]


def detect_backend(env):
    for name, key_env, _ in BACKENDS:
        if env.get(key_env):
            return name, env[key_env]
    return None, None


def available_backends(env):
    """All configured backends in priority order: [(name, api_key), ...]."""
    return [(name, env[key_env]) for name, key_env, _ in BACKENDS if env.get(key_env)]


def search_with_fallback(query, candidates, max_results=4):
    """Try each configured backend in order; return (results, backend_name).

    Falls through on error or empty results; returns ([], "") if all fail.
    """
    by_name = {b[0]: b[2] for b in BACKENDS}
    for name, api_key in candidates:
        try:
            results = by_name[name](query, api_key, max_results=max_results)
            if results:
                return results, name
        except Exception:
            continue
    return [], ""


# ---------------------------------------------------------------------------
# 打分 Scoring
# ---------------------------------------------------------------------------
def _query_terms(query_text):
    """Weak relevance terms: CJK bigrams + English words (len>=4)."""
    if isinstance(query_text, list):
        query_text = " ".join(query_text)
    text = query_text or ""
    cjk = re.findall(r"[一-鿿]", text)
    terms = {cjk[i] + cjk[i + 1] for i in range(len(cjk) - 1)}
    terms.update(w for w in re.findall(r"[a-z][a-z0-9]{3,}", text.lower()))
    return terms


def _matches_query(item, terms):
    if not terms:
        return True
    text = (item.get("title", "") + " " + item.get("snippet", "")).lower()
    return any(t in text for t in terms)


def score_evidence(evidence, queries=""):
    """机器证据分 0-10: 数量 + 可信来源 + 具体性 + 匹配度（弱相关性折扣）。

    匹配度是折扣项而非加分项：与检索词没有任何重叠的内容把总分打折到最低一半，
    防止“有数字但不相关”的内容刷分。
    """
    if not evidence:
        return 0.0
    count_score = min(4.0, len(evidence))
    credible = sum(1 for e in evidence if is_credible(e.get("url", "")))
    cred_score = min(3.0, float(credible))
    specific = sum(1 for e in evidence if is_specific(e.get("snippet", "") + e.get("title", "")))
    spec_score = min(3.0, float(specific))
    base = min(10.0, count_score + cred_score + spec_score)
    terms = _query_terms(queries)
    matched = sum(1 for e in evidence if _matches_query(e, terms))
    ratio = matched / float(len(evidence))
    return round(base * (0.5 + 0.5 * ratio), 1)


def tier_for(score):
    if score >= 7:
        return "strong"
    if score >= 4:
        return "weak"
    return "none"


# ---------------------------------------------------------------------------
# 输出 Output
# ---------------------------------------------------------------------------
def build_report(product_desc, target_user, market, lang, metrics, backend, mode, generated_at, notes, community_signals=None):
    scores = [m["score"] for m in metrics]
    overall = round(sum(scores) / len(scores), 1) if scores else 0.0
    return {
        "product": product_desc,
        "target_user": target_user,
        "market": market,
        "lang": lang,
        "generated_at": generated_at,
        "backend": backend,
        "mode": mode,
        "overall_score": overall,
        "overall_tier": tier_for(overall),
        "metrics": metrics,
        "community_signals": community_signals or [],
        "notes": notes,
    }


def render_markdown(report):
    lines = ["## 市场调研 Market Research", ""]
    lines.append("- 产品 Product：%s" % report["product"])
    if report.get("target_user"):
        lines.append("- 目标用户 Target users：%s" % report["target_user"])
    if report.get("market"):
        lines.append("- 目标市场 Target market：%s" % report["market"])
    lines.append("- 后端 Backend：%s ｜ 模式 Mode：%s ｜ 生成时间：%s"
                 % (report["backend"], report["mode"], report["generated_at"]))
    lines.append("- 总体证据分 Overall evidence score：**%s/10**（%s）"
                 % (report["overall_score"], report["overall_tier"]))
    lines.append("")
    lines.append("| 指标 Metric | 分数 Score | 证据档 Tier | 证据数 | 来源 Sources |")
    lines.append("| --- | --- | --- | --- | --- |")
    for m in report["metrics"]:
        srcs = "; ".join(e.get("url", "") for e in m["evidence"][:3])
        lines.append("| %s | %s | %s | %d | %s |"
                     % (m["label"], m["score"], m["tier"], len(m["evidence"]), srcs))
    lines.append("")
    if not any(m["evidence"] for m in report["metrics"]):
        lines.append("> 说明 Note：0.0 分 = 未找到公开证据（证据强度分），不代表市场不存在或产品失败。")
        lines.append("> 0.0 means no public evidence was found (evidence-strength score); it does NOT mean the market does not exist or the product failed.")
        lines.append("")
    for m in report["metrics"]:
        lines.append("### %s — %s/10（%s）" % (m["label"], m["score"], m["tier"]))
        lines.append("")
        if m.get("summary"):
            lines.append(m["summary"])
            lines.append("")
        if not m["evidence"]:
            lines.append("无公开证据 No public evidence found. %s" % m.get("queries", ""))
            lines.append("")
            continue
        for e in m["evidence"][:5]:
            lines.append("- %s [%s](%s)" % (e.get("title", ""), e.get("url", ""), e.get("url", "")))
            snip = e.get("snippet", "").strip()
            if snip:
                lines.append("  %s" % snip[:220])
        lines.append("")
    community = report.get("community_signals") or []
    if community:
        lines.append("### 社区信号 Community Signals")
        lines.append("")
        lines.append("目标用户在社区里的真实讨论（直抓；agent 需阅读核对真实需求、付费意愿等）：")
        lines.append("Real community discussions (directly captured; read them to verify demand & willingness to pay):")
        lines.append("")
        for e in community[:8]:
            tag = "[HN] " if e.get("community_source") == "hn" else ""
            lines.append("- %s%s [%s](%s)" % (tag, e.get("title", ""), e.get("url", ""), e.get("url", "")))
            snip = e.get("snippet", "").strip()
            if snip:
                lines.append("  %s" % snip[:200])
        lines.append("")
    elif report.get("mode") in ("plan_only", "agent_fill"):
        lines.append("> 社区直查清单 Community checklist：请运行 evidence_fill_form.json 中 community_plan 的 site: 查询，")
        lines.append("> 把结果填进 community_signals 后重跑 --score-only。")
        lines.append("")
    if report.get("notes"):
        lines.append("> 备注 Notes：%s" % report["notes"])
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 主流程 Main
# ---------------------------------------------------------------------------
def parse_args(argv):
    args = {"product": None, "out": "market_research_report.json",
            "format": "both", "score_only": None, "calibrate": None,
            "no_search": False, "force": False,
            "target_user": "", "market": "", "lang": ""}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif a == "--product" and i + 1 < len(argv):
            args["product"] = argv[i + 1]
            i += 1
        elif a == "--target-user" and i + 1 < len(argv):
            args["target_user"] = argv[i + 1]
            i += 1
        elif a == "--market" and i + 1 < len(argv):
            args["market"] = argv[i + 1]
            i += 1
        elif a == "--lang" and i + 1 < len(argv):
            args["lang"] = argv[i + 1]
            i += 1
        elif a == "--out" and i + 1 < len(argv):
            args["out"] = argv[i + 1]
            i += 1
        elif a == "--format" and i + 1 < len(argv):
            args["format"] = argv[i + 1]
            i += 1
        elif a == "--score-only" and i + 1 < len(argv):
            args["score_only"] = argv[i + 1]
            i += 1
        elif a == "--calibrate" and i + 1 < len(argv):
            args["calibrate"] = argv[i + 1]
            i += 1
        elif a == "--no-search":
            args["no_search"] = True
        elif a == "--force":
            args["force"] = True
        elif not a.startswith("-"):
            args["product"] = a
        else:
            print("未知参数 unknown option: %s" % a)
            sys.exit(2)
        i += 1
    return args


def load_product(path_or_desc, fallback=None):
    if fallback and fallback.get("product"):
        return (fallback["product"], fallback.get("target_user", ""),
                fallback.get("market", ""), fallback.get("lang", "auto"))
    if not path_or_desc:
        return "", "", "", "auto"
    if os.path.exists(path_or_desc) and path_or_desc.lower().endswith(".json"):
        with open(path_or_desc, encoding="utf-8") as f:
            data = json.load(f)
        return (data.get("product", ""), data.get("target_user", ""),
                data.get("market", ""), data.get("lang", "auto"))
    return path_or_desc, "", "", "auto"




def print_key_setup_hint():
    """No API key detected: print actionable setup instructions (中英双语)."""
    print()
    print("⚠ 未检测到搜索 API key  No search API key detected")
    print("   (TAVILY_API_KEY / SERPER_API_KEY / BING_API_KEY 均未配置)")
    print("已自动降级：生成检索计划 + evidence_fill_form.json，由 agent 补查后打分。")
    print("Degraded: a search plan + evidence_fill_form.json was generated; the agent fills")
    print("evidence with its own web search, then scores.")
    print("已尝试 Hacker News 免费接口直抓社区讨论（无需 key）；全自动搜索仍建议配置一个 key。")
    print("A free Hacker News capture is attempted automatically; configure a key for full web search.")
    print()
    print("想让脚本全自动联网搜索？配置一个 key 即可（可选，约 2 分钟）。")
    print("Want fully automatic web search? Set up one key (optional, ~2 min):")
    print("  1. 免费领取 API key  Get a free API key:")
    print("     - Tavily (推荐 recommended): https://tavily.com → Dashboard → API Keys")
    print("     - Serper (Google 结果): https://serper.dev → API Key")
    print("     - Bing: Azure 门户 → Bing Web Search 资源 → Keys & Endpoint")
    print("  2. 设置环境变量（变量名必须一致；key 只存本机、不会进 Git）")
    print("     Set the env var (name must match; key stays local, never in Git):")
    print("     - Windows 当前会话 current session: $env:TAVILY_API_KEY=tvly-xxxx")
    print("     - Windows 永久 permanent: setx TAVILY_API_KEY tvly-xxxx")
    print("     - macOS/Linux: export TAVILY_API_KEY=tvly-xxxx   (写入 ~/.zshrc 持久生效)")
    print("  3. 重新运行验证  Re-run to verify:")
    print("     python references/market_research.py --product 你的产品")
    print("     输出显示 live backend (tavily/serper/bing) 即配置成功。")
    print()

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = parse_args(sys.argv[1:])
    if not args["product"] and not args["score_only"]:
        print("错误 Error: 缺少产品描述 missing --product")
        print(__doc__)
        return 1

    score_only_data = {}
    if args["score_only"]:
        try:
            with open(args["score_only"], encoding="utf-8") as _f:
                score_only_data = json.load(_f)
        except Exception:
            score_only_data = {}
    product, target_user, market, lang = load_product(args["product"], score_only_data)
    if args.get("target_user"):
        target_user = args["target_user"]
    if args.get("market"):
        market = args["market"]
    if args.get("lang"):
        lang = args["lang"]
    if not product:
        print("错误 Error: product.json 缺少 product 字段")
        return 1
    if lang not in ("zh", "en", "auto"):
        lang = "auto"
    if lang == "auto":
        lang = "zh" if any("\u4e00" <= c <= "\u9fff" for c in product[:60]) else "en"

    generated_at = time.strftime("%Y-%m-%d %H:%M:%S")

    metrics_out = []
    notes = []
    community_signals = []

    # ---- 模式 1: 仅用填写表单打分（不联网） ----
    if args["score_only"]:
        with open(args["score_only"], encoding="utf-8") as f:
            filled_form = json.load(f)
        filled = filled_form.get("metrics", {})
        community_signals = filled_form.get("community_signals") or []
        for mid, label, desc in METRICS:
            entry = filled.get(mid, {}) or {}
            if "score" in entry and isinstance(entry["score"], (int, float)):
                score = float(entry["score"])
                evidence = entry.get("evidence", [])
            else:
                evidence = entry.get("evidence", [])
                score = score_evidence(evidence, entry.get("queries") or "")
            metrics_out.append({
                "id": mid, "label": label, "desc": desc, "score": score,
                "tier": tier_for(score), "evidence": evidence,
                "summary": entry.get("note", ""), "queries": "",
            })
        mode = "agent_fill"
        backend = "agent (manual fill)"
        notes.append("分数基于 agent 填写的证据表单计算；证据质量由填写者保证。")
        notes.append("Scores computed from agent-filled evidence form; evidence quality is the filler's responsibility.")

    else:
        # ---- 模式 2: 联网搜索 ----
        env = os.environ
        backends_avail = available_backends(env)
        do_search = bool(backends_avail) and not args["no_search"]
        queries_map = dict(default_queries(product, target_user, lang))

        if not do_search:
            backend = "none (no API key)"
            notes.append("未配置 TAVILY_API_KEY / SERPER_API_KEY / BING_API_KEY。")
            notes.append("No API key configured. Fill evidence_fill_form.json and re-run with --score-only.")
            print_key_setup_hint()
        else:
            mode = "live_search"
            backend = " -> ".join(n for n, _ in backends_avail)
            notes.append("实时搜索（多后端按序降级：%s）；结果分数为机器证据分，agent 可人工校准 (--calibrate)。"
                         % backend)
            notes.append("Live search (multi-backend fallback: %s); scores are machine evidence scores; calibrate with --calibrate." % backend)

        # 生成检索计划 / 证据表单（保留已有已填证据，不静默覆盖）
        community_map = community_queries(product, target_user, lang)
        community_plan = {mid: community_map.get(mid, []) for mid in COMMUNITY_METRICS}
        plan = [{"id": mid, "label": label, "desc": desc,
                 "queries": (queries_map.get(mid, [])[:3] +
                             community_map.get(mid, [])[:2])}
                for mid, label, desc in METRICS]

        preserved = {}
        if os.path.exists("evidence_fill_form.json"):
            try:
                with open("evidence_fill_form.json", encoding="utf-8") as f:
                    old_form = json.load(f)
                old_metrics = old_form.get("metrics", {}) or {}
                old_product = old_form.get("product", "") or ""
                has_evidence = any((old_metrics.get(mid, {}) or {}).get("evidence")
                                   for mid, _, _ in METRICS)
                if has_evidence and old_product and old_product != product and not args["force"]:
                    print("警告 Warning：evidence_fill_form.json 属于其他产品（%s），"
                          "为避免覆盖已填证据已停止；确认要重新生成请加 --force。"
                          % old_product[:60])
                    return 1
                if has_evidence and not args['force']:
                    preserved = {mid: old_metrics.get(mid, {}) for mid, _, _ in METRICS
                                 if old_metrics.get(mid, {}).get("evidence")}
                    notes.append("已保留 %d 个指标的已填证据；本次仅更新检索词。--force 可放弃旧证据。"
                                 % len(preserved))
                elif has_evidence and args['force']:
                    notes.append('已按 --force 放弃旧证据，重新生成空表单。')
                    notes.append('--force: old evidence discarded, regenerating an empty form.')
            except Exception:
                preserved = {}

        fill_out = {"product": product, "target_user": target_user,
                    "community_plan": community_plan,
                    "community_signals": community_signals,
                    "metrics": {p["id"]: {
                        "evidence": (preserved.get(p["id"]) or {}).get("evidence", []),
                        "note": (preserved.get(p["id"]) or {}).get("note", ""),
                        "queries": p["queries"]} for p in plan}}
        with open("evidence_fill_form.json", "w", encoding="utf-8") as f:
            json.dump(fill_out, f, ensure_ascii=False, indent=2)

        if not do_search:
            if not args["no_search"]:
                kw_hn = query_keywords(product)
                t_hn = query_keywords(target_user) if target_user else ""
                seen_hn = set()
                for q in ([kw_hn] + ([t_hn] if t_hn and t_hn != kw_hn else []))[:2]:
                    if not q:
                        continue
                    for item in search_hn(q, max_results=4):
                        u = item.get("url", "")
                        if u and u not in seen_hn:
                            seen_hn.add(u)
                            community_signals.append(item)
                if seen_hn:
                    backend = "hn (free, no key)"
                    notes.append("已从 Hacker News 免费接口直抓 %d 条社区讨论（无需 key）；其余证据请按表单补查。"
                                 % len(seen_hn))
                    notes.append("Captured %d discussions from Hacker News (free API, no key); fill the rest via the form."
                                 % len(seen_hn))
            preserved_any = any((preserved.get(p["id"]) or {}).get("evidence") for p in plan)
            mode = "agent_fill" if preserved_any else "plan_only"
            if preserved_any:
                notes.append("降级模式 + 已有证据：分数来自 evidence_fill_form.json 的已填证据。")
                notes.append("Degraded mode with preserved evidence: scores come from the filled evidence form.")

        if do_search:
            used_backends = []
            if not args["no_search"]:
                kw_hn = query_keywords(product)
                t_hn = query_keywords(target_user) if target_user else ""
                for q in ([kw_hn] + ([t_hn] if t_hn and t_hn != kw_hn else []))[:2]:
                    if not q:
                        continue
                    community_signals.extend(search_hn(q, max_results=4))
                if any(c.get("community_source") == "hn" for c in community_signals):
                    used_backends.append("hn(free)")
            for p in plan:
                evidence, seen = [], set()
                for query in p["queries"]:
                    try:
                        results, used_name = search_with_fallback(query, backends_avail, max_results=4)
                        if used_name and used_name not in used_backends:
                            used_backends.append(used_name)
                    except Exception as e:
                        notes.append("[%s] 搜索失败 search failed: %s" % (p["id"], e))
                        results = []
                    for r in results:
                        u = r.get("url", "")
                        if u and u not in seen:
                            seen.add(u)
                            evidence.append(r)
                            if is_community(u):
                                community_signals.append(r)
                    if len(evidence) >= 5:
                        break
                    time.sleep(0.3)
                score = score_evidence(evidence, " ".join(p["queries"]))
                summary = summarize_metric(p["label"], evidence)
                metrics_out.append({
                    "id": p["id"], "label": p["label"], "desc": p["desc"],
                    "score": score, "tier": tier_for(score),
                    "evidence": evidence[:6], "summary": summary,
                    "queries": " | ".join(p["queries"]),
                })
            seen_c, signals = set(), []
            for item in community_signals:
                u = item.get("url", "")
                if u and u not in seen_c:
                    seen_c.add(u)
                    signals.append(item)
            community_signals = signals
            if used_backends:
                backend = " -> ".join(used_backends)
        else:
            for p in plan:
                entry = preserved.get(p["id"], {}) or {}
                evidence = entry.get("evidence", [])
                score = score_evidence(evidence, " ".join(p["queries"]))
                metrics_out.append({
                    "id": p["id"], "label": p["label"], "desc": p["desc"],
                    "score": score, "tier": tier_for(score),
                    "evidence": evidence[:6],
                    "summary": summarize_metric(p["label"], evidence),
                    "queries": " | ".join(p["queries"]),
                })

    # ---- 人工校准 ----
    if args["calibrate"]:
        try:
            with open(args["calibrate"], encoding="utf-8") as f:
                calib = json.load(f)
            for m in metrics_out:
                if m["id"] in calib and isinstance(calib[m["id"]], (int, float)):
                    m["score"] = float(calib[m["id"]])
                    m["tier"] = tier_for(m["score"])
                    m["calibrated"] = True
            notes.append("已应用人工校准 applied manual calibration.")
        except Exception as e:
            print("警告 warning: 校准文件读取失败 %s" % e)

    report = build_report(product, target_user, market, lang, metrics_out,
                          backend, mode, generated_at, notes, community_signals)

    with open(args["out"], "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    if args["format"] in ("md", "both"):
        print(render_markdown(report))
        print()
    if args["format"] in ("json", "both"):
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def summarize_metric(label, evidence):
    if not evidence:
        return "未找到公开证据 No public evidence found."
    credible = sum(1 for e in evidence if is_credible(e.get("url", "")))
    specific = sum(1 for e in evidence if is_specific(e.get("snippet", "") + e.get("title", "")))
    urls = [e.get("url", "") for e in evidence[:3]]
    return ("共 %d 条证据，其中可信来源 %d 条、含具体信息 %d 条。代表来源：%s"
            % (len(evidence), credible, specific, "；".join(urls)))


if __name__ == "__main__":
    sys.exit(main())
