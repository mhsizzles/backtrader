import backtrader as bt
import os


# ---- Custom Sizer: invest X% of cash each trade ----
class PercentSizer(bt.Sizer):
    params = (("perc", 0.5),)  # 50% of cash by default

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            # invest % of cash in units of shares
            target_value = cash * self.p.perc
            size = int(target_value / data.close[0])  # floor to whole shares
            return size
        else:
            return self.broker.getposition(data).size  # sell all


class MACrossRSISell(bt.Strategy):
    params = dict(
        fast=5,              # short MA
        slow=20,             # long  MA
        rsi_period=14,
        rsi_sell=70          # sell when RSI >= 70
    )

    def __init__(self):
        self.sma_fast = bt.ind.SMA(self.data.close, period=self.p.fast)
        self.sma_slow = bt.ind.SMA(self.data.close, period=self.p.slow)
        self.crossover = bt.ind.CrossOver(self.sma_fast, self.sma_slow)
        self.rsi = bt.ind.RSI(self.data.close, period=self.p.rsi_period)

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None

    def next(self):
        if self.order:
            return

        # Entry: Golden cross OR RSI >= 35
        if not self.position:
            if self.crossover[0] > 0 or self.rsi[0] >= 35:
                self.order = self.buy()

        # Exit: RSI >= 70
        else:
            if self.rsi[0] >= self.p.rsi_sell:
                self.order = self.close()


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # --- Data ---
    datapath = os.path.join(os.path.dirname(__file__), '../datas/STM.csv')
    data = bt.feeds.BacktraderCSVData(dataname=datapath)
    cerebro.adddata(data)

    # --- Strategy ---
    cerebro.addstrategy(MACrossRSISell, fast=5, slow=20, rsi_period=14, rsi_sell=70)

    # --- Broker / Cash / Commission ---
    initial_cash = 80*12
    cerebro.broker.set_cash(initial_cash)
    cerebro.broker.setcommission(commission=0.001) # 0.9% per trade

    # --- Custom position sizing: X% of cash ---
    cerebro.addsizer(PercentSizer, perc=0.99)  # Invest 99% of cash each trade

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    final_value = cerebro.broker.getvalue()
    print('Final   Portfolio Value: %.2f' % final_value)
    print(f'Final gain (%): {((final_value - initial_cash) / initial_cash) * 100:.2f}%')

    #cerebro.plot()
