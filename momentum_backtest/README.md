# Momentum Backtest

Backtest di una strategia **dual momentum** su ETF, con costi di transazione e
**walk-forward validation** per non farsi ingannare dall'overfitting.

> ⚠️ Progetto didattico, non è una consulenza finanziaria. Un buon backtest non
> garantisce risultati futuri.

## La strategia

Ogni fine mese:
1. per ogni ETF si calcola il **momentum**: rendimento degli ultimi `lookback`
   mesi, saltando l'ultimo mese (`12-1 momentum`);
2. si comprano in parti uguali i `top_k` ETF con momentum più alto
   (**momentum relativo**);
3. un ETF viene comprato solo se il suo momentum è positivo (**momentum
   assoluto**), altrimenti quella quota resta in liquidità. È questo che, in
   teoria, protegge dai crolli come quelli del 2008 o del 2022.

Il programma confronta anche portafogli più semplici: buy & hold SPY,
equal weight, 60/40, S&P 500 con filtro di trend (media mobile a 10 mesi) e
portafogli a percentuali fisse (80/20 con obbligazioni, oro o emergenti,
70/30, 80/10/10). Per aggiungerne uno basta una riga in `FIXED_PORTFOLIOS`
dentro `main.py`.

Universo di default: `SPY` (azioni USA), `EFA` (azioni sviluppate ex-USA),
`EEM` (emergenti), `IEF` (Treasury 7-10 anni), `GLD` (oro), `VNQ` (immobiliare).

## Le trappole che il codice evita

| Trappola | Come viene gestita |
|---|---|
| **Look-ahead bias** (usare dati futuri) | i pesi decisi a fine mese *t* si applicano al mese *t+1* (`backtest.py`), e c'è un test apposito |
| **Ignorare i costi** | costo per ogni euro scambiato (`--cost-bps`), turnover calcolato sui pesi effettivi dopo il movimento dei prezzi |
| **Overfitting dei parametri** | `walk_forward.py`: sceglie `lookback` e `top_k` sui 5 anni precedenti e li usa solo sull'anno successivo |
| **Confronto ingiusto** | tutte le strategie sono confrontate sullo stesso periodo out-of-sample |

Cosa **non** è modellato: tasse (in Italia il 26% sulle plusvalenze, che con
una strategia attiva paghi a ogni vendita invece che alla fine), dividendi
tassati alla fonte, cambio EUR/USD, survivorship bias nella scelta degli ETF.

## Uso

```bash
cd momentum_backtest
pip install -r requirements.txt

python main.py                         # dati reali da Yahoo Finance dal 2005
python main.py --synthetic             # dati simulati, senza internet
python main.py --cost-bps 20 --lookback 6 --top-k 1
python main.py --tickers SPY EFA IEF --benchmark SPY
python main.py --csv prezzi.csv        # CSV con colonna Date + una colonna per ticker
python main.py --end 2023-12-31        # test di robustezza: senza gli ultimi anni
python main.py --help
```

Su Windows con Git Bash (il terminale di VS Code con `MINGW64`) usa le barre `/`:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python main.py
```

Output: tabella con CAGR, volatilità, Sharpe, max drawdown, Calmar; valore finale
di 10.000 €; parametri scelti dal walk-forward anno per anno; grafico `equity.png`.

Test:
```bash
python -m unittest discover -s tests -v
```

## Come leggere i risultati

- Guarda **Sharpe** e **max drawdown**, non solo il CAGR: rendere il 2% in più
  con un crollo del -50% non è un affare.
- Se la versione **walk-forward** va molto peggio di quella a parametri fissi, i
  parametri fissi erano probabilmente ottimizzati sul passato.
- Il benchmark da battere è un semplice **equal weight** o un ETF globale: se
  la strategia non lo batte *dopo costi e tasse*, non vale la complessità.
- Con `--synthetic` i prezzi sono simulati con fasi di trend, quindi il
  momentum lì tende a funzionare *per costruzione*. Quei numeri servono solo a
  verificare che il codice giri.

## Struttura

```
data.py          # Yahoo Finance / CSV / dati sintetici, conversione a mensile
strategy.py      # dual momentum, benchmark, portafogli fissi, filtro di trend
backtest.py      # motore di backtest con costi
metrics.py       # CAGR, volatilità, Sharpe, drawdown, Calmar
walk_forward.py  # ottimizzazione walk-forward dei parametri
main.py          # CLI
tests/           # test unitari (incluso quello anti look-ahead)
```

## Idee per continuare

- Aggiungere la tassazione italiana al 26% sulle plusvalenze realizzate
- Usare ETF UCITS quotati in Europa (es. `SWDA.MI`, `CSSPX.MI`) per un investitore italiano
- Ponderare per volatilità inversa invece che in parti uguali
- Sostituire la regola fissa con un modello ML (es. LightGBM) mantenendo lo stesso walk-forward
