import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from psycopg import AsyncConnection
from pybit.unified_trading import HTTP

from database.handler import get_user_data, add_user, check_user, change_userdata

from bot.utils.bot_manager import get_bybit_session

router: Router = Router()

@router.message(Command('start'))
async def start(message: Message, conn: AsyncConnection, logger: logging.Logger) -> None:
    " getting user status "
    logger.debug("used command command /start")

    uid = message.from_user.id
    await autocheck(conn, uid, username= message.from_user.username)
    user_data = await get_user_data(conn, uid)
    
    api_key = user_data.get('bybit_api')
    has_keys = api_key not in (None, 'none', 'None')
    
    text = (
        f"Статус аккаунта\n"
        f"ID: {uid}\n"
        f"BYBIT - ключи: {'✅' if has_keys else '❌'}\n\n"
    )
    text += (
        "Доступные команды:\n"
        "/set_bybit_keys - установить новые ключи\n"
        "/profile - посмотреть информацию о портфеле\n\n"
        "/mono - запустить мониторинг крипты\n"
        "ПРИМЕР: /mono BTCUSDT interval 60 - запускает мониторинг крипты BTC с интервалом в 1 минуту"
    )
    logger.debug('message is sending')
    await message.answer(text)


class Regist(StatesGroup):
    waiting_for_api = State()
    waiting_for_secret_key = State()

@router.message(Command('set_bybit_keys'))
async def set_bybit_api(message: Message, state: FSMContext, logger: logging.Logger) -> None:
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
    check: bool = await check_user(conn, uid)
    if check:
        return None
    
    await add_user(conn, uid, username, "None", "None")