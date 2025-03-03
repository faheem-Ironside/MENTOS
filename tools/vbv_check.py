import os
import re
import time
import csv

VBV_BIN_FILE = "tools/vbvbin.txt"
BINS_CSV_FILE = "bins_all.csv"

# Load VBV BIN data
def load_vbv_bins():
    vbv_data = {}
    if os.path.exists(VBV_BIN_FILE):
        with open(VBV_BIN_FILE, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split("|")
                if len(parts) >= 3:
                    vbv_data[parts[0]] = (parts[1], parts[2])  # BIN → (VBV Status, Response)
    return vbv_data

# Load BIN details from bins_all.csv
def load_bin_details():
    bin_data = {}
    if os.path.exists(BINS_CSV_FILE):
        with open(BINS_CSV_FILE, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 7:
                    bin_data[row[0]] = {
                        "country": row[1],
                        "flag": row[2],
                        "vendor": row[3],
                        "type": row[4],
                        "level": row[5],
                        "bank": row[6]
                    }
    return bin_data

VBV_BINS = load_vbv_bins()
BIN_DETAILS = load_bin_details()

def check_vbv(bin_number):
    return VBV_BINS.get(bin_number, ("Unknown ❓", "No VBV data available"))

def get_bin_info(bin_number):
    return BIN_DETAILS.get(bin_number, {
        "country": "Unknown",
        "flag": "🌍",
        "vendor": "Unknown",
        "type": "Unknown",
        "level": "Unknown",
        "bank": "Unknown"
    })

def handle_vbv(bot, message):
    start_time = time.time()
    message_text = message.text.strip()

    # If the message is a reply, extract text from replied message
    if message.reply_to_message and message.reply_to_message.text:
        message_text = message.reply_to_message.text.strip()

    # Extract card details
    match = re.search(r"(\d{6,16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})", message_text)
    if not match:
        bot.reply_to(message, "❌ *Invalid format!*\nUse `/vbv cardnumber|mm|yy|cvc`", parse_mode="Markdown")
        return

    card_number, card_month, card_year, card_cvc = match.groups()
    bin_number = card_number[:6]

    # Check VBV status
    vbv_status, vbv_response = check_vbv(bin_number)

    # Get BIN details
    bin_info = get_bin_info(bin_number)
    vendor = bin_info["vendor"].upper()
    card_type = bin_info["type"].upper()
    card_level = bin_info["level"].upper()
    bank_name = bin_info["bank"]
    country_name = bin_info["country"]
    country_emoji = bin_info["flag"]

    end_time = time.time()
    processing_time = round(end_time - start_time, 2)

    bot.reply_to(message, f"""
<b>{'Passed ✅' if 'FALSE' in vbv_status else 'Failed ❌'}</b>

𝗖𝗮𝗿𝗱 ⇾ <code>{card_number}|{card_month}|{card_year}|{card_cvc}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ 3DS Lookup
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ⇾ {vbv_response}

𝗜𝗻𝗳𝗼 ⇾ {vendor} - {card_type} - {card_level}
𝐈𝐬𝐬𝐮𝐞𝐫 ⇾ {bank_name}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ⇾ {country_name} {country_emoji}

𝗧𝗶𝗺𝗲 ⇾ {processing_time} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀
""", parse_mode="HTML")