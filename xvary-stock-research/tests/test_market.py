import unittest
from unittest.mock import patch
from typing import Optional

from tools import market


class MarketTests(unittest.TestCase):
    def test_get_ratios_short_circuits_after_first_provider_with_ratios(self) -> None:
        calls: list[str] = []

        def yahoo(_ticker: str):
            calls.append("yahoo")
            return {
                "provider": "yahoo",
                "price": 100.0,
                "pe": 25.0,
                "dividend_yield_pct": 1.2,
                "beta": 1.1,
            }

        def finviz(_ticker: str):
            calls.append("finviz")
            return {
                "provider": "finviz",
                "price": 100.0,
                "pe": 18.0,
                "dividend_yield_pct": 2.0,
                "beta": 0.9,
            }

        def stooq(_ticker: str):
            calls.append("stooq")
            return {
                "provider": "stooq",
                "price": 100.0,
                "pe": None,
                "dividend_yield_pct": None,
                "beta": None,
            }

        with patch("tools.market._fetch_yahoo", yahoo), patch(
            "tools.market._fetch_finviz", finviz
        ), patch("tools.market._fetch_stooq", stooq):
            result = market.get_ratios("AAPL")

        self.assertEqual(result["provider"], "yahoo")
        self.assertEqual(calls, ["yahoo"])

    def test_get_ratios_uses_second_provider_when_first_has_no_ratios(self) -> None:
        calls: list[str] = []

        def yahoo(_ticker: str):
            calls.append("yahoo")
            return {
                "provider": "yahoo",
                "price": 100.0,
                "pe": None,
                "dividend_yield_pct": None,
                "beta": None,
            }

        def finviz(_ticker: str):
            calls.append("finviz")
            return {
                "provider": "finviz",
                "price": 100.0,
                "pe": 18.0,
                "dividend_yield_pct": 2.0,
                "beta": 0.9,
            }

        def stooq(_ticker: str):
            calls.append("stooq")
            return None

        with patch("tools.market._fetch_yahoo", yahoo), patch(
            "tools.market._fetch_finviz", finviz
        ), patch("tools.market._fetch_stooq", stooq):
            result = market.get_ratios("AAPL")

        self.assertEqual(result["provider"], "finviz")
        self.assertEqual(calls, ["yahoo", "finviz"])

    def test_http_get_json_retries_then_succeeds(self) -> None:
        class FakeResponse:
            def __init__(self, status_code: int, payload: Optional[dict] = None) -> None:
                self.status_code = status_code
                self._payload = payload or {}

            def raise_for_status(self) -> None:
                if self.status_code >= 400:
                    raise market.requests.HTTPError(response=self)

            def json(self) -> dict:
                return self._payload

        with patch("tools.market.requests.get") as get_mock, patch(
            "tools.market.time.sleep"
        ) as sleep_mock:
            get_mock.side_effect = [
                FakeResponse(503),
                FakeResponse(200, {"ok": True}),
            ]
            payload = market._http_get_json("https://example.com")

        self.assertEqual(payload, {"ok": True})
        self.assertEqual(get_mock.call_count, 2)
        sleep_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
