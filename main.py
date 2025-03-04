import asyncio
import logging
import os
import time  # For unique image cache-busting
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from dotenv import load_dotenv
from aiocron import crontab

from db import (get_user_status, init_db, save_user,
                update_frequency, update_status)
from messages import (
    START_MESSAGE, STOP_MESSAGE, WATER_FACTS, WATER_ARTICLES,
    REMINDER_MESSAGE, CUSTOM_FREQUENCY_PROMPT, INVALID_FREQUENCY_MESSAGE, KEYBOARD_OPTIONS
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CAT_API = os.getenv("CAT_API", "https://cataas.com/cat/cute/says/Drink%20Water")

# Ensure bot token is available
if not TOKEN:
    raise ValueError("Bot token is missing. Set TELEGRAM_BOT_TOKEN in .env")

# Initialize the database
init_db()

# Set up bot and dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)

@dp.message(Command("start"))
async def start_command(message: Message):
    chat_id = message.chat.id
    save_user(chat_id, active=1)
    await prompt_frequency(message)

@dp.message(Command("stop"))
async def stop_command(message: Message):
    chat_id = message.chat.id
    update_status(chat_id, active=0)
    await message.answer(STOP_MESSAGE)

@dp.message(Command("info"))
async def info_command(message: Message):
    await message.answer(WATER_FACTS + WATER_ARTICLES)

async def prompt_frequency(message: Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=KEYBOARD_OPTIONS)
    await message.answer(START_MESSAGE, reply_markup=keyboard)

@dp.message(lambda message: message.text.startswith("🐾 Every ") and message.text.split()[-2].isdigit())
async def handle_frequency_selection(message: Message):
    chat_id = message.chat.id
    selected_frequency = int(message.text.split()[-2])
    update_frequency(chat_id, selected_frequency)
    await message.answer(f"✅ You will receive water reminders every {selected_frequency} hours. 🐾")
    schedule_reminder(chat_id, selected_frequency)

@dp.message(F.text == "🐾 Custom")
async def ask_custom_frequency(message: Message):
    await message.answer(CUSTOM_FREQUENCY_PROMPT)

@dp.message(lambda message: message.text.strip().isdigit())
async def handle_custom_frequency(message: Message):
    chat_id = message.chat.id
    user_input = message.text.strip()
    if not user_input.isdigit():
        await message.answer(INVALID_FREQUENCY_MESSAGE)
        return
    custom_frequency = int(user_input)
    if not (1 <= custom_frequency <= 24):
        await message.answer(INVALID_FREQUENCY_MESSAGE)
        return
    update_frequency(chat_id, custom_frequency)
    await message.answer(f"✅ You will receive water reminders every {custom_frequency} hours. 🐾")
    schedule_reminder(chat_id, custom_frequency)

async def get_cute_image():
    url = f"{CAT_API}?{int(time.time())}"
    for _ in range(3):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return url
                    logging.warning(f"API returned {resp.status}, retrying...")
        except Exception as e:
            logging.error(f"Failed to fetch image: {e}")
        await asyncio.sleep(2)
    return CAT_API

def schedule_reminder(chat_id, frequency):
    crontab(f"0 */{frequency} * * *", func=send_reminders, args=(chat_id,))

async def send_reminders(chat_id):
    if get_user_status(chat_id) == 0:
        return
    try:
        cute_image = await get_cute_image()
        await bot.send_photo(chat_id, cute_image, caption=REMINDER_MESSAGE)
        logging.info(f"Sent reminder to {chat_id}")
    except Exception as e:
        logging.error(f"Failed to send reminder: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
