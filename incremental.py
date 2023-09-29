import yfinance as yf
import backtrader as bt
import matplotlib as pl
import matplotlib.pyplot as plt

class ThreeCandlePatternStrategy(bt.Strategy):
    def __init__(self):
        self.order = None
        self.peak_prices = []

    def next(self):
        if len(self.data) < 3:
            return

        # Obtener las sombras (mechas) de las tres velas
        shadow_high1, shadow_low1 = self.data.high[-3], self.data.low[-3]
        shadow_high2, shadow_low2 = self.data.high[-2], self.data.low[-2]
        shadow_high3, shadow_low3 = self.data.high[-1], self.data.low[-1]

        # Verificar si la sombra de la vela central es más alta que las dos velas adyacentes
        if shadow_high2 > shadow_high1 and shadow_high2 > shadow_high3:
            # Se encontró un patrón de tres velas con la sombra alta en la vela central
            self.peak_prices.append(shadow_high2)
            
            print(self.peak_prices)

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None

if __name__ == "__main__":
    cerebro = bt.Cerebro()

    # Agregar un feed de datos (puedes usar tus propios datos aquí)
    nasdaq_data = yf.download('NQ=F', start='2023-09-20', end='2023-09-25', interval='1m')
    feed = bt.feeds.PandasData(dataname=nasdaq_data)
    cerebro.adddata(feed)

    # Agregar la estrategia al cerebro
    cerebro.addstrategy(ThreeCandlePatternStrategy)

    # Establecer el tamaño de la posición
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Configurar el valor inicial de la cartera
    cerebro.broker.set_cash(10000)

    # Ejecutar el backtest
    cerebro.run()

    # Imprimir el valor final de la cartera
    print(f"Valor final de la cartera: {cerebro.broker.getvalue():.2f}")

    
    

    # Graficar los resultados
    cerebro.plot(style='candlestick')
