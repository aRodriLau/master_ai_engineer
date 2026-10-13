"""Caricamento dei prezzi: Yahoo Finance, file CSV oppure dati sintetici."""

import numpy as np
import pandas as pd


def load_yahoo(tickers, start, end=None):
    """Scarica i prezzi di chiusura aggiustati (dividendi inclusi) da Yahoo Finance."""
    import yfinance as yf

    data = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    if data.empty:
        raise RuntimeError("Nessun dato scaricato da Yahoo Finance")
    prices = data["Close"]
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(tickers[0])
    return prices.dropna(how="all")


def load_csv(path):
    """CSV con colonna 'Date' e una colonna di prezzi per ogni ticker."""
    return pd.read_csv(path, index_col="Date", parse_dates=True).sort_index()


def synthetic_prices(tickers, start="2005-01-01", end="2025-12-31", seed=42):
    """Prezzi giornalieri simulati (moto browniano geometrico con regimi di trend).

    Servono solo per provare il codice senza connessione: NON dicono nulla
    sulla bontà della strategia sui mercati reali.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start, end)
    n = len(dates)
    prices = {}
    for t in tickers:
        vol = rng.uniform(0.10, 0.25) / np.sqrt(252)
        # il drift cambia ogni ~6 mesi per simulare fasi di trend
        regimes = np.repeat(rng.normal(0.06, 0.15, n // 126 + 1), 126)[:n] / 252
        rets = regimes + rng.normal(0, vol, n)
        prices[t] = 100 * np.exp(np.cumsum(rets))
    return pd.DataFrame(prices, index=dates)


def to_monthly(prices):
    """Ultimo prezzo di ogni mese."""
    return prices.resample("ME").last().dropna(how="all")
