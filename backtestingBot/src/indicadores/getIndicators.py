import backtrader as bt
import yfinance as yf
import matplotlib.pyplot as plt

class MiEstrategia(bt.Strategy):
 
    def __init__(self):
        ema200 = bt.ind.EMA(period=200)
        ema20 = bt.ind.EMA(period=20)
        self.crossover = bt.indicators.CrossOver(ema200, ema20)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                print(self.crossover > 0)
                self.sell()
        elif self.crossover < 0:
                
            self.close()

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    nasdaq_data = yf.download('NQ=F', start='2023-09-10', end='2023-09-25', interval='2m')
    feed = bt.feeds.PandasData(dataname=nasdaq_data)
    cerebro.adddata(feed)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=50)
    cerebro.addstrategy(MiEstrategia)

    cerebro.run()
    cerebro.plot()
