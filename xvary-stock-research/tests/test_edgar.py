import unittest
from unittest.mock import Mock, patch
from typing import Optional

from tools import edgar


class EdgarTests(unittest.TestCase):
    def test_shares_outstanding_does_not_include_weighted_average_concepts(self) -> None:
        concepts = edgar._FIELD_CONCEPTS["balance_sheet"]["shares_outstanding"]
        self.assertNotIn("WeightedAverageNumberOfDilutedSharesOutstanding", concepts)
        self.assertNotIn("WeightedAverageShares", concepts)

    def test_best_entry_uses_concept_priority_before_recency(self) -> None:
        records = [
            {
                "concept": "Revenue",
                "unit": "USD",
                "form": "10-K",
                "period_end": "2026-12-31",
                "filed": "2027-02-01",
                "period_months": 12,
            },
            {
                "concept": "Revenues",
                "unit": "USD",
                "form": "10-K",
                "period_end": "2025-12-31",
                "filed": "2026-02-01",
                "period_months": 12,
            },
        ]
        best = edgar._best_entry(
            records,
            quarterly=False,
            statement="income_statement",
            field="revenue",
        )
        self.assertIsNotNone(best)
        assert best is not None
        self.assertEqual(best["concept"], "Revenues")

    def test_request_json_retries_then_succeeds(self) -> None:
        class FakeResponse:
            def __init__(self, status_code: int, payload: Optional[dict] = None) -> None:
                self.status_code = status_code
                self._payload = payload or {}

            def raise_for_status(self) -> None:
                if self.status_code >= 400:
                    raise edgar.requests.HTTPError(response=self)

            def json(self) -> dict:
                return self._payload

        session = Mock()
        session.get.side_effect = [
            FakeResponse(503),
            FakeResponse(200, {"ok": True}),
        ]

        with patch("tools.edgar.time.sleep") as sleep_mock:
            data = edgar._request_json("https://example.com", session)

        self.assertEqual(data, {"ok": True})
        self.assertEqual(session.get.call_count, 2)
        sleep_mock.assert_called_once()

    def test_request_json_raises_after_max_retries(self) -> None:
        class FakeResponse:
            def __init__(self, status_code: int) -> None:
                self.status_code = status_code

            def raise_for_status(self) -> None:
                raise edgar.requests.HTTPError(response=self)

            def json(self) -> dict:
                return {}

        session = Mock()
        session.get.return_value = FakeResponse(503)

        with patch("tools.edgar.time.sleep"):
            with self.assertRaises(edgar.requests.HTTPError):
                edgar._request_json("https://example.com", session)
        self.assertEqual(session.get.call_count, edgar._MAX_RETRIES)


if __name__ == "__main__":
    unittest.main()
