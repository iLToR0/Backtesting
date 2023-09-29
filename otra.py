import backtrader as bt
import yfinance as yf
import pandas as pd
import matplotlib as pl
import datetime as dt

class ThreeCandlePatternStrategy(bt.Strategy):
    def __init__(self):
        self.peak_prices = []  # Lista para almacenar los picos de las resistencias y sus marcas de tiempo
        self.order = None  # Variable para llevar un registro de la orden en curso
        self.current_peak = None  # Variable para llevar un registro de la resistencia actual
        self.resistance_broken = False  # Variable para rastrear si la resistencia se ha roto
        self.points_to_dollars = 20  # Valor en dólares por cada punto
        self.stop_loss_points = 20  # Puntos para el stop loss
        self.take_profit_points = 8  # Puntos para el take profit

    def check_and_remove_inactive_resistances(self):
        current_time = self.data.datetime.datetime()
        inactive_resistances = []

        for peak_price, timestamp in self.peak_prices:
            if (current_time - timestamp).total_seconds() > 390 * 60:  # 390 minutos en segundos
                inactive_resistances.append((peak_price, timestamp))

        for resistance in inactive_resistances:
            self.peak_prices.remove(resistance)

    def next(self):
        if len(self.data) < 3:
            return

        self.check_and_remove_inactive_resistances()  # Verificar y eliminar resistencias inactivas

        # Obtener las sombras (mechas) de las tres velas
        shadow_high1, shadow_low1 = self.data.high[-3], self.data.low[-3]
        shadow_high2, shadow_low2 = self.data.high[-2], self.data.low[-2]
        shadow_high3, shadow_low3 = self.data.high[-1], self.data.low[-1]

        # Verificar si la sombra de la vela central es más alta que las dos velas adyacentes
        if shadow_high2 > shadow_high1 and shadow_high2 > shadow_high3:
            if self.current_peak is None:
                current_time = self.data.datetime.datetime()
                self.current_peak = shadow_high2
                self.peak_prices.append((self.current_peak, current_time))
                return

        if self.current_peak is not None and self.data.close[0] > self.current_peak:
            self.resistance_broken = True

        if (
            self.resistance_broken and
            self.data.low[-1] is not None and self.current_peak is not None and
            self.data.low[-1] < self.current_peak and  # Verificar si la vela actual rompe la resistencia hacia abajo
            self.data.close[0] is not None and self.data.close[0] < self.current_peak  # Verificar si la vela actual cierra por debajo de la resistencia
        ):
            self.order = self.sell()

            current_time = self.data.datetime.datetime()
            if (self.current_peak, current_time) in self.peak_prices:
                self.peak_prices.remove((self.current_peak, current_time))
            
            self.current_peak = None
            self.resistance_broken = False

        if self.order:
            current_time = self.data.datetime.datetime()
            if (self.current_peak, current_time) in self.peak_prices:
                self.peak_prices.remove((self.current_peak, current_time))
            
            self.current_peak = None

        # Monitorear y cerrar la posición si se alcanzan niveles de SL o TP
        if self.order:
            current_price = self.data.close[0]
            if self.current_peak is not None:
                sl_price = self.current_peak + (self.stop_loss_points * self.points_to_dollars)
                tp_price = self.current_peak - (self.take_profit_points * self.points_to_dollars)

                if (
                    current_price is not None and
                    (current_price >= sl_price or current_price <= tp_price)
                ):
                    self.close_position()

    def close_position(self):
        if self.order:
            self.order = self.close()  # Cerrar la operación

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



