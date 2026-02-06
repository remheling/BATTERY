import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from bot.config import BOT_TOKEN
from bot.handlers import (
    guard_commands,
    add_admin,
    del_admin,
    mute_status,
    reset_mute,
    reset_mute_one
)
from keep_alive import keep_alive


async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(add_admin, Command("add_admin"))
    dp.message.register(del_admin, Command("del_admin"))
    dp.message.register(mute_status, Command("mute_status"))
    dp.message.register(reset_mute, Command("reset_mute"))
    dp.message.register(reset_mute_one, Command("reset_mute_one"))
    dp.message.register(guard_commands, F.text)

    await dp.start_polling(bot)


if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
