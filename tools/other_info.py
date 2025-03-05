from telebot.types import Message

def handle_info(bot, message: Message):
    user_id = message.from_user.id
    user_info = bot.get_chat(user_id)
    user_status = bot.get_chat_member(user_info.id, user_info.id)

    first_name = user_info.first_name or "N/A"
    username = f"@{user_info.username}" if user_info.username else "No Username"
    is_restricted = "✅ Yes" if user_status.status in ["restricted"] else "❌ No"
    is_scam = "⚠️ Yes" if getattr(user_info, "is_scam", False) else "❌ No"
    is_premium = "🌟 Yes" if getattr(user_info, "is_premium", False) else "❌ No"

    info_text = (
        "🔍 <b>Your Info on 𝗠𝗲𝗻𝘁𝗼𝘀 ⚡</b>\n"
        "━━━━━━━━━━━━━━\n"
        f"👤 <b>First Name:</b> {first_name}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"📛 <b>Username:</b> {username}\n"
        f"🔗 <b>Profile Link:</b> <a href=\"tg://user?id={user_id}\">Profile Link</a>\n"
        f"🔒 <b>TG Restrictions:</b> {is_restricted}\n"
        f"🚨 <b>TG Scamtag:</b> {is_scam}\n"
        f"🌟 <b>TG Premium:</b> {is_premium}"
    )

    bot.reply_to(message, info_text, parse_mode="HTML")