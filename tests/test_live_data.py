import unittest
from services.assistant_intent_service import detect_intent, reply_for
from services.market_price_service import get_prices

class LiveDataTests(unittest.TestCase):
    def test_assistant_intents_support_localized_keywords(self):
        self.assertEqual(detect_intent('what is the weather today'), 'weather')
        self.assertEqual(detect_intent('केले का भाव'), 'market_price')
        self.assertIn('weather', reply_for('weather', 'en').lower())

    def test_market_fallback_has_change_and_suggestion(self):
        result = get_prices('banana', 'Kerala', 'Thrissur')
        self.assertIn('modal_price', result)
        self.assertIn('change', result)
        self.assertTrue(result['suggestion'])

if __name__ == '__main__':
    unittest.main()
