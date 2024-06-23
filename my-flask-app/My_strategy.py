import datetime
from typing import Union, Any
import requests 
import yaml

from Strategy_sell import strategy_sell
from Strategy_buy import strategy_buy
from get_signal import calculate_ppo_buy_sell_signals, monthly_deposit, make_investment_decision



def my_strategy(stock_data, initial_investment, monthly_investment, option_strategy):

    result = [] #거래 결과를 초기화, 저장하는 용도
    # Initialize variables
    portfolio_value = 0 #계좌 잔고
    cash = initial_investment # 현금
    deposit = 0 # 보관금,
    invested_amount = initial_investment
    account_balance = 0
    shares = 0
    recent_high = 0
    recent_low = 1000000000000000000
    # val_ave = 0
    Invest_day = False
    Monthly_invested = False
    Sudden_fall = False
    signal = ''
    str_strategy = ""
    recent_signal = ''
    prev_month = None #현재 월을 비교하여 다르다면, 이는 새로운 달이 시작
    currency = 1300
    stock_ticker = stock_data.iloc[0]['Stock']
    print(stock_ticker)
    if '.K' in stock_ticker: currency = 1 # 한국주식의 경우
    # 한국 주식 티커의 경우 환율을 1로 설정
    if len(stock_ticker) == 6 and stock_ticker.isdigit():
        currency = 1
    print(currency)
    PPO_BUY = False  # Initialize neither buy nor sell signal is active
    PPO_SELL = False

      
    # Find the first trading day
    # first_day = stock_data.iloc[1]['Date']
    first_day = stock_data.index.min()
    # first_day = stock_data.iloc[1]['Date Time']
    first_trading_day = first_day + datetime.timedelta(days=1) #매매일

    first_investing_day = first_day + datetime.timedelta(days=1) #투자적립일

    if first_trading_day.weekday() >= 1:
        first_trading_day += datetime.timedelta(days=7 - first_trading_day.weekday())

    # Loop over data
    for i, row in stock_data.iterrows():
        # current_date = row['Date']
        current_date = row.name
        index = stock_data.index.get_loc(i)
        # 매달 적립 수행# 현재 날짜를 확인하고 새로운 달이 시작되면 자동으로 적립을 수행합니다.
        cash, invested_amount, signal, prev_month = monthly_deposit(current_date, prev_month, monthly_investment, cash, invested_amount)

        # Open High Low Close Volume
        # row['Date'].weekday()는 현재 데이터의 요일, row['Date'].day는 현재 데이터의 일
        # 첫 번째 주 중에 현재 날짜가 있거나, 일이 7 이하이고 거래 시작일 이후이면 Invest_day를 True로
        if current_date.weekday() == 0 or current_date.day <= 7 and current_date >= first_trading_day:
            Invest_day = True
        # 투자 결정 확인
        Invest_day = make_investment_decision(current_date, first_trading_day)

        # Calculate current price and performance
        price = row['Close'] * currency # 종가(원화환산)
        Open = row['Open'] * currency # 종가(원화환산)
        High = row['High'] * currency # 종가(원화환산)
        Low = row['Low'] * currency # 종가(원화환산)
        Close = row['Close'] * currency # 종가(원화환산)
        Volume = row['Volume']
        performance = (price - recent_high) / recent_high if recent_high else 0
  
        # Update recent high
        recent_high = max(recent_high, price)
        recent_low = min(recent_low, price)
       
        rsi_ta = row['RSI_14']
        mfi_ta = row['MFI_14']
        bb_upper_ta = row['UPPER_20']
        bb_lower_ta = row['LOWER_20']
        aroon_up_ta = row['AROONU_25']
        aroon_down_ta = row['AROOND_25']
        sma05_ta = row['SMA_5']
        sma20_ta = row['SMA_20']
        sma60_ta = row['SMA_60']
        sma120_ta = row['SMA_120']
        sma240_ta = row['SMA_240']
        stochk_ta = row['STOCHk_20_10_3']
        stochd_ta = row['STOCHd_20_10_3']

        # # PPO 매수 및 매도 신호 계산 (예: 12일 단기 EMA, 26일 장기 EMA, 9일 신호선)+ 상승,하강
        # My_strategy.py 파일 내에서 calculate_ppo_buy_sell_signals 함수 호출 부분 수정
        PPO_BUY, PPO_SELL, ppo_histogram, SMA_20_turn, SMA_60_turn = calculate_ppo_buy_sell_signals(stock_data, index, short_window=12, long_window=26, signal_window=9)




        if performance< -0.4 and (aroon_up_ta == 0 and bb_lower_ta > row['Close']):
            Sudden_fall = True
            signal = 'Sudden fall'
            shares_to_sell = 0.5 * shares
            shares -= shares_to_sell
            cash += shares_to_sell * price * 0.5
            deposit += shares_to_sell * price * 0.5
            signal = 'sell 0.5%' + ' ' + signal
 
                
        if Sudden_fall and (SMA_60_turn == True or PPO_BUY == True):
            shares_to_buy_depot = 0.5 * max(0, deposit) // price
            shares_to_buy_cash = 1.0 * max(0, cash) // price
            shares += shares_to_buy_depot + shares_to_buy_cash
            deposit -= shares_to_buy_depot * price
            cash -= shares_to_buy_cash * price
            signal = 'sudden fall + sma trend rise'
            Sudden_fall = False

        # Check if portfolio value has doubled and sell 50% stocks
        if portfolio_value >= 2 * invested_amount and cash > invested_amount and PPO_BUY == False:
            # shares_to_sell = 0.5 * shares
            shares_to_sell = 0.5 * shares
            shares -= shares_to_sell
            cash += shares_to_sell * price * 0.5
            deposit += shares_to_sell * price * 0.5
            signal = 'Act1 end!  sell 50%' + ' ' + signal
        else:
            # Hold cash
            pass

        sell_result = strategy_sell(current_date,rsi_ta, mfi_ta, sma20_ta, sma60_ta, stock_ticker, Sudden_fall, stochk_ta, stochd_ta, PPO_SELL,option_strategy)

        if isinstance(sell_result, tuple):
            ta_sell_amount, sell_signal, Sudden_fall = sell_result
        else:
            ta_sell_amount = sell_result
            sell_signal = '' + ' ' + signal

        if Invest_day and ta_sell_amount > 0:
            shares_to_sell = ta_sell_amount * shares
            shares -= shares_to_sell
            cash += shares_to_sell * price
            signal = sell_signal + ' ' + signal

        buy_result = strategy_buy(current_date, price, mfi_ta, sma20_ta, sma60_ta, recent_high, performance, rsi_ta, stochk_ta, stochd_ta, PPO_BUY,option_strategy)

        if isinstance(buy_result, tuple):
            perform_buy_amount, buy_signal = buy_result
        else:
            perform_buy_amount = buy_result
            return_signal = ''  + ' ' + signal

        if Invest_day and PPO_BUY == True:
            shares_to_buy = 0.5 * min(cash, monthly_investment) // price
            shares += shares_to_buy
            cash -= shares_to_buy * price
            signal = 'weekly trade'  + ' ' + signal

        if Invest_day and perform_buy_amount > 0:
            shares_to_buy = perform_buy_amount * cash // price
            shares += shares_to_buy
            cash -= shares_to_buy * price
            signal = 'week +' + buy_signal  + ' ' + signal
            # print(currency) 



        # Update portfolio value and save result
        portfolio_value = shares * price
        # Calculate account value
        account_balance = portfolio_value + cash + deposit

        rate = (account_balance / invested_amount - 1) * 100

        result.append([current_date, price/currency, Open/currency, High/currency,Low/currency, Close/currency, Volume, bb_upper_ta, bb_lower_ta, sma05_ta, sma20_ta, sma60_ta, sma120_ta, sma240_ta, recent_high/currency, aroon_up_ta, aroon_down_ta, ppo_histogram, SMA_20_turn, SMA_60_turn, recent_low/currency, account_balance, deposit, cash, portfolio_value, shares,  rate, invested_amount,  signal, rsi_ta,  stochk_ta,  stochd_ta, stock_ticker])


        if signal != '':
            recent_signal = current_date.strftime('%Y-%m-%d') + ":" + signal
        signal = ''

        # Find the next first trading day to invest
        if current_date.weekday() == 0 and current_date >= first_trading_day:
            first_trading_day = current_date + datetime.timedelta(days=7)
            Invest_day = False

        if current_date.day == 1 and current_date.weekday() < 5 and current_date >= first_trading_day:
            first_investing_day = current_date + datetime.timedelta(days=30)

        # Reset variables to initial values
        if current_date == stock_data.index[-1]:#마지막 인덱스(날짜)
            signal = ''
            pass
 
    # last_signal 딕셔너리 구성
    last_signal = {
        "recent_signal": recent_signal,  # recent_signal 변수가 무엇인지 확인 필요
        "PPO Buy Signal": PPO_BUY,
        "PPO Sell Signal": PPO_SELL,
    }

    total_account_balance = account_balance
    total_rate = rate
    # str_strategy += ("\n(+)200%->50% cash, peak*0.5 down-> invest{:,.0f} %,".format(30) + "peak*0.7 down->invest{:,.0f}".format(70))

    # last_signal 딕셔너리를 문자열로 변환하여 추가
    last_signal_str = str(last_signal)
    recent_signal = str(recent_signal)
  
    # Create dictionary to store results
    result_dict = {
        'result': result,
        'Total_account_balance': total_account_balance,
        'Total_rate': total_rate,
        'Last_signal''': last_signal,
        'Strategy''': recent_signal,
        'Invested_amount': invested_amount  # 이 부분을 추가
    }
    # print(result)
    return result_dict

