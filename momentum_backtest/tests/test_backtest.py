import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backtest import run_backtest  # noqa: E402
from metrics import cagr, max_drawdown  # noqa: E402
from strategy import buy_and_hold_weights, dual_momentum_weights  # noqa: E402


def monthly(values):
    idx = pd.date_range("2020-01-31", periods=len(values[next(iter(values))]), freq="ME")
    return pd.DataFrame(values, index=idx)


class TestBacktest(unittest.TestCase):
    def test_buy_and_hold_matches_asset_without_costs(self):
        prices = monthly({"A": [100, 110, 99, 120], "B": [100, 100, 100, 100]})
        r = run_backtest(prices, buy_and_hold_weights(prices, "A"), cost_bps=0)
        # il primo mese si decide il peso, si è investiti dal secondo
        self.assertAlmostEqual((1 + r).prod(), 120 / 100)

    def test_no_look_ahead(self):
        # cambiare un prezzo futuro non deve cambiare i pesi decisi prima
        rng = np.random.default_rng(0)
        base = monthly({t: 100 * np.cumprod(1 + rng.normal(0.01, 0.05, 40)) for t in "ABC"})
        altered = base.copy()
        altered.iloc[-1] *= 3
        w1 = dual_momentum_weights(base, 6, 1)
        w2 = dual_momentum_weights(altered, 6, 1)
        pd.testing.assert_frame_equal(w1.iloc[:-1], w2.iloc[:-1])

    def test_negative_momentum_goes_to_cash(self):
        prices = monthly({"A": list(range(200, 180, -1)), "B": list(range(100, 80, -1))})
        w = dual_momentum_weights(prices, lookback=3, top_k=1)
        self.assertEqual(w.values.sum(), 0)

    def test_costs_reduce_returns(self):
        prices = monthly({"A": [100, 110, 99, 120], "B": [100, 101, 102, 103]})
        w = buy_and_hold_weights(prices, "A")
        self.assertLess(run_backtest(prices, w, 50).sum(), run_backtest(prices, w, 0).sum())

    def test_metrics(self):
        r = pd.Series([0.1, -0.5, 0.2] + [0.0] * 9)
        self.assertAlmostEqual(max_drawdown(r), -0.5)
        self.assertAlmostEqual(cagr(r), 1.1 * 0.5 * 1.2 - 1)


if __name__ == "__main__":
    unittest.main()
