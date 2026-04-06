import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from psycopg import AsyncConnection
from pybit.unified_trading import HTTP

from database.handler import get_user_data, add_user, check_user, change_userdata
from cache import set_cache_data, get_cache_data, delete_cache

router: Router = Router()

@router.message(Command('start'))
async def start(message: Message, conn: AsyncConnection, logger: logging.Logger) -> None:
    " getting user status "
    logger.debug("used command command /start")

    uid: int = message.from_user.id
    cid: str = f"status:{uid}"

    text: str = await get_cache_data(cid)

    if text is None:
        await autocheck(conn, uid, username= message.from_user.username)
        user_data = await get_user_data(conn, uid)
        
        api_key = user_data.get('bybit_api')
        has_keys = api_key not in (None, 'none', 'None')
        
        text = (
            f"**Добро пожаловать!**\n\n"
            f"┌ **Ваш ID:** `{uid}`\n"
            f"└ **Bybit ключи:** {'✅ установлены' if has_keys else '❌ не установлены'}\n\n"
        )
        text += "!!!ОЗНАКОМЬТЕСЬ С КОМАНДАМИ: /help"

        await set_cache_data(cid, data = text, es = 60*60*24)

    await message.answer(text)


class Regist(StatesGroup):
    waiting_for_api = State()
    waiting_for_secret_key = State()

@router.message(Command('set_bybit_keys'))
async def set_bybit_api(message: Message, state: FSMContext, logger: logging.Logger) -> None:
    cid: str = f"status:{message.from_user.id}"
    await delete_cache(cid)

    logger.debug("user entering bybit api key")
    await state.set_state(Regist.waiting_for_api)
    await message.answer('Отправьте ваш API ключ Bybit')

@router.message(Regist.waiting_for_api)
async def set_bybit_secret_key(message: Message, state: FSMContext, logger: logging.Logger) -> None:
    logger.debug("user entering bybit secret key")
    api: str = message.text.strip()

    await state.update_data(api=api)
    await state.set_state(Regist.waiting_for_secret_key)
    await message.answer('Отправьте ваш секретный API ключ ByBit')

@router.message(Regist.waiting_for_secret_key)
async def set_bybit_secret_key(message: Message, state: FSMContext, conn: AsyncConnection, logger: logging.Logger) -> None:
    data = await state.get_data()
    api: str = data.get('api')
    secret: str = message.text.strip()

    uid: int = message.from_user.id
    try:
        await change_userdata(conn, uid, "bybit_api", api)
        await change_userdata(conn, uid, "bybit_secret_key", secret)

        session: HTTP = HTTP(
            testnet=False,
            api_key=api,
            api_secret=secret)
        test = session.get_wallet_balance(accountType="UNIFIED")

        logger.debug('user keys was saved')
        await message.answer('Ключи успешно сохранены')
    except Exception as e:
        logger.warning('something went wrong in saving user keys')
        await message.answer('Произошла ошибка, попробуйте снова')
    finally:
        await state.clear()

async def autocheck(conn: AsyncConnection, uid: int, username: str) -> None:
    """ cheching user in database or not """
    check: bool = await check_user(conn, uid)
    if check:
        return None
    
    await add_user(conn, uid, username, "None", "None")