from aiogram import Bot

from psycopg import AsyncConnection
from pybit.unified_trading import HTTP

from database.handler import get_user_data

global_bot: Bot = None

def set_bot(bot) -> None:
    global global_bot
    global_bot = bot

async def get_bot() -> Bot:
    return global_bot 

async def get_bybit_session(conn: AsyncConnection, uid: int) -> None:
    user_data: dict[str, str] = get_user_data(conn, uid)
    session: HTTP = HTTP(
        testnet=False,
        api_key=user_data.get('bybit_api'),
        api_secret=user_data('bybit_secret_key')
    )
    return session

async def send_monitoring(chat_id: int, category: str, crypto: str) -> None:
    try:
        bybit_session = HTTP(testnet=False)
        ticket = bybit_session.get_tickers(category=category, symbol=crypto)
        price = ticket['result']['list'][0]['lastPrice']
        text = f"{crypto} - {price}"
        await send_message(chat_id=chat_id, text=text)
    except Exception as e:
        await send_message(chat_id=chat_id, text=f"Error: {e}")