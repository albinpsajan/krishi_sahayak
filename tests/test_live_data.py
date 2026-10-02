import unittest
from unittest.mock import patch
from services.assistant_intent_service import detect_intent, reply_for
from services.market_price_service import get_prices

class LiveDataTests(unittest.TestCase):
    def test_assistant_intents_support_localized_keywords(self):
        self.assertEqual(detect_intent('what is the weather today'), 'weather')
        self.assertEqual(detect_intent('केले का भाव'), 'market_price')
        self.assertIn('weather', reply_for('weather', 'en').lower())

    @patch('services.market_price_service.fetch_records', side_effect=OSError('offline'))
    def test_market_feed_failure_is_explicitly_unavailable(self, fetch):
        with patch.dict('os.environ', {'DATA_GOV_API_KEY': ''}):
            result = get_prices('banana', 'Kerala', 'Thrissur')
        self.assertFalse(result['available'])
        self.assertIsNone(result['modal_price'])
        self.assertTrue(result['warning'])

if __name__ == '__main__':
    unittest.main()
