import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    ChatJoinRequest,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    FSInputFile
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = -4296793908
GEM_IMAGE = "gems.png"
GEM_LINK = "https://gclick.su?ref=gemes"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.chat_join_request(F.chat.id == CHANNEL_ID)
async def handle_join_request(request: ChatJoinRequest):
    user = request.from_user

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💎 Забрать 2000 Гемов",
            url=GEM_LINK
        )]
    ])

    text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Твоя заявка на рассмотрении!\n\n"
        "Пока ждёшь забери 2000 гемов по кнопке ниже 👇"
    )

    try:
        if os.path.isfile(GEM_IMAGE):
            photo = FSInputFile(GEM_IMAGE)
            await bot.send_photo(
                chat_id=user.id,
                photo=photo,
                caption=text,
                reply_markup=keyboard
            )
        else:
            await bot.send_message(
                chat_id=user.id,
                text=text,
                reply_markup=keyboard
            )
    except Exception as e:
        logging.error(f"Ошибка: {e}")


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Бот активен! ✅")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
