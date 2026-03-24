#!/usr/bin/env python3
"""Standalone market data fetcher with no API key.

Public functions:
- get_quote(ticker)
- get_ratios(ticker)

Fallback order: Yahoo -> Finviz -> Stooq

Examples:
    python tools/market.py AAPL
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from datetime import datetime, timezone
import time
from typing import Any, Optional

import requests

_TIMEOUT = 20
_MAX_RETRIES = 3
_INITIAL_BACKOFF_SECONDS = 1.0
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_HEADERS = {
    "User-Agent": "claude-code-stock-analysis-skill/1.0 (research@xvary.com)",
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
}
_SUFFIX_MULTIPLIERS = {
    "K": 1_000,
    "M": 1_000_000,
    "B": 1_000_000_000,
    "T": 1_000_000_000_000,
}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _to_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_compact(raw: str) -> Optional[float]:
    value = raw.strip().replace(",", "").replace("$", "").replace("~", "")
    if not value or value.upper() == "N/A":
        return None
    suffix = value[-1].upper()
    mult = _SUFFIX_MULTIPLIERS.get(suffix, 1.0)
    if suffix in _SUFFIX_MULTIPLIERS:
        value = value[:-1]
    try:
        return float(value) * mult
    except ValueError:
        return None


def _parse_percent(raw: str) -> Optional[float]:
    val = raw.strip().replace("%", "")
    try:
        if not val or val.upper() == "N/A":
            return None
        return float(val)
    except ValueError:
        return None


def _http_get_json(url: str) -> dict[str, Any]:
    last_error: Optional[Exception] = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
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


def _http_get_text(url: str) -> str:
    last_error: Optional[Exception] = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            if response.status_code in _RETRYABLE_STATUS_CODES:
                raise requests.HTTPError(
                    f"Retryable status {response.status_code}",
                    response=response,
                )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            if attempt >= _MAX_RETRIES:
                break
            backoff = _INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1))
            time.sleep(backoff)
    assert last_error is not None
    raise last_error


def _fetch_yahoo(ticker: str) -> Optional[dict[str, Any]]:
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}"
    payload = _http_get_json(url)
    rows = payload.get("quoteResponse", {}).get("result", [])
    if not rows:
        return None

    q = rows[0]
    price = _to_float(q.get("regularMarketPrice"))
    if price is None:
        return None

    return {
        "provider": "yahoo",
        "price": price,
        "currency": q.get("currency", "USD"),
        "market_cap": _to_float(q.get("marketCap")),
        "volume": _to_float(q.get("regularMarketVolume")),
        "high_52w": _to_float(q.get("fiftyTwoWeekHigh")),
        "low_52w": _to_float(q.get("fiftyTwoWeekLow")),
        "pe": _to_float(q.get("trailingPE")),
        "dividend_yield_pct": (
            _to_float(q.get("dividendYield")) * 100.0
            if _to_float(q.get("dividendYield")) is not None
            else None
        ),
        "beta": _to_float(q.get("beta")),
    }


def _extract_finviz_map(html: str) -> dict[str, str]:
    pairs = re.findall(r"<td[^>]*>([^<]+)</td><td[^>]*>(?:<b>)?([^<]+)", html)
    out: dict[str, str] = {}
    for key, value in pairs:
        out[key.strip()] = value.strip()
    return out


def _fetch_finviz(ticker: str) -> Optional[dict[str, Any]]:
    url = f"https://finviz.com/quote.ashx?t={ticker.upper()}"
    html = _http_get_text(url)
    data = _extract_finviz_map(html)

    price = _parse_compact(data.get("Price", ""))
    if price is None:
        return None

    low_52w = None
    high_52w = None
    range_raw = data.get("52W Range", "")
    m = re.search(r"([0-9]+\.?[0-9]*)\s*-\s*([0-9]+\.?[0-9]*)", range_raw)
    if m:
        low_52w = _to_float(m.group(1))
        high_52w = _to_float(m.group(2))

    return {
        "provider": "finviz",
        "price": price,
        "currency": "USD",
        "market_cap": _parse_compact(data.get("Market Cap", "")),
        "volume": _parse_compact(data.get("Volume", "")),
        "high_52w": high_52w,
        "low_52w": low_52w,
        "pe": _parse_compact(data.get("P/E", "")),
        "dividend_yield_pct": _parse_percent(data.get("Dividend %", "")),
        "beta": _to_float(data.get("Beta")),
    }


def _fetch_stooq(ticker: str) -> Optional[dict[str, Any]]:
    if "." in ticker:
        return None
    symbol = f"{ticker.lower()}.us"
    url = f"https://stooq.com/q/l/?s={symbol}&f=sd2t2ohlcv&h&e=csv"
    text = _http_get_text(url)

    reader = csv.DictReader(io.StringIO(text))
    row = next(reader, None)
    if not row:
        return None

    close = _to_float(row.get("Close"))
    if close is None:
        return None

    return {
        "provider": "stooq",
        "price": close,
        "currency": "USD",
        "market_cap": None,
        "volume": _to_float(row.get("Volume")),
        "high_52w": None,
        "low_52w": None,
        "pe": None,
        "dividend_yield_pct": None,
        "beta": None,
    }


def _collect_market_data(ticker: str) -> Optional[dict[str, Any]]:
    for fetcher in (_fetch_yahoo, _fetch_finviz, _fetch_stooq):
        try:
            result = fetcher(ticker)
        except Exception:
            result = None
        if result and result.get("price") is not None:
            return result
    return None


def get_quote(ticker: str) -> dict[str, Any]:
    """Return quote-level market data (price/cap/volume/52w range)."""
    normalized = ticker.strip().upper()
    result = _collect_market_data(normalized)
    if not result:
        raise RuntimeError(f"No quote data available for {normalized}")

    return {
        "ticker": normalized,
        "provider": result["provider"],
        "price": result["price"],
        "currency": result.get("currency", "USD"),
        "market_cap": result.get("market_cap"),
        "volume": result.get("volume"),
        "high_52w": result.get("high_52w"),
        "low_52w": result.get("low_52w"),
        "as_of_utc": _iso_now(),
    }


def get_ratios(ticker: str) -> dict[str, Any]:
    """Return ratio-level market data (P/E, dividend yield, beta)."""
    normalized = ticker.strip().upper()

    # Prefer Yahoo for ratios; short-circuit once we get usable ratio data.
    fallback: Optional[dict[str, Any]] = None
    for fetcher in (_fetch_yahoo, _fetch_finviz, _fetch_stooq):
        try:
            result = fetcher(normalized)
        except Exception:
            result = None
        if not result or result.get("price") is None:
            continue
        if fallback is None:
            fallback = result
        if any(result.get(k) is not None for k in ("pe", "dividend_yield_pct", "beta")):
            chosen = result
            break
    else:
        chosen = fallback

    if not chosen:
        raise RuntimeError(f"No market data available for {normalized}")

    return {
        "ticker": normalized,
        "provider": chosen["provider"],
        "pe": chosen.get("pe"),
        "dividend_yield_pct": chosen.get("dividend_yield_pct"),
        "beta": chosen.get("beta"),
        "as_of_utc": _iso_now(),
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description="Standalone market data fetcher")
    parser.add_argument("ticker", help="Ticker symbol, e.g. AAPL")
    parser.add_argument("--indent", type=int, default=2, help="JSON indent")
    args = parser.parse_args()

    payload = {
        "quote": get_quote(args.ticker),
        "ratios": get_ratios(args.ticker),
    }
    print(json.dumps(payload, indent=args.indent, sort_keys=False))


if __name__ == "__main__":
    _main()
