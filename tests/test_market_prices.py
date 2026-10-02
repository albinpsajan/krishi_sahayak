"""Regression fixtures are test-only; the production service has no price fixtures."""
import os
import unittest
from unittest.mock import patch
from services.cache import clear
from services.market_price_service import get_prices
from services.market_provider import _records_from_agmarknet_payload


def record(crop="Banana", price=3100, **kwargs):
    return {"commodity": crop, "state": "Kerala", "district": "Thrissur",
            "market": "Thrissur", "variety": "Other", "grade": "FAQ",
            "arrival_date": "01/01/2025", "min_price": str(price - 100),
            "max_price": str(price + 100), "modal_price": str(price), **kwargs}


class MarketPriceTests(unittest.TestCase):
    def setUp(self):
        clear()
        self.key = patch.dict(os.environ, {"DATA_GOV_API_KEY": "test-only"})
        self.key.start()
        self.addCleanup(self.key.stop)
        self.addCleanup(clear)

    @patch("services.market_price_service.fetch_records")
    def test_no_data_gov_key_still_uses_keyless_agmarknet(self, fetch):
        with patch.dict(os.environ, {"DATA_GOV_API_KEY": ""}):
            fetch.return_value = [record()]
            result = get_prices()
        self.assertTrue(result["available"])
        self.assertEqual(result["modal_price"], 3100)
        fetch.assert_called_once()

    @patch("services.market_price_service.fetch_records")
    def test_crop_switch_and_cache_are_isolated(self, fetch):
        fetch.side_effect = [[record()], [record("Tomato", 1700)]]
        banana = get_prices("banana")
        tomato = get_prices("tomato")
        self.assertEqual(banana["modal_price"], 3100)
        self.assertEqual(tomato["modal_price"], 1700)
        self.assertEqual(get_prices("banana")["modal_price"], 3100)
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(fetch.call_args.args[0], "Tomato")
        self.assertIsNone(tomato["change"])

    @patch("services.market_price_service.fetch_records")
    def test_rejects_wrong_crop_location_and_invalid_prices(self, fetch):
        fetch.return_value = [record("Tomato"), record(district="Palakkad"),
                              record(modal_price="NaN"), record(arrival_date="invalid"),
                              record(modal_price="999999"), record(modal_price=None)]
        result = get_prices("banana", market="Thrissur")
        self.assertFalse(result["available"])
        self.assertIsNone(result["modal_price"])

    @patch("services.market_price_service.fetch_records")
    def test_newest_report_preserves_variety_and_actual_date(self, fetch):
        fetch.return_value = [record(), record(price=3300, arrival_date="02/01/2025", variety="Robusta")]
        result = get_prices()
        self.assertEqual(result["arrival_date"], "2025-01-02")
        self.assertEqual(result["variety"], "Robusta")
        self.assertEqual(result["modal_price"], 3300)
        self.assertTrue(result["stale"])

    @patch("services.market_price_service.fetch_records")
    def test_state_fallback_uses_real_market_without_relabeling(self, fetch):
        fetch.side_effect = [[], [record(district="Palakkad", market="Palakkad Market")]]
        result = get_prices("banana", "Kerala", "Thrissur")
        self.assertTrue(result["available"])
        self.assertEqual(result["district"], "Palakkad")
        self.assertEqual(result["market"], "Palakkad Market")
        self.assertEqual(result["location_match"], "state")
        self.assertIn("No recent Thrissur report", result["warning"])

    @patch("services.market_price_service.fetch_records", side_effect=OSError("offline"))
    def test_provider_failure_never_fabricates_price(self, fetch):
        result = get_prices("coconut")
        self.assertFalse(result["available"])
        self.assertIsNone(result["modal_price"])

    @patch("services.market_price_service.fetch_records", return_value=[])
    def test_no_records_and_unknown_crop(self, fetch):
        self.assertEqual(get_prices("paddy")["reason"], "no_records")
        self.assertEqual(fetch.call_args.args[0], "Paddy(Common)")
        self.assertEqual(get_prices("vegetables")["reason"], "unsupported_crop")
        self.assertEqual(fetch.call_count, 2)

    def test_agmarknet_payload_is_normalized_to_price_records(self):
        filters = {
            "market_data": [{"id": 139, "mkt_name": "Thrissur Market", "state_id": 17, "district_id": 283}],
            "district_data": [{"id": 283, "state_id": 17, "district_name": "Thirssur"}],
        }
        state = {"state_id": 17, "state_name": "Keralam"}
        payload = {"success": True, "markets": [{"marketName": "Thrissur Market", "dates": [{
            "arrivalDate": "02/10/2026",
            "data": [{"variety": "Robusta", "minimumPrice": 2200, "maximumPrice": 3000, "modalPrice": 2700, "arrivals": 0.5}],
        }]}]}
        records = _records_from_agmarknet_payload(payload, filters, "Banana", state, {283}, None)
        self.assertEqual(records[0]["state"], "Kerala")
        self.assertEqual(records[0]["district"], "Thrissur")
        self.assertEqual(records[0]["modal_price"], 2700)
        self.assertEqual(records[0]["_source"], "AGMARKNET live portal")


if __name__ == "__main__":
    unittest.main()
