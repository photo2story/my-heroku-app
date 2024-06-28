# app.py
# app.py
from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import requests
import sys
import certifi
import threading
import logging
import nest_asyncio

logging.basicConfig(level=logging.INFO)

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), 'my-flask-app'))

from datetime import datetime
import pandas as pd
import numpy as np
from get_ticker import load_tickers, search_tickers, get_ticker_name, update_stock_market_csv
from estimate_stock import estimate_snp, estimate_stock
from Results_plot import plot_comparison_results, plot_results_all
from get_compare_stock_data import merge_csv_files, load_sector_info
from Results_plot_mpl import plot_results_mpl
from get_ticker import get_ticker_from_korean_name

os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/save_search_history', methods=['POST'])
def save_search_history():
    data = request.json
    stock_name = data.get('stock_name')
    print(f'Saved {stock_name} to search history.')
    return jsonify({"success": True})

@app.route('/api/get_images', methods=['GET'])
def get_images():
    image_folder = os.path.join(app.static_folder, 'images')
    images = []
    for filename in os.listdir(image_folder):
        if filename.endswith('.png'):
            images.append(filename)
    return jsonify(images)

sent_messages = {}

def reset_sent_messages():
    global sent_messages
    sent_messages = {}
    threading.Timer(10.0, reset_sent_messages).start()

reset_sent_messages()

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='', intents=intents)

stocks = ['QQQ', 'NVDA', 'BAC', 'COIN']
start_date = "2022-01-01"
end_date = datetime.today().strftime('%Y-%m-%d')
initial_investment = 30000000
monthly_investment = 1000000

processed_message_ids = set()

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
    if not hasattr(bot, 'is_logged_in') or not bot.is_logged_in:
        bot.is_logged_in = True
        print(f'Logged in as {bot.user.name}')
        channel = bot.get_channel(int(CHANNEL_ID))
        if channel:
            await channel.send(f'Bot has successfully logged in: {bot.user.name}')

@bot.command()
async def ping(ctx):
    if ctx.message.id not in processed_message_ids:
        processed_message_ids.add(ctx.message.id)
        await ctx.send(f'pong: {bot.user.name}')

def run_discord_bot():
    nest_asyncio.apply()
    bot.run(TOKEN)

if __name__ == '__main__':
    discord_thread = threading.Thread(target=run_discord_bot)
    discord_thread.start()
    app.run(debug=True)


# # # .\.venv\Scripts\activate
# #  python app.py 
# git add runtime.txt
# git commit -m "Update Python runtime to a supported version"
# git push heroku main
