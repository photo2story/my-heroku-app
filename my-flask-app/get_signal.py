#### get_signal.py


import pandas as pd
import numpy as np

def monthly_deposit(current_date, prev_month, monthly_investment, cash, invested_amount):
    signal = '' # Initialize signal with an empty string
    if prev_month != f"{current_date.year}-{current_date.month}":
       cash += monthly_investment
       invested_amount += monthly_investment
       signal = 'Monthly invest'
       prev_month = f"{current_date.year}-{current_date.month}"
    return cash, invested_amount, signal, prev_month

#월의 첫 번째 주 중 첫 번째 평일 등)에 따라 투자 결정을 내리는 데 사용됩니다.
def make_investment_decision(current_date, first_trading_day):
    if current_date.weekday() == 0 or (current_date.day <= 7 and current_date >= first_trading_day):
        return True
    return False

def calculate_ppo_buy_sell_signals(stock_data, index, short_window, long_window, signal_window):
    PPO_BUY = False
    PPO_SELL = False
    SMA_20_turn = False
    SMA_60_turn = False

    # print(stock_data['SMA_20'].iloc[index])
    if index >= 7 and stock_data['SMA_20'].iloc[index] > stock_data['SMA_60'].iloc[index] and stock_data['SMA_60'].iloc[index] > stock_data['SMA_120'].iloc[index]:
        SMA_60_turn = True
    else:
        SMA_60_turn = False
    if index >= 7 and stock_data['SMA_10'].iloc[index] > stock_data['SMA_20'].iloc[index]:
        SMA_20_turn = True
    else:
        SMA_20_turn = False
    
    # 각 행에 대한 단기 및 장기 EMA 계산
    short_ema = stock_data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = stock_data['Close'].ewm(span=long_window, adjust=False).mean()
    # 각 행에 대한 PPO 계산
    ppo = ((short_ema - long_ema) / long_ema) * 100
    # 각 행에 대한 PPO 시그널 계산
    ppo_signal = ppo.ewm(span=signal_window, adjust=False).mean()
    # 히스토그램 계산
    ppo_histogram = ppo - ppo_signal
    # 매수 및 매도 신호 결정, 기준선1.1
    ppo_histogram.iloc[index]
    PPO_BUY = True if SMA_60_turn and ppo_histogram.iloc[index] > 1.1 else False
    PPO_SELL = True if not SMA_20_turn and ppo_histogram.iloc[index] < 1.1 else False
    ppo_histogram = ppo_histogram.iloc[index]

    return PPO_BUY, PPO_SELL,  ppo_histogram, SMA_20_turn, SMA_60_turn

def calculate_ppo_buy_sell_signals2(stock_data, index, short_window, long_window, signal_window):
  PPO_BUY = False
  PPO_SELL = False
  SMA_20_turn = False
  SMA_60_turn = False

  #이전 날(i-1)과 현재 날(i)의 단기 이동평균(SMA_20)과 장기 이동평균(SMA_60)의 차이를 계산하여 PPO(Price Percentage Oscillator) 지표를 만듭니다.
  ppo_index_1 = (stock_data.iloc[index-9]['SMA_20']-stock_data.iloc[index-9]['SMA_60']) / stock_data.iloc[index-9]['SMA_60'] *100 #signal, 9일
  ppo_index_0 = (stock_data.iloc[index]['SMA_20']-stock_data.iloc[index]['SMA_60']) / stock_data.iloc[index]['SMA_60'] *100 #PPO

  ppo_histogram = ppo_index_1 - ppo_index_0
  if ppo_index_0 - ppo_index_1>0: # 히스토그램 = PPO-signal (+)매수
       # print(f" 매수신호입니다! 이전: {ppo_index_0}")
      PPO_BUY = True
  elif ppo_index_0 - ppo_index_1<0: # 히스토그램 = PPO-signal (-)매도
       # print(f" 매도신호입니다! 이전: {ppo_index_0}")
       PPO_SELL = True
  else:    
      PPO_BUY = False
      PPO_SELL = False


  if index >= 7 and stock_data.iloc[index]['SMA_60'] > stock_data.iloc[index-5]['SMA_120']:
      # print(f"상승 구간입니다! 이전: {stock_data.iloc[i-7]['SMA_60']}")
      # print(f"상승 구간입니다! 현재: {stock_data.iloc[i]['SMA_60']}")
      SMA_60_turn = True
  else:    
      SMA_60_turn = False


  return PPO_BUY, PPO_SELL, ppo_histogram, SMA_20_turn, SMA_60_turn


# 테스트를 위한 예제 데이터 생성
def create_example_data():
    np.random.seed(0)  # 결과 일관성을 위해 시드 설정
    dates = pd.date_range(start="2020-01-01", periods=100)
    close_prices = np.random.uniform(100, 200, size=100)
    stock_data = pd.DataFrame({'Close': close_prices}, index=dates)
  
    # SMA_60과 SMA_120 추가
    stock_data['SMA_10'] = stock_data['Close'].rolling(window=10).mean()
    stock_data['SMA_20'] = stock_data['Close'].rolling(window=20).mean()
    stock_data['SMA_60'] = stock_data['Close'].rolling(window=60).mean()
    stock_data['SMA_120'] = stock_data['Close'].rolling(window=120).mean()
    return stock_data
  
# 테스트 코드
if __name__ == "__main__":
    stock_data = create_example_data()

    # PPO 매수 및 매도 신호 계산
    # 여기서는 마지막 날짜(인덱스 99)에 대한 신호를 계산합니다.
    PPO_BUY, PPO_SELL, SMA_20_turn, SMA_60_turn  = calculate_ppo_buy_sell_signals(stock_data, 99, short_window=12, long_window=26, signal_window=9)

    print("PPO Buy Signal:", PPO_BUY)
    print("PPO Sell Signal:", PPO_SELL)
    print("SMA 20 Turn:", SMA_20_turn)
    print("SMA 60 Turn:", SMA_60_turn)