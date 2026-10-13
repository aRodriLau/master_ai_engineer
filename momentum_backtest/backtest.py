"""Motore di backtest mensile con costi di transazione."""

import pandas as pd


def run_backtest(monthly_prices, target_weights, cost_bps=10.0, cash_rate=0.0):
    """Rendimenti mensili netti della strategia.

    - I pesi decisi a fine mese t vengono applicati ai rendimenti del mese t+1
      (shift di 1): niente look-ahead bias.
    - Il turnover è misurato rispetto ai pesi "derivati" dall'andamento del
      mese precedente, quindi include anche i ribilanciamenti.
    - `cost_bps`: costo per ogni euro scambiato (commissioni + spread), in punti base.
    - `cash_rate`: rendimento annuo della liquidità non investita.
    """
    asset_rets = monthly_prices.pct_change().fillna(0.0)
    weights = target_weights.shift(1).fillna(0.0)
    cash_ret = (1 + cash_rate) ** (1 / 12) - 1

    gross, costs = [], []
    drifted = pd.Series(0.0, index=monthly_prices.columns)
    for date in asset_rets.index:
        w = weights.loc[date]
        turnover = (w - drifted).abs().sum()
        cost = turnover * cost_bps / 10_000
        r_assets = (w * asset_rets.loc[date]).sum()
        r = r_assets + (1 - w.sum()) * cash_ret
        gross.append(r)
        costs.append(cost)
        # pesi a fine mese dopo il movimento dei prezzi
        grown = w * (1 + asset_rets.loc[date])
        drifted = grown / (1 + r) if (1 + r) != 0 else grown

    gross = pd.Series(gross, index=asset_rets.index)
    costs = pd.Series(costs, index=asset_rets.index)
    return (gross - costs).rename("returns")
