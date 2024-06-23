
## Results_plot_mpl.py


import yfinance as yf
import matplotlib.pyplot as plt
from mplchart.chart import Chart
from mplchart.primitives import Candlesticks, Volume, TradeMarker, TradeSpan
from mplchart.indicators import SMA, EMA, RSI, MACD, PPO
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import requests
import numpy as np
import FinanceDataReader as fdr
from datetime import datetime
import os
from get_ticker import get_ticker_name, get_ticker_market
from tradingview_ta import TA_Handler, Interval, Exchange

def convert_file_path_for_saving(file_path):
  return file_path.replace('/', '-')

def convert_file_path_for_reading(file_path):
  return file_path.replace('-', '/')

def save_figure(fig, file_path):
  file_path = convert_file_path_for_saving(file_path)
  fig.savefig(file_path)
  plt.close(fig)  # 닫지 않으면 메모리를 계속 차지할 수 있음

def get_tradingview_analysis(ticker):
  # tv_symbol = f"{ticker.upper()}/USD"  # 트레이딩뷰에서 사용하는 심볼 형식
  market = get_ticker_market(ticker, file_path='stock_market.csv')
  if market == 'KRX':
    screener = "korea"
  elif market == 'UPBIT' or market == 'BINANCE' :   
    screener = "crypto"
  else:   
    screener = "america"

  print(market)

  tv_handler = TA_Handler(
      symbol = ticker,
      exchange = market,  # 해당 거래소로 설정
      screener = screener,  # 예: "america" 또는 "crypto"
      interval = Interval.INTERVAL_1_DAY,
  )
  tv_analysis = tv_handler.get_analysis().summary
  return tv_analysis

def plot_results_mpl(ticker,start_date, end_date):
    # print(plt.style.available)

    # ticker = 'AAPL'
    prices = fdr.DataReader(ticker,start_date, end_date)
    # print(prices)
    max_bars = 250
    prices.dropna(inplace=True)

    # Calculate SMA 20 and SMA 60
    SMA20 = prices['Close'].rolling(window=20).mean()
    # print(SMA20)
    SMA60 = prices['Close'].rolling(window=60).mean()

    # Define window spans for calculations
    short_window = 12
    long_window = 26
    signal_window = 9

    # 각 행에 대한 단기 및 장기 EMA 계산
    short_ema = prices['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = prices['Close'].ewm(span=long_window, adjust=False).mean()
    # 각 행에 대한 PPO 계산
    ppo = ((short_ema - long_ema) / long_ema) * 100
    # 각 행에 대한 PPO 시그널 계산
    ppo_signal = ppo.ewm(span=signal_window, adjust=False).mean()
    # 히스토그램 계산
    ppo_histogram = ppo - ppo_signal

    # Calculate PPO Histogram with error handling
    try:
        ppo_histogram = ppo - ppo_signal
    except TypeError as e:
        print(f"Error calculating PPO Histogram: {e}")
        ppo_histogram = pd.Series(np.zeros(len(ppo)), index=ppo.index)  # Fallback to a series of zeros

    indicators = [
      Candlesticks(), SMA(20), SMA(60), Volume(),
      RSI(), PPO(), TradeSpan('ppohist>0')
    ]

    chart = Chart(title=ticker, max_bars=max_bars)
    chart.plot(prices, indicators)

    fig = chart.figure

    # 그래프를 PNG 파일로 저장
    save_figure(fig, 'result_mpl_{}.png'.format(ticker))
    # 티커 이름 가져오기
    name = get_ticker_name(ticker)


    # 그래프를 PNG 파일로 저장
    save_figure(fig, 'result_mpl_{}.png'.format(ticker))

    # tv_analysis =get_tradingview_analysis(ticker)

    # Discord로 이미지 전송
    import requests

    # Discord로 이미지 전송
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

    # 결과 메시지 전송
    message = f"Stock: {ticker} ({name})\n" \
              f"Close 종가: {prices['Close'].iloc[-1]:,.2f}\n" \
              f"SMA 20: {SMA20.iloc[-1]:,.2f}\n" \
              f"SMA 60: {SMA60.iloc[-1]:,.2f}\n" \
              f"PPO Histogram: {ppo_histogram.iloc[-1]:,.2f}\n" \
              # f"트레이딩뷰 BUY: {tv_analysis['BUY']}, NEUTRAL: {tv_analysis['NEUTRAL']}, SELL: {tv_analysis['SELL']}"
    response = requests.post(DISCORD_WEBHOOK_URL, data={'content': message})
    if response.status_code != 204:
       print('Discord 메시지 전송 실패')
    else:
       print('Discord 메시지 전송 성공')

    # 이미지 파일 전송
    files = {'file': open('result_mpl_{}.png'.format(ticker), 'rb')}
    response = requests.post(DISCORD_WEBHOOK_URL, files=files)


if __name__ == "__main__":
    # 사용 예시
  ticker ='VOO'
  start_date = "2022-01-01"
  end_date = datetime.today().strftime('%Y-%m-%d')  # 오늘 날짜 문자열로 변환하기
  plot_results_mpl(ticker,start_date , end_date)

  # from tradingview_ta import TA_Handler, Interval, Exchange

  # tesla = TA_Handler(
  #     symbol="U",
  #     screener="america",
  #     exchange="NYSE",
  #     interval=Interval.INTERVAL_1_DAY,
  # )
  # # Existing code: ...
  # # At the point where you are fetching analysis from TradingView
  # tesla_analysis = tesla.get_analysis()

  # # Check if we received an analysis object
  # if tesla_analysis is not None:
  #     print(tesla_analysis.summary)  # Assuming .summary is a valid attribute of the analysis object
  # else:
  #     print("Failed to retrieve analysis.")
  # # Example output: {"RECOMMENDATION": "BUY", "BUY": 8, "NEUTRAL": 6, "SELL": 3}
  # tv_analysis = get_tradingview_analysis(ticker)