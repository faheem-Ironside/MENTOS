import requests
import telebot
import tools.kill
import asyncio
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import command handlers
from tools.auth_chk import handle_chk
from tools.auth_b3 import handle_b3
from tools.kill import handle_kill
from tools.charge_at import handle_at
from tools.charge_au import handle_au
from tools.other_info import handle_info
from tools.other_gen import handle_gen
from tools.vbv_check import handle_vbv  # ✅ Async function
from tools.other_fake import handle_fake
from tools.plan import add_user, remove_user, is_user_allowed

# ✅ Your bot token (Replace with your actual token)
TOKEN = "7069147116:AAF6jfs0LwW5PqG3h3eAjj5jgS5fFrlTwoQ"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

OWNER_ID = 7980317129  # Replace with your Telegram user ID
USER_FILE = "users.txt"  # File to store user IDs

# ✅ Function to save users
def save_user(user_id):
    try:
        with open(USER_FILE, "r") as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        users = []

    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(str(user_id) + "\n")

# ✅ Start Menu Button
def start_menu_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔎 Menu", callback_data="menu"))
    return markup

# ✅ Full Menu
def full_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔐 Auth Gates", callback_data="auth_gates"),
        InlineKeyboardButton("⚡ Charge Gates", callback_data="charge_gates"),
        InlineKeyboardButton("📜 CC Killer", callback_data="cc_killer"),
        InlineKeyboardButton("⚒ Other Commands", callback_data="other_commands"),
        InlineKeyboardButton("🛒 Buy Premium", url="https://t.me/faheem_Ironside")
    )
    return markup

# ✅ Back to Menu Button
def back_to_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("↩️ Menu", callback_data="menu"))
    return markup

# ✅ /start Command
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    save_user(user_id)  # ✅ Save user ID

    text = (
        "🤖 *Bot Status: Active* ✅\n\n"
        "📢 *For announcements and updates, join us 👉* [here](https://t.me/+zeonwU69EYswMDZl)\n\n"
        "💡 *Tip: To use this bot in your group, make sure to set it as an admin.*"
    )
    bot.reply_to(message, text, reply_markup=start_menu_button(), parse_mode="Markdown")

# ✅ Callback Handlers (Menu)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "menu":
        text = (
            "❓ *How can I assist you today?*\n\n"
            "🌟 *Stay updated for the latest features and improvements!*\n\n"
            "💎 *Upgrade to Premium for exclusive benefits.*"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text, reply_markup=full_menu(), parse_mode="Markdown")

    elif call.data == "auth_gates":
        text = (
            "*🔐 Auth Gates*\n\n"
            "📍 *Braintree Auth 1*\n"
            "/chk ✅ Active\n\n"
            "📍 *Braintree Auth 2*\n"
            "/b3 ✅ Active\n\n"
            "➕ *Adding more...*"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text, reply_markup=back_to_menu(), parse_mode="Markdown")

    elif call.data == "charge_gates":
        text = (
            "👿 *Charge Gates*\n\n"
            "📍 *Braintree Charge*\n"
            "/at ✅ Active\n\n"
            "📍 *Stripe Charge*\n"
            "/au ✅ Active\n\n"
            "➕ *Adding more...*"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text, reply_markup=back_to_menu(), parse_mode="Markdown")

    elif call.data == "cc_killer":
        text = (
            "🍒 *Turbo Killer*\n\n"
            "⏩ *Kill CC:* Command 👇\n"
            "`/kill cardnumber|mm|yy|cvc`\n\n"
            "⚠️ *Warning:* This is a Card Fucker Cmd!"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text, reply_markup=back_to_menu(), parse_mode="Markdown")

    elif call.data == "other_commands":
        text = (
            "💎 *Other Tools*\n\n"
            "🔎 *Check Details*\n"
            "/info ✅ Active\n\n"
            "📍 *Generate Cards*\n"
            "/gen ✅ Active\n\n"
            "☠️ *Fake Address US*\n"
            "/fake ✅ Active\n\n"
            "⭐ *Vbv Checker*\n"
            "/vbv ✅ Active\n\n"
            "[+] *Adding more...*"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text, reply_markup=back_to_menu(), parse_mode="Markdown")

# ✅ Command Handlers
@bot.message_handler(func=lambda message: message.text.startswith("/kill"))
def kill_command(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "🚫 *Access Denied!* Contact the owner.", parse_mode="Markdown")
        return
    handle_kill(bot, message)

@bot.message_handler(func=lambda message: message.text.startswith("/chk"))
def chk_command(message):
    handle_chk(bot, message)

@bot.message_handler(func=lambda message: message.text.startswith("/b3"))
def b3_command(message):
    handle_b3(bot, message)

@bot.message_handler(func=lambda message: message.text.startswith("/at"))
def at_command(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "🚫 *Access Denied!* Contact the owner.", parse_mode="Markdown")
        return
    handle_at(bot, message)

@bot.message_handler(func=lambda message: message.text.startswith("/au"))
def au_command(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "🚫 *Access Denied!* Contact the owner.", parse_mode="Markdown")
        return
    handle_au(bot, message)

@bot.message_handler(func=lambda message: message.text.startswith("/info"))
def info_command(message):
    handle_info(bot, message)

@bot.message_handler(func=lambda message: message.text.startswith("/vbv"))
def vbv_command(message):
    handle_vbv(bot, message)

@bot.message_handler(func=lambda message: message.text.startswith("/fake"))
def fake_command(message):
    handle_fake(bot, message)

# ✅ Async handler (Fixed `handle_gen`)
@bot.message_handler(func=lambda message: message.text.startswith("/gen"))
def gen_command(message):
    asyncio.run(handle_gen(bot, message))  # ✅ Runs async function properly in Termux

# ✅ Run the bot
print("🤖 Bot is running...")
bot.polling(none_stop=True)