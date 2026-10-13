"""Metriche di performance su rendimenti mensili."""

import numpy as np
import pandas as pd


def equity_curve(returns, initial=10_000):
    return initial * (1 + returns).cumprod()


def cagr(returns):
    years = len(returns) / 12
    return (1 + returns).prod() ** (1 / years) - 1 if years > 0 else np.nan


def volatility(returns):
    return returns.std() * np.sqrt(12)


def sharpe(returns, rf=0.0):
    excess = returns - ((1 + rf) ** (1 / 12) - 1)
    std = excess.std()
    return excess.mean() / std * np.sqrt(12) if std > 0 else np.nan


def max_drawdown(returns):
    curve = (1 + returns).cumprod()
    return (curve / curve.cummax() - 1).min()


def summary(returns, name=None):
    mdd = max_drawdown(returns)
    c = cagr(returns)
    return pd.Series(
        {
            "CAGR": c,
            "Volatilità": volatility(returns),
            "Sharpe": sharpe(returns),
            "Max drawdown": mdd,
            "Calmar": c / abs(mdd) if mdd < 0 else np.nan,
            "Mesi positivi": (returns > 0).mean(),
        },
        name=name,
    )
