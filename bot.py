import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    ChatJoinRequest,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    FSInputFile
)
from config import BOT_TOKEN, CHANNEL_ID, GEM_IMAGE_URL, GEM_LINK
import os

logging.basicConfig(level=logging.INFO)

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
        "Пока ждёшь — забери 2000 гемов ниже? Нажми кнопку 👇"
    )

    try:
        if GEM_IMAGE_URL and os.path.isfile(GEM_IMAGE_URL):
            photo = FSInputFile(GEM_IMAGE_URL)
            await bot.send_photo(
                chat_id=user.id,
                photo=photo,
                caption=text,
                reply_markup=keyboard
            )
        elif GEM_IMAGE_URL and GEM_IMAGE_URL.startswith("http"):
            await bot.send_photo(
                chat_id=user.id,
                photo=GEM_IMAGE_URL,
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
        logging.error(f"Не удалось отправить сообщение пользователю {user.id}: {e}")


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Бот активен! ✅\nЖду заявок в канал...")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
