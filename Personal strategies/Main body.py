import backtrader as bt
import os
from Strategies import MACrossRSISell

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


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # --- Data ---
    datapath = os.path.join(os.path.dirname(__file__), '../datas/STM.csv')
    data = bt.feeds.GenericCSVData(
    dataname='datas/STM.csv',
    dtformat=('%Y-%m-%d'),
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=5,
    openinterest=6,
    # If you have headers, set this:
    header=0,
)

    cerebro.adddata(data)

    # --- Strategy ---
    cerebro.addstrategy(MACrossRSISell, fast=5, slow=20, rsi_period=14, rsi_sell=70)

    # --- Broker / Cash / Commission ---
    initial_cash = 10000.0
    cerebro.broker.set_cash(initial_cash)
    cerebro.broker.setcommission(commission=0.001) # 0.9% per trade

    # --- Custom position sizing: X% of cash ---
    cerebro.addsizer(PercentSizer, perc=0.5)  # Invest 99% of cash each trade

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    final_value = cerebro.broker.getvalue()
    print('Final   Portfolio Value: %.2f' % final_value)
    print(f'Final gain (%): {((final_value - initial_cash) / initial_cash) * 100:.2f}%')

    cerebro.plot()
