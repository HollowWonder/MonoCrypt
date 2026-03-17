from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router: Router = Router()

@router.message(Command('get_id'))
async def get_id(message: Message) -> None:
    await message.answer(text=f'uid: {message.from_user.id}')