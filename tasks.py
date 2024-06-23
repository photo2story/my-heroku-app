from celery_config import app
import asyncio

stocks = ['AAPL', 'MSFT', 'GOOGL']  # 예시 주식 목록

async def backtest_and_send(stock):
    # 백테스트 및 결과 전송 로직
    pass

@app.task
def run_discord_tasks():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_tasks())

async def run_tasks():
    for stock in stocks:
        await backtest_and_send(stock)
        await asyncio.sleep(2)
    print("All tasks have been started.")
