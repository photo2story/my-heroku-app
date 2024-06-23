from datetime import datetime


def strategy_buy(current_date, price, mfi_ta, sma20_ta, sma60_ta, recent_high, performance, rsi_ta, stochk_ta, stochd_ta, PPO_BUY,option_strategy):
     
    # if rsi_ta < 20  and PPO_BUY:
    #     # Buy more with 80% of available cash
    #     perform_buy_amount = 1
    #     buy_percent = int(perform_buy_amount * 100)
    #     buy_signal = 'buy {:,}%'.format(buy_percent)
    # elif rsi_ta < 30 and PPO_BUY:
    #     # Buy more with 50% of available cash
    #     perform_buy_amount = 0.9
    #     buy_percent = int(perform_buy_amount * 100)
    #     buy_signal = 'buy {:,}%'.format(buy_percent)
    # elif rsi_ta < 40 and PPO_BUY:
    #     # Buy more with 50% of available cash
    #     perform_buy_amount =0.80
    #     buy_percent = int(perform_buy_amount * 100)
    #     buy_signal = 'buy {:,}%'.format(buy_percent)
    # elif stochk_ta > stochd_ta and PPO_BUY:
    #     # Buy more with 40% of available cash
    #     perform_buy_amount = 0.5
    #     buy_percent = int(perform_buy_amount * 100)
    #     buy_signal = 'buy {:,}%'.format(buy_percent)
    # else:
    #     perform_buy_amount = 0
    #     buy_signal = None
    #  'default'  'monthly' 'modified_monthly'
    if option_strategy == 'default':
        perform_buy_amount = 1.0 if PPO_BUY else 0.5
    elif option_strategy == 'modified_monthly' and performance > 0:
        perform_buy_amount = 0
    else:
       perform_buy_amount = 1.0 if PPO_BUY else 0.5


  
    # 옵션 2: 적립식 투자일 경우, 매월 100% 투자
    # 옵션 3: 변형 적립식 투자일 경우, 수익률이 음수일 때만 투자
    if option_strategy == 'modified_monthly' and performance > 0:
        perform_buy_amount = 0
        buy_signal = None

    else:
        buy_percent = int(perform_buy_amount * 100)
        buy_signal = 'buy {:,}%'.format(buy_percent)

    # suden
    # if option_strategy in ['monthly', 'modified_monthly']:
    #     return 0, None
    
    # # 날짜 문자열을 datetime 객체로 변환
    # date = date_str
  
    # # 매수 금지 기간 설정
    # no_buy_start = datetime(date.year, 7, 1)
    # no_buy_end = datetime(date.year, 10, 30)
  
    # # 날짜가 매수 금지 기간 내에 있는지 확인
    # if (no_buy_start <= date <= no_buy_end) and option_strategy == 'modified_monthly':
    #     return 0, None
    # if sell_signal is not None : 
    #     perform_buy_amount = 0
    #     buy_signal = None
  
    return perform_buy_amount, buy_signal


