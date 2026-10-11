import unittest
from decimal import Decimal
from profit_calculator import calculate_profit

class ProfitCalculatorTests(unittest.TestCase):
    
    def test_profitable_product_passes(self):
        result = calculate_profit(
            sale_price="30.00",
            product_cost="20.00",
            return_allowance="0.50"
        )
        self.assertEqual(result.net_profit, Decimal("2.89"))
        self.assertTrue(result.qualifies)

    def test_unprofitable_product_is_rejected(self):
        result = calculate_profit(
            sale_price="25.00",
            product_cost="20.00"
        )
        self.assertLess(result.net_profit, Decimal("2.00"))
        self.assertFalse(result.qualifies)

    def test_shipping_is_deducted(self):
        result = calculate_profit(
            sale_price="30.00",
            product_cost="20.00",
            seller_shipping="3.00"
        )
        self.assertEqual(result.net_profit, Decimal("0.89"))

    def test_negative_cost_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_profit(
                sale_price="30.00",
                product_cost="-5.00"
            )

if __name__ == "__main__":
    unittest.main()
