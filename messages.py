from aiogram.types import KeyboardButton

# General messages
START_MESSAGE = "🐾 How often would you like to receive water reminders? 🐾"
STOP_MESSAGE = "🚫 Water reminders stopped. Stay hydrated though! 🐾"

# Info messages
WATER_FACTS = (
    "💧 **Staying hydrated helps maintain energy levels and brain function.**\n\n"
    "🚰 **Drinking enough water can help prevent headaches and improve focus.**\n\n"
    "🩺 **Proper hydration supports kidney and heart health.**\n\n"
    "🥤 **Recommended daily intake: 8 glasses (2 liters) of water per day.**\n\n"
)

WATER_ARTICLES = (
    "📚 **More Resources on Hydration:**\n\n"
    "1️⃣ [Healthline: How Much Water Should You Drink Per Day?](https://www.healthline.com/nutrition/how-much-water-should-you-drink-per-day)\n\n"
    "2️⃣ [Mayo Clinic: Water: How much should you drink every day?](https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/water/art-20044256)\n\n"
    "3️⃣ [Medical News Today: 15 benefits of drinking water](https://www.medicalnewstoday.com/articles/290814)"
)

# Reminder messages
REMINDER_MESSAGE = "💧 Time to drink water! 🐾"
CUSTOM_FREQUENCY_PROMPT = "🐾 Please enter the number of hours between reminders (e.g., `3` for every 3 hours). 🐾"
INVALID_FREQUENCY_MESSAGE = "❌ Please enter a number between 1 and 24. 🐾"

# Keyboard buttons
KEYBOARD_OPTIONS = [
    [KeyboardButton(text="🐾 Every 2 hours"), KeyboardButton(text="🐾 Every 4 hours")],
    [KeyboardButton(text="🐾 Every 6 hours"), KeyboardButton(text="🐾 Custom")]
]
