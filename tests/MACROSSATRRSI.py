import backtrader as bt
import os


class MACrossRSI_ATRFilter(bt.Strategy):
    params = dict(
        # Signals
        fast=5, slow=20, slow2=200,         # SMAs (5/20 cross, 200 as trend context)
        rsi_period=14, rsi_sell=70,         # Exit when RSI >= 70

        # Volatility filter
        atr_period=14,
        atr_min_pct=0.02,                   # require ATR >= 1% of price
        atr_max_pct=None,                   # optional cap, e.g. 0.05 for <= 5%

        # Sizing
        stake=100
    )

    def __init__(self):
        # Indicators
        self.sma_fast = bt.ind.SMA(self.data.close, period=self.p.fast)
        self.sma_slow = bt.ind.SMA(self.data.close, period=self.p.slow)
        self.sma_slow2 = bt.ind.SMA(self.data.close, period=self.p.slow2)
        self.crossover = bt.ind.CrossOver(self.sma_fast, self.sma_slow)
        self.rsi = bt.ind.RSI(self.data.close, period=self.p.rsi_period)

        self.atr = bt.ind.ATR(self.data, period=self.p.atr_period)
        # Volatility ratio (dimensionless): ATR as % of price
        self.atr_ratio = self.atr / self.data.close

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None

    def _passes_atr_filter(self):
        r = float(self.atr_ratio[0])
        if r < self.p.atr_min_pct:
            return False
        if self.p.atr_max_pct is not None and r > self.p.atr_max_pct:
            return False
        return True

    def next(self):
        if self.order:
            return

        if not self.position:
            # Entry: (Golden cross OR price > 200SMA OR RSI < 30) AND ATR filter
            if (
                (self.crossover[0] > 0 or
                 self.data.close[0] > self.sma_slow2[0] or
                 self.rsi[0] < 30)
                and self._passes_atr_filter()
            ):
                self.order = self.buy()  # size set by sizer
        else:
            # Exit: RSI >= rsi_sell
            if self.rsi[0] >= self.p.rsi_sell:
                self.order = self.close()


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # --- Data ---
    datapath = os.path.join(os.path.dirname(__file__), '../datas/orcl-2014.txt')
    data = bt.feeds.BacktraderCSVData(dataname=datapath)
    cerebro.adddata(data)

    # --- Strategy ---
    cerebro.addstrategy(
        MACrossRSI_ATRFilter,
        fast=5, slow=20, slow2=200,
        rsi_period=14, rsi_sell=70,
        atr_period=14, atr_min_pct=0.01,  # try 0.005–0.02 (0.5%–2%)
        atr_max_pct=None                  # e.g., set to 0.05 to avoid >5% daily ATR
    )

    # --- Broker / Cash / Costs ---
    initial_cash = 10000
    cerebro.broker.set_cash(initial_cash)
    cerebro.broker.setcommission(commission=0.001)  # 0.1% per trade

    # --- Position sizing ---
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
    cerebro.run()
    final_value = cerebro.broker.getvalue()
    print(f'Final   Portfolio Value: {final_value:.2f}')
    print(f'Final gain (%): {((final_value - initial_cash) / initial_cash) * 100:.2f}%')

    cerebro.plot()
