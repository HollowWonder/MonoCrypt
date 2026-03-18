from psycopg import AsyncConnection
from pybit.unified_trading import HTTP

from database.handler import get_user_data
from bot.utils.bot_manager import get_bot

async def get_bybit_session(conn: AsyncConnection, uid: int) -> HTTP | None:
    try:
        user_data: dict[str, str] = await get_user_data(conn, uid)
        session: HTTP = HTTP(
            testnet=False,
            api_key=user_data.get('bybit_api'),
            api_secret=user_data.get('bybit_secret_key')
        )
        return session
    except Exception as e:
        return None

async def send_message(chat_id: int, text: str) -> None:
    bot = await get_bot()
    await bot.send_message(chat_id=chat_id, text=text)

async def send_monitoring(chat_id: int, category: str, crypto: str) -> None:
    try:
        bybit_session = HTTP(testnet=False)
        ticket = bybit_session.get_tickers(category=category, symbol=crypto)
        price = ticket['result']['list'][0]['lastPrice']
        text = f"{crypto} - {price}"
        await send_message(chat_id=chat_id, text=text)
    except Exception as e:
        await send_message(chat_id=chat_id, text=f"Error: {e}")

async def get_bybit_profile(conn: AsyncConnection, uid: int) -> str:
    bybit_session: HTTP = await get_bybit_session(conn=conn, uid=uid)
    text: str = "---Профиль ByBit"
    
    if bybit_session is None:
        return text + " - соединение отсутствует. Проверьте ключи---"

    text += "---\n\n"
    balance = bybit_session.get_wallet_balance(accountType="UNIFIED")
    account_info = balance['result']['list'][0]

    total_wallet_balance: str = float(account_info['totalWalletBalance'])
    total_equity: str = float(account_info['totalEquity'])
    
    text += (
        "--Общие сведения--\n"
        f"Баланс кошелька: {total_wallet_balance}\n"
        f"Цена всех активов: {total_equity}\n\n"
        )
    coins = account_info['coin']
    text += "--Активы (количество | стоимость в usd)--\n"
    for coin in coins:
        coin_name = coin['coin']
        usd_value = coin['usdValue']
        count = coin['walletBalance']
        text += f"{coin_name}: {count} | {usd_value}\n"

    return text