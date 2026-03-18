from aiogram import Bot

global_bot: Bot = None

def set_bot(bot) -> None:
    global global_bot
    global_bot = bot

async def get_bot() -> Bot:
    return global_bot 