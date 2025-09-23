import backtrader as bt
import os


class MACrossRSISell(bt.Strategy):
    params = dict(
        fast=5,              # short MA
        slow=20,             # long  MA
        rsi_period=14,
        rsi_sell=70,         # sell when RSI >= 70
        stake=100            # shares/contracts per trade
    )

    def __init__(self):
        self.sma_fast = bt.ind.SMA(self.data.close, period=self.p.fast)
        self.sma_slow = bt.ind.SMA(self.data.close, period=self.p.slow)
        self.crossover = bt.ind.CrossOver(self.sma_fast, self.sma_slow)  # +1 on golden cross, -1 on death cross
        self.rsi = bt.ind.RSI(self.data.close, period=self.p.rsi_period)

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None

    def next(self):
        if self.order:
            return

        # Entry: BUY on golden cross (5 SMA crosses above 20 SMA)
        if not self.position:
            if self.crossover[0] > 0 or self.rsi[0] >= 35:
                self.order = self.buy(size=self.p.stake)

        # Exit: SELL when RSI reaches/exceeds 70
        else:
            if self.rsi[0] >= self.p.rsi_sell:
                self.order = self.close()


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # Use your existing sample file (adjust path if needed)
    datapath = os.path.join(os.path.dirname(__file__), '../datas/orcl-2014.txt')
    data = bt.feeds.BacktraderCSVData(dataname=datapath)
    cerebro.adddata(data)

    cerebro.addstrategy(MACrossRSISell, fast=5, slow=20, rsi_period=14, rsi_sell=70, stake=100)

    cerebro.broker.set_cash(10000)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)  # optional: external sizer; remove if you prefer strategy stake

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final   Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()
