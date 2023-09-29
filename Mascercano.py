import backtrader as bt
import pandas as pd
import datetime as dt

class ThreeCandlePatternStrategy(bt.Strategy):
    params = (
        ("stop_loss", 20),  # Puntos para el stop loss
        ("take_profit", 10),
        ("pip_value", 20)  # Valor del pip o punto
    )

    def __init__(self):
        self.peak_prices = []  # Lista para almacenar los picos de las resistencias y sus marcas de tiempo
        self.orders = []  # Lista para llevar un registro de las órdenes en curso
        self.position_open = False  # Variable para rastrear si hay una posición abierta
        self.breakout_price = None  # Precio de ruptura de resistencia

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

        # Obtener las sombras (mechas) de las tres velas más recientes
        shadow_high1, shadow_low1 = self.data.high[-3], self.data.low[-3]
        shadow_high2, shadow_low2 = self.data.high[-2], self.data.low[-2]
        shadow_high3, shadow_low3 = self.data.high[-1], self.data.low[-1]

        # Verificar si la sombra de la vela central es más alta que las dos velas adyacentes
        if shadow_high2 > shadow_high1 and shadow_high2 > shadow_high3:
            current_time = self.data.datetime.datetime()
            peak_price = shadow_high2
            self.peak_prices.append((peak_price, current_time))

        # Verificar si el precio rompe una resistencia hacia arriba
        for resistance, timestamp in self.peak_prices:
            if (
                self.data.high[0] is not None and
                self.data.high[0] > resistance and
                self.breakout_price is None
            ):
                self.breakout_price = resistance
                continue

        # Verificar si el precio rompe la misma resistencia hacia abajo y abrir una posición si corresponde
        if (
            self.breakout_price is not None and
            self.data.close[0] is not None and
            self.data.close[0] < self.breakout_price and
            not self.position_open
        ):
            self.orders.append(self.sell())
            self.position_open = True
            self.breakout_price = None

        # Monitorear y cerrar las posiciones si se alcanzan niveles de SL o TP
        for i in range(len(self.orders)):
            current_price = self.data.close[0]
            sl_price = self.peak_prices[i][0] + (self.params.stop_loss * self.params.pip_value)
            tp_price = self.peak_prices[i][0] - (self.params.take_profit * self.params.pip_value)

            if (
                current_price is not None and
                (current_price >= sl_price or current_price <= tp_price)
            ):
                self.close_position(i)

    def close_position(self, index):
        if index < len(self.orders):
            self.orders[index] = self.close()  # Cerrar la operación
            self.position_open = False

if __name__ == "__main__":
    cerebro = bt.Cerebro()

    # Agregar un feed de datos (puedes usar tus propios datos aquí)
    archivo_csv = 'data.csv'

    # Cargar los datos en un DataFrame de pandas
    df = pd.read_csv(archivo_csv, sep=';', header=None, names=['datetime', 'open', 'high', 'low', 'close', 'volume'])

    # Añadir milisegundos a la columna 'datetime'
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d %H%M%S')

    # Establecer la columna 'datetime' como índice de tiempo
    df.set_index('datetime', inplace=True)

    # Convertir las columnas numéricas a tipo float
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)

    data_feed = bt.feeds.PandasData(dataname=df)
    
    cerebro.adddata(data_feed)
    
    # Establecer el tamaño del pip (tamaño del punto)
    pip_value = 20  # Ajusta este valor según tu mercado

    # Agregar la estrategia al cerebro con el valor del pip
    cerebro.addstrategy(ThreeCandlePatternStrategy, pip_value=pip_value)

    # Establecer el valor inicial de la cartera
    cerebro.broker.set_cash(10000)

    # Ejecutar el backtest
    cerebro.run()

    # Imprimir el valor final de la cartera
    final_portfolio_value = cerebro.broker.getvalue()
    print(f"Valor final de la cartera: {final_portfolio_value:.2f}")
    
    # Graficar los resultados
    cerebro.plot(style='candlestick')

