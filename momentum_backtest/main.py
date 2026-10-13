"""Backtest di una strategia dual momentum su ETF, con walk-forward validation.

Esempi:
    python main.py                          # dati reali da Yahoo Finance
    python main.py --synthetic              # dati simulati (senza internet)
    python main.py --csv prezzi.csv --benchmark SPY
"""

import argparse

import pandas as pd

from backtest import run_backtest
from data import load_csv, load_yahoo, synthetic_prices, to_monthly
from metrics import equity_curve, summary
from strategy import buy_and_hold_weights, dual_momentum_weights, equal_weight_weights
from walk_forward import walk_forward

# Azioni USA, azioni sviluppate ex-USA, emergenti, Treasury 7-10 anni, oro, immobiliare
DEFAULT_TICKERS = ["SPY", "EFA", "EEM", "IEF", "GLD", "VNQ"]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS)
    p.add_argument("--benchmark", default="SPY")
    p.add_argument("--start", default="2005-01-01")
    p.add_argument("--end", default=None)
    p.add_argument("--csv", help="file CSV di prezzi invece di Yahoo Finance")
    p.add_argument("--synthetic", action="store_true", help="usa prezzi simulati")
    p.add_argument("--cost-bps", type=float, default=10.0, help="costo per operazione in punti base")
    p.add_argument("--cash-rate", type=float, default=0.02, help="rendimento annuo della liquidità")
    p.add_argument("--lookback", type=int, default=12, help="lookback della strategia a parametri fissi")
    p.add_argument("--top-k", type=int, default=2, help="numero di asset da tenere")
    p.add_argument("--plot", default="equity.png", help="file del grafico ('' per disattivarlo)")
    return p.parse_args()


def load_prices(args):
    if args.synthetic:
        return synthetic_prices(args.tickers, args.start, args.end or "2025-12-31")
    if args.csv:
        return load_csv(args.csv)
    return load_yahoo(args.tickers, args.start, args.end)


def main():
    args = parse_args()
    prices = load_prices(args).dropna()
    monthly = to_monthly(prices)
    print(f"Dati: {list(monthly.columns)}  {monthly.index[0].date()} -> {monthly.index[-1].date()} "
          f"({len(monthly)} mesi)\n")

    bt = lambda w: run_backtest(monthly, w, args.cost_bps, args.cash_rate)
    wf_returns, choices = walk_forward(monthly, cost_bps=args.cost_bps, cash_rate=args.cash_rate)

    strategies = {
        f"Dual momentum ({args.lookback}m, top {args.top_k})":
            bt(dual_momentum_weights(monthly, args.lookback, args.top_k)),
        "Dual momentum walk-forward": wf_returns,
        f"Buy & hold {args.benchmark}": bt(buy_and_hold_weights(monthly, args.benchmark)),
        "Equal weight (ribil. mensile)": bt(equal_weight_weights(monthly)),
    }
    # Confronto solo sul periodo out-of-sample, uguale per tutti
    oos = wf_returns.index
    strategies = {name: r.loc[oos] for name, r in strategies.items()}

    table = pd.DataFrame([summary(r, name) for name, r in strategies.items()])
    pct = ["CAGR", "Volatilità", "Max drawdown", "Mesi positivi"]
    fmt = table.copy()
    fmt[pct] = fmt[pct].map(lambda x: f"{x:.1%}")
    fmt[["Sharpe", "Calmar"]] = fmt[["Sharpe", "Calmar"]].map(lambda x: f"{x:.2f}")
    print(f"Periodo out-of-sample: {oos[0].date()} -> {oos[-1].date()}  "
          f"(costi {args.cost_bps:g} bps, liquidità {args.cash_rate:.1%}/anno)\n")
    print(fmt.to_string())

    curves = pd.DataFrame({n: equity_curve(r) for n, r in strategies.items()})
    print("\n10.000 € iniziali diventano (al lordo delle tasse):")
    print(curves.iloc[-1].map(lambda x: f"{x:,.0f} €").to_string())

    print("\nParametri scelti dal walk-forward per ogni anno:")
    print(choices.to_string(index=False))

    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        ax = curves.plot(figsize=(11, 6), logy=True, title="Equity (scala log, out-of-sample)")
        ax.set_ylabel("€")
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(args.plot, dpi=120)
        print(f"\nGrafico salvato in {args.plot}")


if __name__ == "__main__":
    main()
