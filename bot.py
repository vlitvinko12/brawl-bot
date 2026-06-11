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
CHANNEL_ID = -1004296793908
GEM_IMAGE = "gems.png"
GEM_LINK = "https://gclick.su?ref=gemes"

# Твой Telegram ID — только ты можешь использовать /accept_all
ADMIN_ID = 1989200344  # Замени на свой Telegram ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Храним заявки в памяти
pending_requests = {}


@dp.chat_join_request(F.chat.id == CHANNEL_ID)
async def handle_join_request(request: ChatJoinRequest):
    user = request.from_user

    # Сохраняем заявку
    pending_requests[user.id] = request

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💎 Забрать 2000 Гемов",
            url=GEM_LINK
        )]
    ])

    text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Твоя заявка на рассмотрении!\n\n"
        "Пока ждёшь — можешь получить 2000 гемов за 10 рублей? Нажми кнопку 👇"
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
        logging.error(f"Ошибка отправки: {e}")


@dp.message(Command("accept_all"))
async def accept_all(message: Message):
    if ADMIN_ID and message.from_user.id != ADMIN_ID:
        await message.answer("❌ У тебя нет прав!")
        return

    count = len(pending_requests)
    if count == 0:
        await message.answer("📭 Заявок нет!")
        return

    await message.answer(f"⏳ Принимаю {count} заявок...")

    accepted = 0
    failed = 0

    for user_id, request in list(pending_requests.items()):
        try:
            await bot.approve_chat_join_request(
                chat_id=CHANNEL_ID,
                user_id=user_id
            )
            accepted += 1
            del pending_requests[user_id]
            await asyncio.sleep(0.05)  # Небольшая пауза чтобы не превысить лимиты
        except Exception as e:
            logging.error(f"Ошибка принятия {user_id}: {e}")
            failed += 1

    await message.answer(
        f"✅ Принято: {accepted}\n"
        f"❌ Ошибок: {failed}"
    )


@dp.message(Command("count"))
async def count_requests(message: Message):
    if ADMIN_ID and message.from_user.id != ADMIN_ID:
        await message.answer("❌ У тебя нет прав!")
        return
    await message.answer(f"📊 Заявок в очереди: {len(pending_requests)}")


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Бот активен! ✅")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
