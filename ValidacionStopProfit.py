import backtrader as bt
import pandas as pd
import datetime as dt

class ThreeCandlePatternStrategy(bt.Strategy):
    def __init__(self):
        self.resistencias = []  # Lista para almacenar los picos de las resistencias y sus marcas de tiempo
        self.resistenciaRota = None
        self.resistenciaeliminar = []
        self.stop_loss_puntos = 2
        self.take_profit_puntos = 2
        self.is_trade_open = False  #
        self.valorContrato = 20
        

    def next(self):
        if len(self.data) < 3:
            return

        # Obtener las sombras (mechas) de las tres velas más recientes
        shadow_high1, shadow_low1 = self.data.high[-3], self.data.low[-3]
        shadow_high2, shadow_low2 = self.data.high[-2], self.data.low[-2]
        shadow_high3, shadow_low3 = self.data.high[-1], self.data.low[-1]

        # Verificar si la sombra de la vela central es más alta que las dos velas adyacentes
        if shadow_high2 > shadow_high1 and shadow_high2 > shadow_high3:
            # Almacenar el pico high de la vela central en la lista
            self.resistencias.append(shadow_high2)
        if not self.is_trade_open:
            for resistencia in self.resistencias.copy():
                if self.data.high[-1] > resistencia and self.data.close[-1] <= resistencia:
                    self.resistenciaeliminar.append(resistencia)
                elif self.data.high[-1] > resistencia and self.data.close[-1] > resistencia:
                    if self.data.close[0] >= resistencia:
                        self.resistenciaeliminar.append(resistencia)
                    elif self.data.close[0] < resistencia:
                        self.sell()
                        print(self.data.datetime[0])
                        self.is_trade_open = True
                        stop_loss_price = self.data.open[1] + 20  # Calcula el precio de stop loss en dólares reales
                        take_profit_price = self.data.open[1] - 20  # Calcula el precio de take profit en dólares reales
                       
                        
                        self.stop_loss_order = self.buy(
                                exectype=bt.Order.Stop, price=stop_loss_price)


                        self.take_profit_order = self.buy(
                                exectype=bt.Order.Limit, price=take_profit_price)
                        
            for resistencia in self.resistenciaeliminar:
                if resistencia in self.resistencias:
                    self.resistencias.remove(resistencia)

    def notify_trade(self, trade):
        if trade.isclosed:
            self.is_trade_open = False           

if __name__ == "__main__":
    cerebro = bt.Cerebro()

    # Agregar un feed de datos (puedes usar tus propios datos aquí)
    archivo_csv = 'dataaa.csv'

    # Cargar los datos en un DataFrame de pandas
    df = pd.read_csv(archivo_csv, sep=';', header=None, names=['datetime', 'open', 'high', 'low', 'close', 'volume'])

    # Añadir milisegundos a la columna 'datetime'
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d%m%Y %H%M%S')

    # Establecer la columna 'datetime' como índice de tiempo
    df.set_index('datetime', inplace=True)
    df = df[::-1]

    # Convertir las columnas numéricas a tipo float
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)

    data_feed = bt.feeds.PandasData(dataname=df)

    cerebro.adddata(data_feed)

    # Agregar la estrategia al cerebro
    cerebro.addstrategy(ThreeCandlePatternStrategy)
    
    # Ejecutar el backtest
    cerebro.run()

    print("Picos detectados:")
    for peak in cerebro.runstrats[0][0].resistencias:
        print(f"Pico: {peak:.2f}")

        plotlines = dict(
    buy=dict(marker='^', markersize=8.0, color='lime', fillstyle='full'),
    sell=dict(marker='v', markersize=8.0, color='red', fillstyle='full')
)

    cerebro.plot(style="candlestick")
