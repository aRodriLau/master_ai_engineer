"""Strategia "dual momentum" e benchmark, su dati mensili.

Regola: a fine mese si calcola il momentum di ogni asset (rendimento degli
ultimi `lookback` mesi, saltando l'ultimo mese per evitare l'effetto di
reversal di breve periodo). Si comprano in parti uguali i `top_k` asset
con il momentum più alto, ma solo se positivo (momentum assoluto); la
quota rimanente resta in liquidità.
"""

import pandas as pd


def momentum(monthly_prices, lookback=12, skip=1):
    return monthly_prices.shift(skip) / monthly_prices.shift(lookback) - 1


def dual_momentum_weights(monthly_prices, lookback=12, top_k=2, skip=1):
    """Pesi target decisi a fine mese t (da applicare nel mese t+1)."""
    mom = momentum(monthly_prices, lookback, skip)
    ranks = mom.rank(axis=1, ascending=False)
    selected = (ranks <= top_k) & (mom > 0)
    weights = selected.astype(float) / top_k
    # finché non c'è abbastanza storia per il segnale si sta in liquidità
    return weights.where(mom.notna().all(axis=1), 0.0, axis=0)


def buy_and_hold_weights(monthly_prices, ticker):
    w = pd.DataFrame(0.0, index=monthly_prices.index, columns=monthly_prices.columns)
    w[ticker] = 1.0
    return w


def equal_weight_weights(monthly_prices):
    n = monthly_prices.shape[1]
    return pd.DataFrame(1.0 / n, index=monthly_prices.index, columns=monthly_prices.columns)


def fixed_weights(monthly_prices, allocation):
    """Portafoglio a percentuali fisse, es. {"SPY": 0.8, "IEF": 0.2}."""
    missing = set(allocation) - set(monthly_prices.columns)
    if missing:
        raise ValueError(f"Ticker non presenti nei dati: {sorted(missing)}")
    w = pd.DataFrame(0.0, index=monthly_prices.index, columns=monthly_prices.columns)
    for ticker, share in allocation.items():
        w[ticker] = share
    return w


def sixty_forty_weights(monthly_prices, stocks="SPY", bonds="IEF"):
    return fixed_weights(monthly_prices, {stocks: 0.6, bonds: 0.4})


def trend_filter_weights(monthly_prices, risky="SPY", safe="IEF", months=10):
    """Sull'S&P 500 se sopra la media mobile a 10 mesi, altrimenti obbligazioni."""
    price = monthly_prices[risky]
    above = price > price.rolling(months).mean()
    w = pd.DataFrame(0.0, index=monthly_prices.index, columns=monthly_prices.columns)
    w[risky] = above.astype(float)
    w[safe] = 1.0 - w[risky]
    return w
