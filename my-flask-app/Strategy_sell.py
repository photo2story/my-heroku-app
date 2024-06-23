from datetime import datetime

def strategy_sell(date_str, rsi_ta, mfi_ta, sma20_ta, sma60_ta, stock_ticker, Sudden_fall, stochk_ta, stochd_ta, PPO_SELL,option_strategy):
    # 날짜 문자열을 datetime 객체로 변환
    date = date_str

    # 옵션 2와 옵션 3 모두에서 매도 신호를 주지 않음
    # if option_strategy in ['monthly', 'modified_monthly']:
    #     return 0, None, ""

  # 기타 경우에 대한 매도 전략 로직

    # 매도 전략 적용 기간 설정
    sell_start = datetime(date.year, 8, 1)
    sell_end = datetime(date.year, 8, 30)

    # 날짜가 매도 전략 적용 기간 내에 있는지 확인
    if sell_start <= date <= sell_end:
        return 0.5, 'sell 50%', Sudden_fall
    
    # ppo_index= (sma20_ta-sma60_ta) / sma20_ta *100

    if stock_ticker == 'SOXL'or stock_ticker == 'UPRO'or stock_ticker == 'TQQQ':
        if rsi_ta > 60 and stochk_ta < stochd_ta:
            ta_sell_amount = 0.5
            sell_percent = int(ta_sell_amount * 100)
            sell_signal = 'sell {:,}%'.format(sell_percent)
        # elif stochk_ta < stochd_ta:
        #     ta_sell_amount = 0.3
        #     sell_percent = int(ta_sell_amount * 100)
        #     sell_signal = 'sell {:,}%'.format(sell_percent)    
        #     Sudden_fall == False
        else:
            ta_sell_amount = 0
            sell_signal = None

    elif stock_ticker == 'AAPL'or stock_ticker == 'TSLA' or stock_ticker == 'NVDA' or stock_ticker == 'QQQ' or stock_ticker == '305540.KS' or stock_ticker == '005490.KS'\
            or stock_ticker == 'SPY' or stock_ticker == 'MSFT' or stock_ticker == 'MSFT' or stock_ticker == '373220' or stock_ticker == 'U' or stock_ticker == 'IONQ' or stock_ticker =='086520':
        if rsi_ta > 60 and stochk_ta < stochd_ta:
            ta_sell_amount = 0.3
            sell_percent = int(ta_sell_amount * 100)
            sell_signal = 'sell {:,}%'.format(sell_percent)
        else:
            ta_sell_amount = 0
            sell_signal = None
    else:          
        if rsi_ta > 60 and stochk_ta < stochd_ta:
          ta_sell_amount = 0.3
          sell_percent = int(ta_sell_amount * 100)
          sell_signal = 'sell {:,}%'.format(sell_percent)
        else:
          ta_sell_amount = 0
          sell_signal = None

    return ta_sell_amount, sell_signal, Sudden_fall
