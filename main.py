import asyncio
import logging
import os
import random

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from dotenv import load_dotenv

from db import (get_user_status, init_db, save_user,
                update_frequency, update_status)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Cute cat image API
CAT_API = "https://cataas.com/cat/cute/says/Drink%20Water"

# Initialize the database
init_db()

# Set up bot and dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Start command
@dp.message(Command("start"))
async def start_command(message: Message):
    chat_id = message.chat.id
    save_user(chat_id, active=1)  # Ensure user is set as active
    await prompt_frequency(message)

# Stop command
@dp.message(Command("stop"))
async def stop_command(message: Message):
    chat_id = message.chat.id
    update_status(chat_id, active=0)  # Set status to inactive
    await message.answer("🚫 Water reminders stopped. Stay hydrated though!")

# Info command
@dp.message(Command("info"))
async def info_command(message: Message):
    water_facts = (
        "💧 Staying hydrated helps maintain energy levels and brain function.",
        "🚰 Drinking enough water can help prevent headaches and improve focus.",
        "🩺 Proper hydration supports kidney and heart health.",
        "🥤 Recommended daily intake: **8 glasses (2 liters)** of water per day."
    )

    water_articles = (
        "1️⃣ [Healthline: How Much Water Should You Drink Per Day?](https://www.healthline.com/nutrition/how-much-water-should-you-drink-per-day)",
        "2️⃣ [Mayo Clinic: Water: How much should you drink every day?](https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/water/art-20044256)",
        "3️⃣ [Medical News Today: 15 benefits of drinking water](https://www.medicalnewstoday.com/articles/290814)"
    )

    info_text = "**Why is drinking water important?**\n" + "\n".join(water_facts) + "\n\n" \
                "**More Resources on Hydration:**\n" + "\n".join(water_articles)

    await message.answer(info_text)

# Prompt user for reminder frequency
async def prompt_frequency(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Every 2 hours")],
                  [KeyboardButton(text="Every 4 hours")],
                  [KeyboardButton(text="Every 6 hours")]],
        resize_keyboard=True
    )
    await message.answer("How often would you like to receive water reminders?", reply_markup=keyboard)

# Handle frequency selection
@dp.message(lambda message: message.text in ["Every 2 hours", "Every 4 hours", "Every 6 hours"])
async def handle_frequency_selection(message: Message):
    chat_id = message.chat.id
    frequency_map = {"Every 2 hours": 2, "Every 4 hours": 4, "Every 6 hours": 6}
    selected_frequency = frequency_map[message.text]

    update_frequency(chat_id, selected_frequency)  # Update frequency & reactivate user
    await message.answer(f"✅ You will receive water reminders every {selected_frequency} hours.")
    asyncio.create_task(send_reminders(chat_id, selected_frequency))

# Fetch new cat image each time
async def get_cute_image():
    return f"{CAT_API}?{random.randint(1, 10000)}"

# Periodic reminder function
async def send_reminders(chat_id, frequency):
    while True:
        if get_user_status(chat_id) == 0:
            break  # Stop if user disabled reminders

        cute_image = await get_cute_image()
        reminder_text = "💧 Hey hooman! Time to drink some water! Stay hydrated!"

        await bot.send_photo(chat_id, cute_image, caption=reminder_text)
        await asyncio.sleep(frequency * 3600)  # Send reminders based on frequency

# Bot startup
async def on_startup():
    logging.basicConfig(level=logging.INFO)
    print("Bot is running...")

# Run bot
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
