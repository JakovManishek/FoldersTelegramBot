import config
import asyncio
import texts.messages as messages


from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession


session = AiohttpSession(proxy='http://proxy.server:3128')
bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)
dp = Dispatcher()



@dp.message(Command(commands=["start", "help", "made_by"]))
async def start(message: Message):
    await message.answer(text=messages.TECHNICAL_JOB_TEXT)


@dp.callback_query(F.data)
async def inline_callback(callback: CallbackQuery):
    await callback.answer(text=messages.TECHNICAL_JOB_TEXT)
    

@dp.message()     
async def other_message(message: Message):
    if message.chat.type == "private":
        await message.answer(text=messages.TECHNICAL_JOB_TEXT)
    
    

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())