"""Walk-forward validation: si sceglie il parametro migliore sul passato
e lo si usa solo sul periodo successivo, mai visto in fase di scelta.

È il modo per non farsi ingannare da un backtest "ottimizzato" su tutto
lo storico (overfitting).
"""

import itertools

import pandas as pd

from backtest import run_backtest
from metrics import sharpe
from strategy import dual_momentum_weights


def walk_forward(
    monthly_prices,
    lookbacks=(3, 6, 9, 12),
    top_ks=(1, 2, 3),
    train_months=60,
    test_months=12,
    cost_bps=10.0,
    cash_rate=0.0,
):
    """Ritorna (rendimenti out-of-sample concatenati, parametri scelti per finestra)."""
    # I segnali usano solo dati passati e il backtest applica lo shift,
    # quindi possiamo calcolare i rendimenti di ogni combinazione una volta
    # sola e poi limitarci a scegliere sulle finestre di training.
    grid = {
        (lb, k): run_backtest(
            monthly_prices, dual_momentum_weights(monthly_prices, lb, k), cost_bps, cash_rate
        )
        for lb, k in itertools.product(lookbacks, top_ks)
    }
    warmup = max(lookbacks) + 1
    dates = monthly_prices.index

    oos, choices = [], []
    start = warmup
    while start + train_months < len(dates):
        train = dates[start : start + train_months]
        test = dates[start + train_months : start + train_months + test_months]
        best = max(grid, key=lambda p: sharpe(grid[p].loc[train]))
        oos.append(grid[best].loc[test])
        choices.append(
            {"test_start": test[0].date(), "test_end": test[-1].date(),
             "lookback": best[0], "top_k": best[1]}
        )
        start += test_months

    return pd.concat(oos).rename("walk_forward"), pd.DataFrame(choices)
