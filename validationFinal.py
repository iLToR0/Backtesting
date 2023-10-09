import backtrader as bt
import pandas as pd
import datetime as dt


class ThreeCandlePatternStrategy(bt.Strategy):

    
    
   
    def __init__(self):
        self.resistenciaSell = []  # Lista para almacenar los picos de las resistenciaSell y sus marcas de tiempo
        self.resistenciaBuy = []
        self.resistenciasAEliminar = []
        self.valor_contrato = 20
        self.StopLoss = 1
        self.TakeProfit = 1
        self.vela = 0
        self.valorInicialCartera = 0
        self.valorFinalCartera=0
        
        
        
    def start(self):
        self.valorInicialCartera = self.broker.getvalue()
        
    
    def stop(self):
        self.valorFinalCartera = self.broker.getvalue()
        

    def next(self):
 
        if len(self.data) < 3:
            return
        self.vela += 1
        #revisar que se tengan que marcar resistencias mientras haya una posicion abierta
        self.marcarResistencias()
        
        #Sell
        self.analizarSell()     
        self.analizarBuy()


        self.eliminarResistencias()             
                                

    


    def analizarSell(self):
        #define si ya se abrio una posicion en esta vela
        self.operacionAbierta = False

        for resistencia in self.resistenciaSell.copy():
            if not self.position: 

                if self.data.high[0] > resistencia and self.data.close[0] <= resistencia:
                    self.resistenciasAEliminar.append(resistencia)

                elif self.data.high[0] > resistencia and self.data.close[0] > resistencia:

                    if self.data.close[1] >= resistencia:
                        self.resistenciasAEliminar.append(resistencia)

                    elif self.data.close[1] < resistencia:
                            
                            if self.operacionAbierta == False:
                                self.operacionAbierta = True
                                self.sell(exectype=bt.Order.Limit,price=self.data.open[2])
                            
                            self.resistenciasAEliminar.append(resistencia)

            else:
                if self.data.high[0] > resistencia:
                    self.resistenciasAEliminar.append(resistencia)

    def analizarBuy(self):
        #define si ya se abrio una posicion en esta vela
        self.operacionAbierta = False

        for resistencia in self.resistenciaBuy.copy():
            if not self.position: 

                if self.data.low[0] < resistencia and self.data.close[0] >= resistencia:
                    self.resistenciasAEliminar.append(resistencia)

                elif self.data.low[0] < resistencia and self.data.close[0] < resistencia:
                    
                    if self.data.close[1] <= resistencia:
                        self.resistenciasAEliminar.append(resistencia)

                    elif self.data.close[1] > resistencia:
                            
                            if self.operacionAbierta == False:
                                self.operacionAbierta = True
                                self.buy(exectype=bt.Order.Stop,price=self.data.open[2])
                            
                            self.resistenciasAEliminar.append(resistencia)

            else:
                if self.data.low[0] < resistencia:
                    self.resistenciasAEliminar.append(resistencia)




    def notify_order(self, order):
        s = order.Status
        print(s[order.status])

        if order.status in [order.Completed]:

        
            if order.isbuy():
                print(f"Compra ejecutada - Precio: {order.executed.price}, Comisión: {order.executed.comm}")

                if self.position:
                    #Set ST y TK
                    oco = self.sell(exectype=bt.Order.Stop,price=order.executed.price - (self.StopLoss * self.valor_contrato) )
                    self.sell(oco=oco,exectype=bt.Order.Limit,price=order.executed.price + (self.TakeProfit * self.valor_contrato))

            elif order.issell():
                print(f"Venta ejecutada - Precio: {order.executed.price}, Comisión: {order.executed.comm}")

                if self.position:
                    #Set ST y TK
                    oco = self.buy(exectype=bt.Order.Stop,price=order.executed.price + (self.StopLoss * self.valor_contrato) )
                    self.buy(oco=oco, exectype=bt.Order.Limit,price=order.executed.price - (self.TakeProfit * self.valor_contrato))

    def marcarResistencias(self):
        #
        shadow_high1, shadow_low1 = self.data.high[-3], self.data.low[-3]
        shadow_high2, shadow_low2 = self.data.high[-2], self.data.low[-2]
        shadow_high3, shadow_low3 = self.data.high[-1], self.data.low[-1]


    #marcar resistencias mientas hay una posicion abierta?

        # Verificar si la sombra de la vela central es más alta que las dos velas adyacentes
        self.marcarResistenciasSell(shadow_high1, shadow_high2, shadow_high3)
        self.marcarResistenciasBuy(shadow_low1, shadow_low2, shadow_low3)






    def marcarResistenciasSell(self, shadow_high1, shadow_high2, shadow_high3):
        if shadow_high2 > shadow_high1 and shadow_high2 > shadow_high3:
            # Almacenar el pico high de la vela central en la lista
            self.resistenciaSell.append(shadow_high2)

    def marcarResistenciasBuy(self, shadow_low1, shadow_low2, shadow_low3):
        if shadow_low2 < shadow_low1 and shadow_low2 < shadow_low3:
            # Almacenar el pico high de la vela central en la lista
            self.resistenciaBuy.append(shadow_low2)


    def eliminarResistencias(self):
        for resistencia in self.resistenciasAEliminar:
            if resistencia in self.resistenciaSell:
                self.resistenciaSell.remove(resistencia)
            if resistencia in self.resistenciaBuy:
                self.resistenciaBuy.remove(resistencia)

    
        

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
    broker = bt.brokers.BrokerBack()
    broker.setcash(10000000.00)
    cerebro.setbroker(broker)
    
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='misanalisis')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='midrawdown')

    

    # Ejecutar el backtest
    thestrats = cerebro.run()
    thestrat = thestrats[0]
    
    
    print("Picos detectados:")
#

    for peak in cerebro.runstrats[0][0].resistenciaBuy:
        print(f"Pico: {peak:.2f}")

    print(cerebro.runstrats[0][0].valorInicialCartera)
    print(cerebro.runstrats[0][0].valorFinalCartera)

    calculo = (cerebro.runstrats[0][0].valorFinalCartera - cerebro.runstrats[0][0].valorInicialCartera) / cerebro.runstrats[0][0].valorInicialCartera * 100
    print(calculo)
    
    print('estadisticas:', thestrat.analyzers.misanalisis.print())
    print('drawdown:', thestrat.analyzers.midrawdown.print())

    cerebro.plot(style="candlestick")