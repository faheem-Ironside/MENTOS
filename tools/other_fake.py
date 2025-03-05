import httpx
from bs4 import BeautifulSoup
from telebot.types import Message
from faker import Faker

def handle_fake(bot, message: Message):
    try:
        # Get country code (default to "us")
        country_code = message.text.split(" ")[1].lower() if len(message.text.split(" ")) > 1 else "us"

        if country_code == "us":  # Generate fake address for the United States using Faker
            fake = Faker('en_US')  # US-specific locale

            fake_name = fake.name()
            fake_gender = fake.random_element(elements=('Male', 'Female'))
            fake_address = fake.street_address()
            fake_city = fake.city()
            fake_state = fake.state()
            fake_zipcode = fake.zipcode()
            fake_phone = fake.phone_number()
            fake_country = "United States"

            # Construct response message
            resp = f"""
<b>Fake Info Created Successfully ✅</b>
━━━━━━━━━━━━━━
🆔 <b>Full Name:</b> <code>{fake_name}</code>
👤 <b>Gender:</b> <code>{fake_gender}</code>
🏠 <b>Street:</b> <code>{fake_address}</code>
🏙️ <b>City/Town/Village:</b> <code>{fake_city}</code>
🌍 <b>State/Province/Region:</b> <code>{fake_state}</code>
📮 <b>Postal Code:</b> <code>{fake_zipcode}</code>
📞 <b>Phone Number:</b> <code>{fake_phone}</code>
🌏 <b>Country:</b> <code>{fake_country}</code>
━━━━━━━━━━━━━━
<b>Checked By:</b> <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>
"""

            bot.send_message(message.chat.id, resp, parse_mode="HTML")

        else:  # Fallback to FakeXY for other countries
            with httpx.Client() as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                url = f"https://www.fakexy.com/fake-address-generator-{country_code}"
                response = client.get(url, headers=headers)

                # DEBUG: Check if we get the correct HTML
                if response.status_code != 200:
                    bot.send_message(message.chat.id, "⚠️ Unable to fetch data from FakeXY. Try again later.")
                    return

                soup = BeautifulSoup(response.text, "html.parser")

                # Extract data using more flexible selection
                def get_detail(label):
                    cell = soup.find("td", string=lambda text: text and label.lower() in text.lower())
                    return cell.find_next_sibling("td").get_text(strip=True).title() if cell else "N/A"

                # Extract fake details
                fake_name = get_detail("Full Name")
                fake_gender = get_detail("Gender")
                fake_address = get_detail("Street")
                fake_city = get_detail("City/Town")
                fake_state = get_detail("State/Province/Region")
                fake_zipcode = get_detail("Zip/Postal Code")
                fake_phone = get_detail("Phone Number")
                fake_country = get_detail("Country")

                # Construct response message
                resp = f"""
    <b>Fake Info Created Successfully ✅</b>
    ━━━━━━━━━━━━━━
    🆔 <b>Full Name:</b> <code>{fake_name}</code>
    👤 <b>Gender:</b> <code>{fake_gender}</code>
    🏠 <b>Street:</b> <code>{fake_address}</code>
    🏙️ <b>City/Town/Village:</b> <code>{fake_city}</code>
    🌍 <b>State/Province/Region:</b> <code>{fake_state}</code>
    📮 <b>Postal Code:</b> <code>{fake_zipcode}</code>
    📞 <b>Phone Number:</b> <code>{fake_phone}</code>
    🌏 <b>Country:</b> <code>{fake_country}</code>
    ━━━━━━━━━━━━━━
    <b>Checked By:</b> <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>
    """

                bot.send_message(message.chat.id, resp, parse_mode="HTML")

    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Error occurred while generating fake info.")