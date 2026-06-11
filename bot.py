import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    ChatJoinRequest,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    FSInputFile,
    CallbackQuery
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = -1004296793908
GEM_IMAGE = "gems.png"
GEM_LINK = "https://gclick.su?ref=gemes"
ADMIN_ID = 1989200344

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Храним заявки и статистику
pending_requests = {}
unsubscribed = set()  # Кто отписался от рассылки
total_received = 0
total_accepted = 0


def get_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Забрать 2000 Гемов", url=GEM_LINK)],
        [InlineKeyboardButton(text="🔕 Отключить рассылку", callback_data="unsubscribe")]
    ])


async def send_gems_message(user_id, first_name):
    text = (
        f"Привет, {first_name}! 👋\n\n"
        "Твоя заявка на рассмотрении!\n\n"
        "Пока ждёшь — можешь получить 2000 гемов за 10 рублей? Нажми кнопку 👇"
    )
    try:
        if os.path.isfile(GEM_IMAGE):
            photo = FSInputFile(GEM_IMAGE)
            await bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=text,
                reply_markup=get_keyboard()
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=get_keyboard()
            )
        return True
    except Exception as e:
        logging.error(f"Ошибка отправки {user_id}: {e}")
        return False


@dp.callback_query(F.data == "unsubscribe")
async def unsubscribe(callback: CallbackQuery):
    user_id = callback.from_user.id
    unsubscribed.add(user_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("✅ Рассылка отключена!", show_alert=False)
    await callback.message.answer("🔕 Ты отписался от рассылки. Больше напоминаний не будет.")


@dp.chat_join_request(F.chat.id == CHANNEL_ID)
async def handle_join_request(request: ChatJoinRequest):
    global total_received
    user = request.from_user
    pending_requests[user.id] = {
        "request": request,
        "first_name": user.first_name,
        "time": datetime.now()
    }
    total_received += 1
    await send_gems_message(user.id, user.first_name)


@dp.message(Command("accept_all"))
async def accept_all(message: Message):
    global total_accepted
    if message.from_user.id != ADMIN_ID:
        return

    count = len(pending_requests)
    if count == 0:
        await message.answer("📭 Заявок нет!")
        return

    await message.answer(f"⏳ Принимаю {count} заявок...")
    accepted = 0
    failed = 0

    for user_id, data in list(pending_requests.items()):
        try:
            await bot.approve_chat_join_request(chat_id=CHANNEL_ID, user_id=user_id)
            accepted += 1
            total_accepted += 1
            del pending_requests[user_id]
            await asyncio.sleep(0.05)
        except Exception as e:
            logging.error(f"Ошибка принятия {user_id}: {e}")
            failed += 1

    await message.answer(f"✅ Принято: {accepted}\n❌ Ошибок: {failed}")


@dp.message(Command("count"))
async def count_requests(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(f"📊 Заявок в очереди: {len(pending_requests)}\n🔕 Отписавшихся: {len(unsubscribed)}")


@dp.message(Command("stats"))
async def stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        f"📊 Статистика:\n\n"
        f"📥 Всего заявок: {total_received}\n"
        f"✅ Принято: {total_accepted}\n"
        f"⏳ В очереди: {len(pending_requests)}\n"
        f"🔕 Отписавшихся: {len(unsubscribed)}"
    )


@dp.message(Command("post"))
async def post(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/post", "").strip()
    if not text:
        await message.answer("❌ Напиши текст!\nПример: /post Ваучеры готовы! 🎁")
        return

    count = len([u for u in pending_requests if u not in unsubscribed])
    if count == 0:
        await message.answer("📭 Нет пользователей для рассылки!")
        return

    await message.answer(f"⏳ Рассылаю {count} пользователям...")
    sent = 0
    failed = 0

    for user_id in pending_requests:
        if user_id in unsubscribed:
            continue
        try:
            await bot.send_message(chat_id=user_id, text=text)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            logging.error(f"Ошибка рассылки {user_id}: {e}")
            failed += 1

    await message.answer(f"✅ Отправлено: {sent}\n❌ Ошибок: {failed}")


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Бот активен! ✅")


async def reminder_task():
    await asyncio.sleep(15 * 60)
    while True:
        active = [u for u in pending_requests if u not in unsubscribed]
        if active:
            logging.info(f"Авто-напоминание: {len(active)} пользователей")
            for user_id in active:
                data = pending_requests[user_id]
                await send_gems_message(user_id, data["first_name"])
                await asyncio.sleep(0.05)
        await asyncio.sleep(15 * 60)


async def main():
    asyncio.create_task(reminder_task())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
