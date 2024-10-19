import unittest
import pandas as pd

from stocks.backtest import backtest_strategy

class TestBacktestStrategy(unittest.TestCase):

    def test_strategy_with_rising_prices(self):
        prices = [100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150]
        initial_investment = 1000

        final_value, transactions, performance_summary = backtest_strategy(initial_investment, prices)

        self.assertGreaterEqual(final_value, initial_investment)
        self.assertGreaterEqual(len(transactions), 0)
        self.assertIn('total_return', performance_summary)
        self.assertIn('max_drawdown', performance_summary)
        self.assertIn('number_of_trades', performance_summary)
        self.assertLess(performance_summary['max_drawdown'], 100)


    def test_strategy_with_falling_prices(self):
        prices = [150, 145, 140, 135, 130, 125, 120, 115, 110, 105, 100]
        initial_investment = 1000

        final_value, transactions, performance_summary = backtest_strategy(initial_investment, prices)

        if len(transactions) > 0:
            self.assertLess(final_value, initial_investment)
        else:
        
            self.assertEqual(final_value, initial_investment)

        self.assertGreaterEqual(len(transactions), 0)

        self.assertLessEqual(performance_summary['total_return'], 0)


    def test_no_transactions(self):
        prices = [100] * 100  
        initial_investment = 1000.0

        final_value, transactions, performance_summary = backtest_strategy(initial_investment, prices)

        self.assertEqual(final_value, initial_investment)
        self.assertEqual(len(transactions), 0)

        self.assertEqual(performance_summary['total_return'], 0)

    def test_edge_case_empty_prices(self):
        prices = []
        initial_investment = 1000.0

        with self.assertRaises(IndexError):
            backtest_strategy(initial_investment, prices)

    def test_edge_case_single_price(self):
        prices = [100]
        initial_investment = 1000.0

        final_value, transactions, performance_summary = backtest_strategy(initial_investment, prices)

        self.assertEqual(final_value, initial_investment)
        self.assertEqual(len(transactions), 0)
        self.assertEqual(performance_summary['total_return'], 0)

if __name__ == '__main__':
    unittest.main()
