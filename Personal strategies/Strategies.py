import backtrader as bt

class MACrossRSISell(bt.Strategy):
    params = dict(
        fast=5,              # short MA
        slow=20,             # long  MA
        rsi_period=14,
        rsi_sell=70,
        #slow2=200,          # sell when RSI >= 70
    )

    def __init__(self):
        self.sma_fast = bt.ind.SMA(self.data.close, period=self.p.fast)
        self.sma_slow = bt.ind.SMA(self.data.close, period=self.p.slow)
        self.crossover = bt.ind.CrossOver(self.sma_fast, self.sma_slow)
        self.rsi = bt.ind.RSI(self.data.close, period=self.p.rsi_period)
        #self.sma_slow2 = bt.ind.SMA(self.data.close, period=self.p.slow2)

        self.order = None

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None

    def next(self):
        if self.order:
            return

        # Entry: Golden cross OR RSI >= 35
        if not self.position:
            #if(
            #(self.crossover[0] > 0 and self.rsi[0] <= 45)
            #or (self.data.close[0] < self.sma_slow2[0])
            #or (self.rsi[0] <= 35) ):
            
            if (self.crossover[0] > 0 and self.rsi[0] <= 45) or self.rsi[0] <= 35:
                self.order = self.buy()

        # Exit: RSI >= 70
        else:
            if self.rsi[0] >= self.p.rsi_sell:
                self.order = self.close()
