import yfinance as yf

nasdaq_data = yf.download('NQ=F', start='2023-08-20', end='2023-09-24',interval='2m')


