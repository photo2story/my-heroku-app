import matplotlib.dates as dates
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import requests
import glob
import asyncio  # 추가
from get_ticker import get_ticker_name
from Results_plot_mpl import plot_results_mpl


def convert_file_path_for_saving(file_path):
  return file_path.replace('/', '-')

def convert_file_path_for_reading(file_path):
  return file_path.replace('-', '/')

def save_figure(fig, file_path):
  file_path = convert_file_path_for_saving(file_path)
  fig.savefig(file_path)
  plt.close(fig)  # 닫지 않으면 메모리를 계속 차지할 수 있음

from PIL import Image

def load_image(file_path):
    file_path = convert_file_path_for_reading(file_path)
    image = Image.open(file_path)
    return image

def plot_results(file_path, total_account_balance, total_rate, str_strategy, stock,invested_amount):
    # 파일 경로 변환
    file_path1 = convert_file_path_for_reading(file_path1)

    result_df = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date',comment='#')

    # 해당 주식 데이터만 추출하여 새로운 DataFrame 생성
    stock_df = result_df[result_df['stock_ticker'] == stock]

    fig, ax2 = plt.subplots(figsize=(12, 7))

    # 하단 그래프
    ax2.plot(stock_df['rate'], label='Daily Return')
    ax2.set_ylabel('Daily Return (%)')
    ax2.legend(loc='upper left')
    # plt.title("\nTotal_account_balance: {:,.0f} won,".format(total_account_balance) +
              # "Total_rate: {:,.0f} %".format(total_rate) +"\nStrategy: {} %".format(str_strategy))

    plt.title("\nTotal_account_balance: {:,.0f} won,".format(total_account_balance) +
          "Total_rate: {:,.0f} %".format(total_rate) +
          "\nInvested_amount: {:,.0f} $".format(invested_amount) +
          "\nStrategy: {} %".format(str_strategy))


    # x축 라벨 설정
    ax2.xaxis.set_major_locator(dates.YearLocator())
    plt.xlabel('Year')

    # 포트폴리오 가치 표시
    plt.annotate('Portfolio Value\n{:.0f}won'.format(total_account_balance),
                 xy=(stock_df.index[0], total_account_balance),
                 xytext=(stock_df.index[0], total_account_balance * 1.25),
                 arrowprops=dict(facecolor='black', headwidth=10, width=2))

    # 그래프를 PNG 파일로 저장
    save_figure(fig, 'result_{}.png'.format(stock))

    # fig.savefig('result_{}.png'.format(stock))
    # plt.close()
    ax2.cla
    plt.cla
    plt.clf()  # Clear the figure to avoid residual plots when this function is called again
  

  # Discord로 이미지 전송
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    message = {
        'content': f"Stock: {stock}\n"
                   f"Invested_amount: {invested_amount:,.0f} $\n"
                   f"Total_account_balance: {total_account_balance:,.0f} $\n"
                   f"Total_rate: {total_rate:,.0f} %\n"
                   f"Strategy: {str_strategy} %\n"
                   f" "
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=message, files={'image': open('result_{}.png'.format(stock), 'rb')})

    if response.status_code != 204:
        print('Discord 메시지 전송 실패')
    else:
        print('Discord 메시지 전송 성공')


