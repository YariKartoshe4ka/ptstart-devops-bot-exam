import asyncio
import logging
import sys
from os import getenv
from time import sleep

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.engine import URL

from commands.regex import router as regex_router
from commands.server import router as server_router
from middlewares import DbSessionMiddleware
from db.models import Base


dp = Dispatcher()
dp.include_router(regex_router)
dp.include_router(server_router)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Добро пожаловать!")


async def main() -> None:
    load_dotenv()

    engine = create_async_engine(
        url=URL.create(
            'postgresql+asyncpg',
            username=getenv('DB_USER'),
            password=getenv('DB_PASSWORD'),
            host=getenv('DB_HOST'),
            port=getenv('DB_PORT'),
            database=getenv('DB_DATABASE')
        ),
        echo=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(token=getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    await dp.start_polling(bot)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, filename='logs.txt', filemode='w')
    asyncio.run(main())
