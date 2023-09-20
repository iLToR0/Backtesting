import backtrader as bt

#Se busca modularizar el codigo a python y la libreria backtrader, respetando al maximo la logica original.

#Se define la clase que representa al indicador. 
#Hereda de bt.Indicator para personalizar un nuevo indicador con la logica de Backtrader y que lo lea como un indicador propio.
#Los params son los originales, pueden ser modificados segun la estrategia.
class BlackcatIndicator(bt.Indicator):
    params = (
        ("length", 27),
        ("ema_length", 13)
    )
#lines almacena y representa las 3 lineas que utiliza Blackcat para los valores calculados x el indicador.
    lines = ("fundtrend", "bullbearline", "bankerentry")

#Metodo init produce la inicializacion al ejecutarse una nueva instancia del indicador y se calculan los valores.
#Close:Precio de cierre; Low y High:Precio mas bao y mas alto dentro del periodo;
#typ: es el precio tipico y se calcula por el promedio ponderado de 3 precios (close,low,high),
#calcula la tendencia del banco y su relacion con el precio.
    def __init__(self):
        close = self.data.close
        low = self.data.low
        high = self.data.high
        typ = (2 * close + high + low + self.data.open) / 5

 # Se utilizan las formulas originales del indicador para calcular la linea fundtrend.
        fundtrend = ((3 * self.xsa((close - bt.indicators.Lowest(low, period=self.params.length)) /
                                   (bt.indicators.Highest(high, period=self.params.length) -
                                    bt.indicators.Lowest(low, period=self.params.length)) * 100, 5, 1)
                     - 2 * self.xsa(self.xsa((close - bt.indicators.Lowest(low, period=self.params.length)) /
                                             (bt.indicators.Highest(high, period=self.params.length) -
                                              bt.indicators.Lowest(low, period=self.params.length)) * 100, 5, 1),
                                     3, 1) - 50) * 1.032 + 50)

        self.lines.fundtrend = fundtrend

#Se calcula la linea bullbearline del indicador; .Lowest y .Highest encuentran los picos minimos y maximos del precio.
#calcula una EMA de 100 períodos(*duda*) basandose en el precio típico y los valores minimos y maximos encontrados.
# *duda* ¿¿¿la ema de 100 periodos es ajustable segun la estrategia o blackcat siempre usa internamente una de 100???

        lol = bt.indicators.Lowest(low, period=34)
        hoh = bt.indicators.Highest(high, period=34)
        bullbearline = bt.indicators.EMA100((typ - lol) / (hoh - lol) * 100)
        self.lines.bullbearline = bullbearline

#calcula bankerentry, determina las señales de entrada segun condiciones de la estrategia.
        self.lines.bankerentry = (fundtrend > bullbearline) & (bullbearline < 25)

#funcion auxiliar, calculamos un valor de salida(out), basada en una serie de datos de entrada(src).
    def xsa(self, src, length, wei):
        sumf = 0.0
        ma = 0.0
        out = 0.0

        for i in range(length):
            if not bt.math.isnan(src[i]):
                sumf += src[i]
                break

        for i in range(length):
            if not bt.math.isnan(src[i]):
                ma = sumf / length
                break

        for i in range(length):
            if not bt.math.isnan(src[i]):
                out = (src[i] * wei + out * (length - wei)) / length
                break

        return out
