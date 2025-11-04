import unittest
from ebayapi import EbayAPI
import os

class TestEbayAPI(unittest.TestCase):
    def setUp(self):
        self.api = EbayAPI('FarThings', 'FarCamera', os.path.join(os.path.dirname(__file__), '../ebay_rest.json'))

    def test_access_token(self):
        token = self.api.get_access_token()
        self.assertTrue(token)

    def test_get_orders(self):
        orders = self.api.get_orders_last_days(days=1)
        self.assertIsInstance(orders, list)

    def test_get_active_listings(self):
        listings = self.api.get_active_listings()
        self.assertIsInstance(listings, list)

if __name__ == '__main__':
    unittest.main()
