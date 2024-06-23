#### get_ticker.py


import pandas as pd
import FinanceDataReader as fdr
import csv
from bs4 import BeautifulSoup
import requests
import yfinance as yf
import investpy
from tradingview_ta import TA_Handler, Interval, Exchange

def get_ticker_name(ticker, file_path='stock_market.csv'):
    df = pd.read_csv(file_path)
    result = df.loc[df['Symbol'] == ticker, 'Name']
    name = result.iloc[0] if not result.empty else None
    return name

def get_ticker_market(ticker, file_path='stock_market.csv'):
  df = pd.read_csv(file_path)
  result = df.loc[df['Symbol'] == ticker, 'Market']
  market = result.iloc[0] if not result.empty else None
  return market


# 주식 정보를 가져오는 함수
def get_stock_info(ticker):
    info = yf.Ticker(ticker).info
    return {
        'Stock': ticker,
        # 'market': info.get('market'),
        'Industry': info.get('industry'),
        'Beta': info.get('beta'),
        'Sector': info.get('sector')
    }
# The rest of the functions (omitted for brevity)

def update_stock_market_csv(file_path, tickers_to_update):
  # Pre-fetch stock information for all tickers
  tickers_info = {ticker: get_stock_info(ticker) for ticker in tickers_to_update}
  df = pd.read_csv(file_path, encoding='utf-8-sig')  # Specify encoding 
  for i, row in df.iterrows():
      ticker = row['Symbol']
      if ticker in tickers_to_update:
          stock_info = get_stock_info(ticker)
          for key, value in stock_info.items():
              df.at[i, key] = value
  df.to_csv(file_path, index=False, encoding='utf-8-sig')  # Specify 

# 필요한 티커 리스트 (예시)
# tickers_to_update = [
#     'VOO', 'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'APTV', 'FSLR', 'JNJ', 'PFE',
#     'INMD', 'UNH', 'OXY', 'XOM', 'CVX', 'AMZN', 'NFLX', 'KO', 'LULU', 'EL',
#     'SBUX', 'CMG', 'NKE', 'BKNG', 'LOW', 'DHI', 'ADSK', 'NIO', 'F', 'BA',
#     'GE', 'C', 'BRK.A', 'BLK', 'V', 'CRK', 'ALB', 'MDT', 'TDOC', 'ENPH',
#     'CSIQ', 'JPM', 'BAC', 'WFC', 'SQ', 'HD', 'PG', 'IONQ', 'SOXL'
# ]
#  # 여기에 필요한 티커 20개 추가

# 파일 경로 지정 및 CSV 파일 업데이트
# file_path = 'stock_market.csv'
# update_stock_market_csv(file_path, tickers_to_update)




