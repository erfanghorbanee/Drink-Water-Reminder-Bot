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
    await message.answer("🚫 Water reminders stopped. Stay hydrated though! 🐾")

@dp.message(Command("info"))
async def info_command(message: Message):
    water_facts = (
        "💧 **Staying hydrated helps maintain energy levels and brain function.**\n\n"
        "🚰 **Drinking enough water can help prevent headaches and improve focus.**\n\n"
        "🩺 **Proper hydration supports kidney and heart health.**\n\n"
        "🥤 **Recommended daily intake: 8 glasses (2 liters) of water per day.**\n\n"
    )
    water_articles = (
        "📚 **More Resources on Hydration:**\n\n"
        "1️⃣ [Healthline: How Much Water Should You Drink Per Day?](https://www.healthline.com/nutrition/how-much-water-should-you-drink-per-day)\n\n"
        "2️⃣ [Mayo Clinic: Water: How much should you drink every day?](https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/water/art-20044256)\n\n"
        "3️⃣ [Medical News Today: 15 benefits of drinking water](https://www.medicalnewstoday.com/articles/290814)"
    )
    await message.answer(water_facts + water_articles)

async def prompt_frequency(message: Message):
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton("🐾 Every 2 hours"), KeyboardButton("🐾 Every 4 hours")],
            [KeyboardButton("🐾 Every 6 hours"), KeyboardButton("🐾 Custom")]
        ]
    )
    await message.answer("🐾 How often would you like to receive water reminders? 🐾", reply_markup=keyboard)

@dp.message(lambda message: message.text.startswith("🐾 Every ") and message.text.split()[-2].isdigit())
async def handle_frequency_selection(message: Message):
    chat_id = message.chat.id
    selected_frequency = int(message.text.split()[-2])
    update_frequency(chat_id, selected_frequency)
    await message.answer(f"✅ You will receive water reminders every {selected_frequency} hours. 🐾")
    schedule_reminder(chat_id, selected_frequency)

@dp.message(F.text == "🐾 Custom")
async def ask_custom_frequency(message: Message):
    await message.answer("🐾 Please enter the number of hours between reminders (e.g., `3` for every 3 hours). 🐾")

@dp.message(lambda message: message.text.strip().isdigit())
async def handle_custom_frequency(message: Message):
    chat_id = message.chat.id
    user_input = message.text.strip()
    if not user_input.isdigit():
        await message.answer("❌ Invalid input. Please enter a number between 1 and 24. 🐾")
        return
    custom_frequency = int(user_input)
    if not (1 <= custom_frequency <= 24):
        await message.answer("❌ Please enter a number between 1 and 24. 🐾")
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
        await bot.send_photo(chat_id, cute_image, caption="💧 Time to drink water! 🐾")
        logging.info(f"Sent reminder to {chat_id}")
    except Exception as e:
        logging.error(f"Failed to send reminder: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