def plot_comparison_results(file_path1, file_path2, stock1, stock2, total_account_balance, total_rate, str_strategy,invested_amount,min_stock_data_date):
    fig, ax2 = plt.subplots(figsize=(12, 7))

    # 각 주식의 데이터프레임을 읽어옵니다.
    # 파일 경로 변환
    file_path1 = convert_file_path_for_reading(file_path1)
    file_path2 = convert_file_path_for_reading(file_path2)
    df1 = pd.read_csv(file_path1, parse_dates=['Date'], index_col='Date')
    df2 = pd.read_csv(file_path2, parse_dates=['Date'], index_col='Date')
    # print(df2)

    # 주식 데이터프레임의 최소 날짜를 찾아서 그 날짜로 범위를 맞춥니다.
    start_date = min_stock_data_date
    end_date = min(df1.index.max(), df2.index.max())

    # 두 데이터프레임의 날짜 범위를 조정합니다.
    df1 = df1.loc[start_date:end_date]
    df2 = df2.loc[start_date:end_date]

    # 7일 이동 평균으로 리샘플링합니다.
    df1['rate_7d_avg'] = df1['rate'].rolling('7D').mean()
    df2['rate_20d_avg'] = df2['rate_vs'].rolling('20D').mean()

    # 주식 1과 주식 2의 7일 이동 평균 데이터를 그래프에 추가
    ax2.plot(df1.index, df1['rate_7d_avg'], label=f'{stock1} 7-Day Avg Return')
    ax2.plot(df2.index, df2['rate_20d_avg'], label=f'{stock2} 20-Day Avg Return')

    # 레이블, 제목, 범례 설정
    plt.ylabel('7-Day Average Daily Return (%)')
    plt.legend(loc='upper left')

    plt.title(f"\nTotal Account Balance: {total_account_balance:,.0f} $, Total Rate: {total_rate:,.0f} %\n" +
              f"Invested Amount: {invested_amount:,.0f} $, Strategy: {str_strategy}")

    # x축 라벨 설정
    ax2.xaxis.set_major_locator(dates.YearLocator())
    plt.xlabel('Year')

    # 그래프를 PNG 파일로 저장
    if len(stock1) == 6 and stock1.isdigit():  # 한국 수식 6자리숫자
        stock1_name = get_ticker_name(stock1)
        if stock1_name is not None:
            stock1 = stock1 + '_' + stock1_name
            # print(stock1)
    save_path = f'comparison_{stock1}_{stock2}.png'
    fig.savefig(save_path)

    
    plt.cla()
    plt.clf()
    plt.close(fig)

    # Discord로 이미지 전송
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    message = {
        'content': f"Stock: {stock1}\nInvested Amount: {invested_amount:,.0f} $, " +
                   f"Total Account Balance: {total_account_balance:,.0f} $, Total Rate: {total_rate:,.0f} %, " +
                   f"Strategy: {str_strategy}"
    }
    with open(f'comparison_{stock1}_{stock2}.png', 'rb') as image:
        response = requests.post(DISCORD_WEBHOOK_URL, json=message, files={'image': image})

    if response.status_code != 204:
        print('Discord 메시지 전송 실패')
    else:
        print('Discord 메시지 전송 성공')



import time  # 추가

async def plot_results_all():
  image_files = glob.glob("comparison_*.png")
  DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

  for image_path in image_files:
      stock = image_path.split('comparison_')[1].split('_VOO.png')[0]
      # 티커 이름 가져오기
      name = get_ticker_name(stock)
      
      # 해당 주식의 CSV 파일 경로 생성
      csv_file_path = f"result_{stock}.csv"
      # print(csv_file_path)

      if os.path.exists(csv_file_path):
          df = pd.read_csv(csv_file_path)
          # print(df)
          last_row = df.iloc[-1]
          total_account_balance = last_row['account_balance']
          # print(str(total_account_balance))
          total_rate = last_row['rate']
          # print(str(total_rate))
          
          # str_strategy = last_row['Strategy']
          invested_amount = last_row['invested_amount']
          str_last_signal = last_row['signal']
          print(str_last_signal)

          # 결과 메시지 전송
          message = {
              'content': f"Stock: {stock} ({name})\n" f"Rate: {total_rate:,.2f} %\n"
                         f"InvestIed_amount: {invested_amount:,.0f} $\n"
                         f"Total_account_balance: {total_account_balance:,.0f} $\n"
                         f"Last_signal: {str_last_signal} \n"
          }
          response = requests.post(DISCORD_WEBHOOK_URL, data=message)
          if response.status_code != 204:
              print('Discord 메시지 전송 실패')
          else:
              print('Discord 메시지 전송 성공')

      # 이미지 파일 전송
      with open(image_path, 'rb') as image:
          response = requests.post(
              DISCORD_WEBHOOK_URL,
              files={'image': image}
          )
          if response.status_code != 204:
              print(f'Graph 전송 실패: {stock}')
          else:
              print(f'Graph 전송 성공: {stock}')

      
      
      # plot_results_mpl(stock, start_date, end_date)

  await asyncio.sleep(1)  # 1초 대기