def load_tickers():
    """CSV 파일에서 티커 데이터를 읽어 딕셔너리로 반환합니다."""
    ticker_dict = {}
    with open('stock_market.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        for rows in csv_reader:
            if len(rows) >= 2:
                ticker_dict[rows[1]] = rows[0]
    return ticker_dict

def search_tickers(stock_name, ticker_dict):
    """주식명으로 티커와 이름을 검색합니다."""
    stock_name_lower = stock_name.lower()
    return [(ticker, name) for name, ticker in ticker_dict.items() if stock_name_lower in name.lower()]

def search_ticker_list_KR():
    """한국 주식 종목을 검색합니다."""

    url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
    response = requests.get(url)
    response.encoding = 'euc-kr'  # Korean encoding
  
    # Convert the HTML content to a pandas DataFrame
    df_listing = pd.read_html(response.text, header=0)[0]
  
    # Rename the columns and format them as needed
    cols_ren = {
        '회사명':'Name',
        '종목코드':'Symbol',
        '업종':'Sector',
    }
  
    df_listing = df_listing.rename(columns=cols_ren)
    df_listing['market'] = 'KRX'
    df_listing['Symbol'] = df_listing['Symbol'].apply(lambda x: '{:06d}'.format(x))
    # df_listing.to_csv('stock_krx.csv', encoding='utf-8-sig', index=False)
    # Now print the DataFrame
    print(df_listing)
    df_KR = df_listing[['Symbol', 'Name', 'market', 'Sector']]
  
    return df_KR

def search_ticker_list_US():
    """Search for US stock listings."""
    df_amex = fdr.StockListing('AMEX')
    df_amex.to_csv('stock_amex.csv', encoding='utf-8-sig', index=False)
  
    df_nasdaq = fdr.StockListing('NASDAQ')
    df_nyse = fdr.StockListing('NYSE')
    
    try:
        df_ETF_US = fdr.StockListing("ETF/US")
        df_ETF_US['market'] = "us_ETF"
        columns_to_select = ['Symbol', 'Name', 'market']
        df_ETF_US = df_ETF_US[columns_to_select]
    except Exception as e:
        print(f"An error occurred while fetching US ETF listings: {e}")
        df_ETF_US = pd.DataFrame(columns=['Symbol', 'Name', 'market'])
    
    df_amex['market'] = "AMEX"
    df_nasdaq['market'] = "NASDAQ"
    df_nyse['market'] = "NYSE"
    
    # If 'Industry' column exists, print it (you can remove this print if not needed)
    if 'Industry' in df_nyse.columns:
        print(df_nyse['Industry'])

    columns_to_select = ['Symbol', 'Name', 'market']
    df_amex = df_amex[columns_to_select]
    df_nasdaq = df_nasdaq[columns_to_select]
    df_nyse = df_nyse[columns_to_select]

    data_frames_US = [df_nasdaq, df_nyse, df_amex, df_ETF_US]
    
    df_US = pd.concat(data_frames_US, ignore_index=True)
    df_US['Sector'] = 'none'
    df_US = df_US[['Symbol', 'Name', 'market', 'Sector']]
    
    return df_US


# Other functions (omitted for brevity)

def search_ticker_list_US_ETF():
    # Fetch the list of ETFs traded in the United States
    df_etfs = investpy.etfs.get_etfs(country='united states')

    # Select only the 'Symbol' and 'Name' columns
    df_US_ETF = df_etfs[['symbol', 'name']].copy()

    # Assign 'US_ETF' to 'market' and 'Sector'
    df_US_ETF['market'] = 'US_ETF'
    df_US_ETF['Sector'] = 'US_ETF'

    # Convert column names to uppercase
    df_US_ETF.columns = ['Symbol', 'Name', 'market', 'Sector']
  
    return df_US_ETF

# Other code utilizing the transformed function (omitted for brevity)

def get_ticker_list_all():
    df_KR = search_ticker_list_KR()
    df_US = search_ticker_list_US()
    df_US_ETF = search_ticker_list_US_ETF()

    df_combined = pd.concat([df_KR, df_US, df_US_ETF], ignore_index=True)
    df_combined.to_csv('stock_market.csv', encoding='utf-8-sig', index=False)

    return df_combined

def get_ticker_from_korean_name(name):
    df_KR = search_ticker_list_KR()
    result = df_KR.loc[df_KR['Name'] == name, 'Symbol']
    ticker = result.iloc[0] if not result.empty else None
    return ticker

if __name__ == "__main__":
    # 사용 예시
    # get_ticker_list_all()
    tickers_to_update = [
    'VOO', 'QQQ', 'AAPL', 'GOOGL', 'MSFT','U', 'SPOT', 'PLTR','ADBE', 'TSLA', 'APTV', 
    'FSLR',  'PFE', 'INMD', 'UNH',  'TDOC', 'OXY', 'FSLR', 'ALB','AMZN', 'NFLX', 'LLY', 'EL',
    'NKE', 'LOW', 'ADSK', 'NIO', 'F', 'BA', 'GE', 'JPM', 'BAC', 'SQ', 'HD', 'PG',
    'IONQ','NVDA','AMD']
     # 여기에 필요한 티커 20개 추가
    
    # # 파일 경로 지정 및 CSV 파일 업데이트
    file_path = 'stock_market.csv'
    update_stock_market_csv(file_path, tickers_to_update)

    # search_ticker_list_US()
    # Use the function and assign the resulting DataFrame to a variable
    # df_US_ETF = search_ticker_list_US_ETF()
    # print(df_US_ETF)
      # # 파일 경로 지정 및 CSV 파일 업데이트
    # df_us = search_ticker_list_US()  # Call the function to retrieve the DataFrame
    # df_us.to_csv('us_stock_market.csv', encoding='utf-8-sig', index=False)  # Save the DataFrame to a CSV
    info = get_stock_info('AAPL')
    print(info)
    market = get_ticker_market('086520', file_path='stock_market.csv')
    print(market)