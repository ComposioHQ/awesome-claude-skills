#!/usr/bin/env python3
"""Standalone SEC EDGAR fetcher for claude-code-stock-analysis-skill.

Public functions:
- get_cik(ticker)
- get_company_facts(ticker)
- get_financials(ticker)
- get_filings_metadata(ticker)

Examples:
    python tools/edgar.py AAPL
    python tools/edgar.py NVDA --mode filings
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
import time
from typing import Any, Optional

import requests

_SEC_CIK_LOOKUP = "https://www.sec.gov/files/company_tickers.json"
_SEC_COMPANY_FACTS = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
_SEC_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
_TIMEOUT = 25
_MAX_RETRIES = 3
_INITIAL_BACKOFF_SECONDS = 1.0
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_ACCEPTED_FORMS = {"10-K", "10-Q", "20-F", "6-K"}
_ANNUAL_FORMS = {"10-K", "20-F"}
_QUARTERLY_FORMS = {"10-Q", "6-K"}
_HEADERS = {
    "User-Agent": "claude-code-stock-analysis-skill/1.0 (research@xvary.com)",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
}

# statement -> field -> accepted concept labels (US-GAAP + IFRS aliases)
_FIELD_CONCEPTS: dict[str, dict[str, tuple[str, ...]]] = {
    "income_statement": {
        "revenue": (
            "Revenues",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenue",
            "RevenueFromContractsWithCustomers",
            "RevenueFromRenderingOfServices",
        ),
        "gross_profit": ("GrossProfit",),
        "operating_income": ("OperatingIncomeLoss", "ProfitLossFromOperatingActivities"),
        "net_income": (
            "NetIncomeLoss",
            "ProfitLoss",
            "ProfitLossAttributableToOwnersOfParent",
        ),
        "eps_diluted": ("EarningsPerShareDiluted", "DilutedEarningsLossPerShare"),
        "eps_basic": (
            "EarningsPerShareBasic",
            "BasicEarningsLossPerShare",
            "BasicAndDilutedEarningsLossPerShare",
        ),
        "r_and_d": ("ResearchAndDevelopmentExpense",),
        "sga": (
            "SellingGeneralAndAdministrativeExpense",
            "GeneralAndAdministrativeExpense",
        ),
        "interest_expense": (
            "InterestExpense",
            "FinanceCosts",
            "BorrowingCostsRecognisedAsExpense",
        ),
        "income_tax_expense": ("IncomeTaxExpenseBenefit",),
    },
    "balance_sheet": {
        "total_assets": ("Assets",),
        "current_assets": ("AssetsCurrent", "CurrentAssets"),
        "current_liabilities": ("LiabilitiesCurrent", "CurrentLiabilities"),
        "total_liabilities": ("Liabilities",),
        "stockholders_equity": ("StockholdersEquity", "Equity"),
        "cash_and_equivalents": (
            "CashAndCashEquivalentsAtCarryingValue",
            "CashAndCashEquivalents",
        ),
        "long_term_debt": ("LongTermDebt", "LongTermDebtNoncurrent", "LongtermBorrowings"),
        "short_term_borrowings": (
            "ShortTermBorrowings",
            "CurrentPortionOfLongtermBorrowings",
        ),
        "shares_outstanding": (
            "CommonStockSharesOutstanding",
            "EntityCommonStockSharesOutstanding",
            "NumberOfSharesIssued",
            "ShareIssued",
            "OrdinarySharesNumber",
        ),
    },
    "cash_flow": {
        "operating_cash_flow": (
            "NetCashProvidedByOperatingActivities",
            "OperatingCashFlow",
            "CashFlowsFromUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivities",
        ),
        "capex": (
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities",
        ),
        "depreciation_amortization": (
            "DepreciationDepletionAndAmortization",
            "Depreciation",
            "DepreciationAndAmortization",
            "DepreciationExpense",
        ),
        "stock_based_compensation": (
            "StockBasedCompensation",
            "ShareBasedCompensation",
            "AdjustmentsForSharebasedPayments",
        ),
        "dividends_paid": (
            "DividendsCommonStockCash",
            "DividendsPaid",
            "DividendsPaidOrdinarySharesPerShare",
        ),
    },
}


def _concept_map() -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for statement, fields in _FIELD_CONCEPTS.items():
        for field, concepts in fields.items():
            for concept in concepts:
                out[concept] = (statement, field)
    return out


_CONCEPT_MAP = _concept_map()


def _field_concept_priority() -> dict[tuple[str, str], dict[str, int]]:
    priorities: dict[tuple[str, str], dict[str, int]] = {}
    for statement, fields in _FIELD_CONCEPTS.items():
        for field, concepts in fields.items():
            priorities[(statement, field)] = {
                concept: idx for idx, concept in enumerate(concepts)
            }
    return priorities


_FIELD_CONCEPT_PRIORITY = _field_concept_priority()


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(_HEADERS)
    return s


def _request_json(url: str, session: requests.Session) -> dict[str, Any]:
    last_error: Optional[Exception] = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=_TIMEOUT)
            if response.status_code in _RETRYABLE_STATUS_CODES:
                raise requests.HTTPError(
                    f"Retryable status {response.status_code}",
                    response=response,
                )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt >= _MAX_RETRIES:
                break
            backoff = _INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1))
            time.sleep(backoff)
    assert last_error is not None
    raise last_error


def _variants(ticker: str) -> list[str]:
    t = ticker.strip().upper()
    candidates = [
        t,
        t.replace(".", "-"),
        t.replace("-", "."),
        t.replace(".", ""),
        t.split(".")[0],
        t.split("-")[0],
    ]
    out: list[str] = []
    for c in candidates:
        if c and c not in out:
            out.append(c)
    return out


def _parse_period_months(start: Optional[str], end: Optional[str]) -> Optional[int]:
    if not end:
        return None
    if not start:
        return 0
    try:
        s = datetime.strptime(start, "%Y-%m-%d")
        e = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return None
    days = (e - s).days
    if days <= 0:
        return 0
    if days <= 120:
        return 3
    if days <= 210:
        return 6
    if days <= 310:
        return 9
    return 12


def _is_quarterly(form: str, period_months: Optional[int]) -> bool:
    if form in _QUARTERLY_FORMS:
        return True
    return period_months is not None and 1 <= period_months <= 4


def _to_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def get_cik(ticker: str) -> Optional[str]:
    """Resolve ticker to zero-padded SEC CIK."""
    with _session() as s:
        data = _request_json(_SEC_CIK_LOOKUP, s)
    lookup: dict[str, str] = {}
    for entry in data.values():
        if not isinstance(entry, dict):
            continue
        symbol = str(entry.get("ticker", "")).strip().upper()
        cik_raw = entry.get("cik_str")
        if symbol and cik_raw is not None:
            lookup[symbol] = str(cik_raw).zfill(10)
    for candidate in _variants(ticker):
        if candidate in lookup:
            return lookup[candidate]
    return None


def get_company_facts(ticker: str) -> dict[str, Any]:
    """Fetch raw EDGAR companyfacts payload for a ticker."""
    normalized = ticker.strip().upper()
    cik = get_cik(normalized)
    if not cik:
        raise ValueError(f"CIK not found for ticker: {normalized}")
    with _session() as s:
        facts = _request_json(_SEC_COMPANY_FACTS.format(cik=cik), s)
    return {
        "ticker": normalized,
        "cik": cik,
        "entity_name": facts.get("entityName", normalized),
        "facts": facts.get("facts", {}),
        "raw": facts,
        "retrieved_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


def get_filings_metadata(ticker: str, limit: int = 10) -> list[dict[str, Any]]:
    """Return recent SEC filing metadata for common report forms."""
    normalized = ticker.strip().upper()
    cik = get_cik(normalized)
    if not cik:
        raise ValueError(f"CIK not found for ticker: {normalized}")

    with _session() as s:
        payload = _request_json(_SEC_SUBMISSIONS.format(cik=cik), s)

    recent = payload.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    filing_dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])
    accessions = recent.get("accessionNumber", [])
    docs = recent.get("primaryDocument", [])

    rows: list[dict[str, Any]] = []
    for index, form in enumerate(forms):
        if form not in _ACCEPTED_FORMS:
            continue
        rows.append(
            {
                "form": form,
                "filing_date": filing_dates[index] if index < len(filing_dates) else None,
                "report_date": report_dates[index] if index < len(report_dates) else None,
                "accession_number": accessions[index] if index < len(accessions) else None,
                "primary_document": docs[index] if index < len(docs) else None,
            }
        )
        if len(rows) >= limit:
            break
    return rows


def _extract_line_items(company_facts: dict[str, Any]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    root = company_facts.get("facts", {})
    items: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for namespace in ("us-gaap", "ifrs-full"):
        ns = root.get(namespace, {})
        if not isinstance(ns, dict):
            continue
        for concept, concept_payload in ns.items():
            mapped = _CONCEPT_MAP.get(concept)
            if not mapped:
                continue
            statement, field = mapped
            units = concept_payload.get("units", {})
            if not isinstance(units, dict):
                continue
            for unit, entries in units.items():
                for entry in entries:
                    form = entry.get("form", "")
                    if form not in _ACCEPTED_FORMS:
                        continue
                    value = _to_float(entry.get("val"))
                    if value is None:
                        continue
                    end = entry.get("end")
                    if not end:
                        continue
                    start = entry.get("start")
                    items[(statement, field)].append(
                        {
                            "value": value,
                            "unit": unit,
                            "form": form,
                            "period_end": end,
                            "period_start": start,
                            "period_months": _parse_period_months(start, end),
                            "filed": entry.get("filed"),
                            "concept": concept,
                            "namespace": namespace,
                        }
                    )
    return items


def _best_entry(
    records: list[dict[str, Any]],
    quarterly: bool,
    statement: str,
    field: str,
) -> Optional[dict[str, Any]]:
    if not records:
        return None
    scoped: list[dict[str, Any]] = []
    for record in records:
        is_q = _is_quarterly(record.get("form", ""), record.get("period_months"))
        if quarterly and is_q:
            scoped.append(record)
        elif not quarterly and not is_q and record.get("form") in _ANNUAL_FORMS:
            scoped.append(record)

    if not scoped:
        return None

    concept_priority = _FIELD_CONCEPT_PRIORITY.get((statement, field), {})
    if concept_priority:
        default_rank = len(concept_priority) + 100
        best_rank = min(concept_priority.get(r.get("concept", ""), default_rank) for r in scoped)
        scoped = [
            r
            for r in scoped
            if concept_priority.get(r.get("concept", ""), default_rank) == best_rank
        ]

    unit_counts = Counter(r.get("unit") for r in scoped)
    preferred_unit = unit_counts.most_common(1)[0][0]
    scoped = [r for r in scoped if r.get("unit") == preferred_unit]
    scoped.sort(key=lambda r: (r.get("period_end", ""), r.get("filed", "")), reverse=True)
    return scoped[0]


def _build_snapshot(
    line_items: dict[tuple[str, str], list[dict[str, Any]]],
    quarterly: bool,
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, Any]], Optional[str]]:
    snapshot: dict[str, dict[str, float]] = {
        "income_statement": {},
        "balance_sheet": {},
        "cash_flow": {},
    }
    sources: dict[str, dict[str, Any]] = {}
    period_end: Optional[str] = None

    for (statement, field), records in line_items.items():
        best = _best_entry(
            records,
            quarterly=quarterly,
            statement=statement,
            field=field,
        )
        if not best:
            continue
        snapshot[statement][field] = best["value"]
        key = f"{statement}.{field}"
        sources[key] = {
            "form": best.get("form"),
            "filed": best.get("filed"),
            "period_end": best.get("period_end"),
            "unit": best.get("unit"),
            "concept": best.get("concept"),
            "namespace": best.get("namespace"),
        }
        if best.get("period_end") and (not period_end or best["period_end"] > period_end):
            period_end = best["period_end"]

    return snapshot, sources, period_end


def get_financials(ticker: str) -> dict[str, Any]:
    """Return normalized annual + quarterly financial snapshots."""
    company = get_company_facts(ticker)
    line_items = _extract_line_items(company)

    annual_snapshot, annual_sources, annual_period = _build_snapshot(
        line_items, quarterly=False
    )
    quarterly_snapshot, quarterly_sources, quarterly_period = _build_snapshot(
        line_items, quarterly=True
    )

    return {
        "ticker": company["ticker"],
        "cik": company["cik"],
        "entity_name": company["entity_name"],
        "annual": {
            "period_end": annual_period,
            "statements": annual_snapshot,
            "sources": annual_sources,
        },
        "quarterly": {
            "period_end": quarterly_period,
            "statements": quarterly_snapshot,
            "sources": quarterly_sources,
        },
        "retrieved_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description="Standalone EDGAR fetcher")
    parser.add_argument("ticker", help="Ticker symbol, e.g. AAPL")
    parser.add_argument(
        "--mode",
        default="financials",
        choices=("financials", "facts", "filings"),
        help="Output mode",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indent",
    )
    args = parser.parse_args()

    if args.mode == "financials":
        payload = get_financials(args.ticker)
    elif args.mode == "facts":
        payload = get_company_facts(args.ticker)
        payload = {
            "ticker": payload["ticker"],
            "cik": payload["cik"],
            "entity_name": payload["entity_name"],
            "namespaces": list(payload.get("facts", {}).keys()),
            "retrieved_utc": payload.get("retrieved_utc"),
        }
    else:
        payload = {
            "ticker": args.ticker.strip().upper(),
            "filings": get_filings_metadata(args.ticker),
            "retrieved_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        }

    print(json.dumps(payload, indent=args.indent, sort_keys=False))


if __name__ == "__main__":
    _main()
