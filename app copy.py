# app.py
from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
from threading import Thread
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import requests
import sys
import certifi
import threading
# from celery import Celery


# 콘솔 출력 인코딩을 UTF-8로 설정
sys.stdout.reconfigure(encoding='utf-8')

# 현재 디렉토리 경로를 시스템 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flask-app'))
# Your Discord bot setup and run logic should follow here
from datetime import datetime
import pandas as pd
import numpy as np
from get_ticker import load_tickers, search_tickers, get_ticker_name, update_stock_market_csv
from estimate_stock import estimate_snp, estimate_stock
from Results_plot import plot_comparison_results, plot_results_all
from get_compare_stock_data import merge_csv_files, load_sector_info
from Results_plot_mpl import plot_results_mpl
import xml.etree.ElementTree as ET
from get_ticker import get_ticker_from_korean_name

# SSL 인증서 설정
os.environ['SSL_CERT_FILE'] = certifi.where()

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)

# Celery 설정
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)

# @celery.task
# def long_running_task():
#     # 오래 걸리는 작업을 여기에 작성
#     pass

@app.route("/start-task")
def start_task():
    task = long_running_task.apply_async()
    return jsonify({"task_id": task.id}), 202

@app.route("/api/data")
def get_data():
    sample_data = {"message": "Hello from Flask!"}
    return jsonify(sample_data)

# def run():
#     app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

# # Flask 서버 실행
# def keep_alive():
#     server = Thread(target=run)
#     server.start()

# keep_alive()

# Discord 설정
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.all()
intents.message_content = True
# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='', intents=intents)

# Backtesting 관련 코드
from datetime import datetime
from estimate_stock import estimate_stock, estimate_snp
from Results_plot import plot_comparison_results
from get_ticker import get_ticker_name, get_ticker_from_korean_name

stocks = ['QQQ', 'NVDA', 'BAC', 'COIN']
start_date = "2022-01-01"
end_date = datetime.today().strftime('%Y-%m-%d')
initial_investment = 30000000
monthly_investment = 1000000

async def backtest_and_send(ctx, stock, option_strategy):
    total_account_balance, total_rate, str_strategy, invested_amount, str_last_signal, min_stock_data_date, file_path, result_df = estimate_stock(
        stock, start_date, end_date, initial_investment, monthly_investment, option_strategy)
    min_stock_data_date = str(min_stock_data_date).split(' ')[0]
    user_stock_file_path1 = file_path

    file_path = estimate_snp(stock, 'VOO', min_stock_data_date, end_date, initial_investment, monthly_investment, option_strategy, result_df)
    user_stock_file_path2 = file_path

    name = get_ticker_name(stock)
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    message = {
        'content': f"Stock: {stock} ({name})\n"
                   f"Total_rate: {total_rate:,.0f} %\n"
                   f"Invested_amount: {invested_amount:,.0f} $\n"
                   f"Total_account_balance: {total_account_balance:,.0f} $\n"
                   f"Last_signal: {str_last_signal} \n"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=message)
    if response.status_code != 204:
        print('Failed to send Discord message')
    else:
        print('Successfully sent Discord message')

    plot_comparison_results(user_stock_file_path1, user_stock_file_path2, stock, 'VOO', total_account_balance, total_rate, str_strategy, invested_amount, min_stock_data_date)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Waiting"))

@bot.command()
async def buddy(ctx):
    loop = asyncio.get_running_loop()
    for stock in stocks:
        await backtest_and_send(ctx, stock, 'modified_monthly')
        plot_results_mpl(stock, start_date, end_date)
        await asyncio.sleep(2)
    await ctx.send("Backtesting results have been organized.")

@bot.command()
async def ticker(ctx, *, query: str = None):
    print(f'Command received: ticker with query: {query}')
    if query is None:
        await ctx.send("Please enter ticker stock name or ticker.")
        return

    ticker_dict = load_tickers()
    matching_tickers = search_tickers(query, ticker_dict)

    if not matching_tickers:
        await ctx.send("No search results.")
        return

    response_message = "Search results:\n"
    response_messages = []
    for symbol, name in matching_tickers:
        line = f"{symbol} - {name}\n"
        if len(response_message) + len(line) > 2000:
            response_messages.append(response_message)
            response_message = "Search results (continued):\n"
        response_message += line

    if response_message:
        response_messages.append(response_message)

    for message in response_messages:
        await ctx.send(message)
    print(f'Sent messages for query: {query}')

@bot.command()
async def stock(ctx, *args):
    stock_name = ' '.join(args)
    await ctx.send(f'Arguments passed by command: {stock_name}')
    try:
        info_stock = str(stock_name).upper()
        if info_stock.startswith('K '):
            korean_stock_name = info_stock[2:].upper()
            korean_stock_code = get_ticker_from_korean_name(korean_stock_name)
            if korean_stock_code is None:
                await ctx.send(f'Cannot find the stock {korean_stock_name}.')
                return
            else:
                info_stock = korean_stock_code

        await backtest_and_send(ctx, info_stock, option_strategy='1')
        plot_results_mpl(info_stock, start_date, end_date)
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')

@bot.command()
async def show_all(ctx):
    try:
        await plot_results_all()
        await ctx.send("All results have been successfully displayed.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        print(f"Error: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send(f'Bot has successfully logged in: {bot.user.name}')

# ping 명령어 중복 확인 후 등록
if not bot.get_command('ping'):
    @bot.command()
    async def ping(ctx):
        await ctx.send('pong')

def run_discord_bot():
    bot.run(TOKEN)

# Discord Bot을 별도의 스레드에서 실행
discord_thread = threading.Thread(target=run_discord_bot)
discord_thread.start()

if __name__ == '__main__':
    app.run(debug=True)
# # # .\.venv\Scripts\activate
# python app.py 