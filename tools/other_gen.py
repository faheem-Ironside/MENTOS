import random
import time
import requests

# Luhn Algorithm to validate card numbers
async def checkLuhn(cardNo):
    nDigits = len(cardNo)
    nSum = 0
    isSecond = False
    for i in range(nDigits - 1, -1, -1):
        d = ord(cardNo[i]) - ord("0")
        if isSecond:
            d = d * 2
        nSum += d // 10
        nSum += d % 10
        isSecond = not isSecond
    return nSum % 10 == 0

# Generate a valid CC number
async def cc_generator(cc, mes, ano, cvv):
    if mes == "None" or 'x' in mes.lower():
        mes = f"{random.randint(1, 12):02d}"  # Random month (01-12)

    if ano == "None" or 'x' in ano.lower():
        ano = str(random.randint(2024, 2035))  # Random year (2024-2035)

    if cvv == "None" or 'x' in cvv.lower():
        cvv = str(random.randint(100, 999))  # Random CVV

    # Generate the remaining numbers
    random_digits = ''.join(random.choices("0123456789", k=10))
    cc_number = cc[:6] + random_digits

    # Ensure Luhn compliance
    while not await checkLuhn(cc_number):
        random_digits = ''.join(random.choices("0123456789", k=10))
        cc_number = cc[:6] + random_digits

    return f"`{cc_number}|{mes}|{ano}|{cvv}`"  # Each card is mono-block formatted

# Generate multiple valid cards
async def generate_cards(cc, mes, ano, cvv, amount=10):
    cards = [await cc_generator(cc, mes, ano, cvv) for _ in range(amount)]
    return "\n".join(cards)

# Handle /gen command
async def handle_gen(bot, message):
    start_time = time.perf_counter()
    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(message, "❌ Incorrect format! Use `/gen 519535xxxxxxxxxx|MM|YYYY|CVV`", parse_mode="Markdown")
        return

    input_data = args[1]
    parts = input_data.split("|")

    bin_prefix = parts[0][:6]  # First 6 digits of BIN
    mes = parts[1] if len(parts) > 1 else "None"
    ano = parts[2] if len(parts) > 2 else "None"
    cvv = parts[3] if len(parts) > 3 else "None"

    # BIN Lookup
    try:
        response = requests.get(f"https://bins.antipublic.cc/bins/{bin_prefix}").json()
        brand = response.get("brand", "UNKNOWN")
        bank = response.get("bank", "UNKNOWN")
        country = response.get("country_name", "UNKNOWN")
        flag = response.get("country_flag", "🏳")
    except:
        brand, bank, country, flag = "UNKNOWN", "UNKNOWN", "UNKNOWN", "🏳"

    # Generate 10 cards
    generated_cards = await generate_cards(bin_prefix, mes, ano, cvv, 10)

    execution_time = time.perf_counter() - start_time
    checked_link = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"

    response = (
        f"💳 **𝐂𝐂 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲**\n"
        f"🔹 **𝐁𝐢𝐧** - `{bin_prefix}`\n"
        f"🔹 **𝐀𝐦𝐨𝐮𝐧𝐭** - 10\n\n"
        f"{generated_cards}\n\n"  # Cards listed in mono format one by one
        f"ℹ️ **𝗜𝗻𝗳𝗼** - {brand}\n"
        f"🏛 **𝐁𝐚𝐧𝐤** - {bank}\n"
        f"🌍 **𝐂𝐨𝐮𝐧𝐭𝐫𝐲** - {country} {flag}\n\n"
        f"⏳ **𝐓𝐢𝐦𝐞** - {execution_time:.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬\n"
        f"✅ **𝐂𝐡𝐞𝐜𝐤𝐞𝐝** - {checked_link}"
    )

    bot.reply_to(message, response, parse_mode="Markdown")  # ✅ Replies in the user's command