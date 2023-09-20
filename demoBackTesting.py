import yfinance as yf
import pandas as pd
import numpy as np
import ta

# Descargar los datos del NASDAQ entre el 1 de septiembre de 2022 y el 1 de septiembre de 2023
nasdaq_data = yf.download('^NDX', start='2020-10-01', end='2023-09-15')

# Calcular la EMA de 200 períodos
nasdaq_data['EMA200'] = nasdaq_data['Close'].rolling(window=200).mean()

nasdaq_data['RSI'] = ta.momentum.RSIIndicator(nasdaq_data['Close'], window=14).rsi()

# Función xrf
def xrf(values, length):
    r_val = np.nan
    if length >= 1:
        for i in range(length + 1):
            if np.isnan(r_val) or not np.isnan(values[i]):
                r_val = values[i]
    return r_val

# Función xsa
def xsa(src, length, wei):
    sumf = np.zeros_like(src)  # Inicializar un array de ceros con la misma forma que src
    ma = np.zeros_like(src)
    out = np.zeros_like(src)
    for i in range(len(src)):
        sumf[i] = sumf[i - 1] + src[i] - (src[i - length] if i >= length else 0)
        ma[i] = sumf[i] / length
        out[i] = src[i] * wei + ma[i] * (length - wei)
    return out

# Definir stop loss y take profit
stop_loss_percent = 0.05  # 5%
take_profit_percent = 0.10  # 10%

# Set up a simple model of banker fund flow trend
close = nasdaq_data['Close']
fundtrend = (
    (3 * xsa(
        (close - nasdaq_data['Low'].rolling(window=27).min()) /
        (nasdaq_data['High'].rolling(window=27).max() - nasdaq_data['Low'].rolling(window=27).min()) * 100,
        5, 1
    ) - 2 * xsa(
        xsa(
            (close - nasdaq_data['Low'].rolling(window=27).min()) /
            (nasdaq_data['High'].rolling(window=27).max() - nasdaq_data['Low'].rolling(window=27).min()) * 100,
            5, 1
        ), 3, 1
    ) - 50
) * 1.032 + 50)

# Define typical price for banker fund
typ = (2 * close + nasdaq_data['High'] + nasdaq_data['Low'] + nasdaq_data['Open']) / 5

# Define banker fund flow bull bear line
bullbearline = (
    ((typ - nasdaq_data['Low'].rolling(window=34).min()) /
     (nasdaq_data['High'].rolling(window=34).max() - nasdaq_data['Low'].rolling(window=34).min()) * 100).ewm(span=13).mean()
)

# Inicializar señales de entrada y salida
nasdaq_data['Long_Entry'] = 0
nasdaq_data['Long_Exit'] = 0
nasdaq_data['Short_Entry'] = 0
nasdaq_data['Short_Exit'] = 0

# Calcular las señales de entrada largas (long) y cortas (short)
for i in range(1, len(nasdaq_data)):
    if nasdaq_data['Close'][i] > nasdaq_data['EMA200'][i] and nasdaq_data['RSI'][i] > 70:
        nasdaq_data['Long_Entry'][i] = 1
    elif nasdaq_data['Close'][i] < nasdaq_data['EMA200'][i] and nasdaq_data['RSI'][i] < 30:
        nasdaq_data['Short_Entry'][i] = 1

# Calcular las señales de salida basadas en stop loss y take profit
for i in range(1, len(nasdaq_data)):
    if nasdaq_data['Long_Entry'][i] == 1:
        stop_loss_price = nasdaq_data['Close'][i] * (1 - stop_loss_percent)
        take_profit_price = nasdaq_data['Close'][i] * (1 + take_profit_percent)
        for j in range(i + 1, len(nasdaq_data)):
            if nasdaq_data['Close'][j] <= stop_loss_price or nasdaq_data['Close'][j] >= take_profit_price:
                nasdaq_data['Long_Exit'][j] = 1
                break

    elif nasdaq_data['Short_Entry'][i] == 1:
        stop_loss_price = nasdaq_data['Close'][i] * (1 + stop_loss_percent)
        take_profit_price = nasdaq_data['Close'][i] * (1 - take_profit_percent)
        for j in range(i + 1, len(nasdaq_data)):
            if nasdaq_data['Close'][j] >= stop_loss_price or nasdaq_data['Close'][j] <= take_profit_price:
                nasdaq_data['Short_Exit'][j] = 1
                break

# Calcular la cantidad de trades largos (long) y cortos (short)
long_trades = nasdaq_data['Long_Entry'].sum()
short_trades = nasdaq_data['Short_Entry'].sum()

# Calcular la rentabilidad de la estrategia
nasdaq_data['Estrategia_Rentabilidad'] = 1.0
nasdaq_data['In_Trade'] = 0
for i in range(1, len(nasdaq_data)):
    if nasdaq_data['Long_Entry'][i] == 1:
        nasdaq_data['In_Trade'][i] = 1
        nasdaq_data['Estrategia_Rentabilidad'][i:] = nasdaq_data['Estrategia_Rentabilidad'][i - 1] * (1 + (nasdaq_data['Close'][i] / nasdaq_data['Close'][i - 1] - 1))
    elif nasdaq_data['Short_Entry'][i] == 1:
        nasdaq_data['In_Trade'][i] = 1
        nasdaq_data['Estrategia_Rentabilidad'][i:] = nasdaq_data['Estrategia_Rentabilidad'][i - 1] * (1 - (nasdaq_data['Close'][i] / nasdaq_data['Close'][i - 1] - 1))

# Calcular la rentabilidad si hubieras hodleado la acción desde el inicio hasta el final
inicio_precio = nasdaq_data.iloc[0]['Close']
final_precio = nasdaq_data.iloc[-1]['Close']
hold_rentabilidad = ((final_precio / inicio_precio) - 1) * 100

# Reemplaza estas fechas con las fechas reales que deseas
fecha_inicio = '2020-10-1'
fecha_final = '2023-08-'

# Obtener el precio de cierre en la fecha de inicio
try:
    precio_inicio = nasdaq_data.loc[fecha_inicio]['Close']
except KeyError:
    print(f"No se encontró la fecha de inicio ({fecha_inicio}) en el DataFrame.")

# Obtener el precio de cierre en la fecha final
try:
    precio_final = nasdaq_data.loc[fecha_final]['Close']
except KeyError:
    print(f"No se encontró la fecha final ({fecha_final}) en el DataFrame.")

# Imprimir los precios si se encontraron
if 'precio_inicio' in locals():
    print(f"Precio de cierre en la fecha de inicio ({fecha_inicio}): {precio_inicio}")

if 'precio_final' in locals():
    print(f"Precio de cierre en la fecha final ({fecha_final}): {precio_final}")


# Imprimir los resultados
print("Cantidad de Trades Largos:", long_trades)
print("Cantidad de Trades Cortos:", short_trades)
print("Rentabilidad de la Estrategia:", nasdaq_data['Estrategia_Rentabilidad'].iloc[-1])
print("Rentabilidad si Hubieras Hodleado:", hold_rentabilidad)
