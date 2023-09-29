import backtrader as bt
import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib as pl

class ThreeCandlePatternStrategy(bt.Strategy):
    def __init__(self):
        self.peak_prices = []  # Lista para almacenar los picos de las resistencias
        self.order = None  # Variable para llevar un registro de la orden en curso
        self.current_peak = None  # Variable para llevar un registro de la resistencia actual
        self.resistance_broken = False  # Variable para rastrear si la resistencia se ha roto

    def next(self):
        if len(self.data) < 3:
            return

        # Obtener las sombras (mechas) de las tres velas
        shadow_high1, shadow_low1 = self.data.high[-3], self.data.low[-3]
        shadow_high2, shadow_low2 = self.data.high[-2], self.data.low[-2]
        shadow_high3, shadow_low3 = self.data.high[-1], self.data.low[-1]

        # Verificar si la sombra de la vela central es más alta que las dos velas adyacentes
        if shadow_high2 > shadow_high1 and shadow_high2 > shadow_high3:
            if self.current_peak is None:
                self.current_peak = shadow_high2
                return

        if self.current_peak is not None and self.data.close[0] > self.current_peak:
            self.resistance_broken = True

        if (
            self.resistance_broken and
            self.data.close[-1] < self.current_peak
        ):
            self.order = self.sell()

            if self.current_peak in self.peak_prices:
                self.peak_prices.remove(self.current_peak)
            
            self.current_peak = None
            self.resistance_broken = False

        if self.current_peak is not None and not self.resistance_broken:
            if self.current_peak in self.peak_prices:
                self.peak_prices.remove(self.current_peak)
            
            self.current_peak = None

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

