import requests
import telebot
import asyncio
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import command handlers
from tools.auth_chk import handle_chk
from tools.auth_b3 import handle_b3
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
        InlineKeyboardButton("📜 CC Killer [Coming Soon]", callback_data="cc_killer"),
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

    elif call.data == "other_commands":
        text = (
            "💎 *Other Tools*\n\n"
            "🔎 *Check Details*\n"
            "/info ✅ Active\n\n"
            "📍 *Generate Cards*\n"
            "/gen ✅ Active\n\n"
            "☠️ *Fake Address US*\n"
            "/fake ✅ Active\n\n"
            "[+] *Adding more...*"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text, reply_markup=back_to_menu(), parse_mode="Markdown")

# ✅ Check command prefixes ("/" and ".")
def is_valid_command(text, command):
    return text.startswith(f"/{command}") or text.startswith(f".{command}")

# ✅ Command Handlers
@bot.message_handler(func=lambda message: is_valid_command(message.text, "chk"))
def chk_command(message):
    handle_chk(bot, message)

@bot.message_handler(func=lambda message: is_valid_command(message.text, "b3"))
def b3_command(message):
    handle_b3(bot, message)

@bot.message_handler(func=lambda message: is_valid_command(message.text, "at"))
def at_command(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "🚫 *Access Denied!* Contact the owner.", parse_mode="Markdown")
        return
    handle_at(bot, message)

@bot.message_handler(func=lambda message: is_valid_command(message.text, "au"))
def au_command(message):
    if not is_user_allowed(message.from_user.id):
        bot.reply_to(message, "🚫 *Access Denied!* Contact the owner.", parse_mode="Markdown")
        return
    handle_au(bot, message)

@bot.message_handler(func=lambda message: is_valid_command(message.text, "info"))
def info_command(message):
    handle_info(bot, message)

@bot.message_handler(func=lambda message: is_valid_command(message.text, "vbv"))
def vbv_command(message):
    handle_vbv(bot, message)

@bot.message_handler(func=lambda message: is_valid_command(message.text, "fake"))
def fake_command(message):
    handle_fake(bot, message)

# ✅ Async handler (Fixed `handle_gen`)
@bot.message_handler(func=lambda message: is_valid_command(message.text, "gen"))
def gen_command(message):
    asyncio.run(handle_gen(bot, message))  # ✅ Runs async function properly in Termux

# ✅ Plan Command (Owner Only)
@bot.message_handler(commands=['plan'])
def plan_command(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "*You are not authorized to use this command!*", parse_mode="Markdown")
        return

    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "*Usage:* `/plan add <user_id>` or `/plan remove <user_id>`", parse_mode="Markdown")
        return

    action, user_id = parts[1], int(parts[2])

    if action == "add":
        add_user(user_id)
        bot.reply_to(message, f"*User {user_id} added to Charge commands access!* ✅", parse_mode="Markdown")
    elif action == "remove":
        remove_user(user_id)
        bot.reply_to(message, f"*User {user_id} removed from Charge commands access!* ❌", parse_mode="Markdown")
    else:
        bot.reply_to(message, "*Invalid action! Use `add` or `remove`.*", parse_mode="Markdown")

# ✅ Broadcast Command (Owner Only)
@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "🚫 *You are not authorized to use this command!*", parse_mode="Markdown")
        return

    text = message.text.replace("/broadcast", "").strip()
    if not text:
        bot.reply_to(message, "⚠️ *Usage:* `/broadcast <message>`", parse_mode="Markdown")
        return

    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()

    for user_id in users:
        try:
            bot.send_message(user_id, f"📢 {text}", parse_mode="Markdown")
        except:
            pass

# ✅ Run the bot
print("🤖 Bot is running...")
bot.polling(none_stop=True)