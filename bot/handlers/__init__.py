from aiogram import Router

import bot.handlers.useful
import bot.handlers.registration
import bot.handlers.bybit
import bot.handlers.info

router: Router = Router()

router.include_router(useful.router)
router.include_router(registration.router)
router.include_router(bybit.router)
router.include_router(info.router)