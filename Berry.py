import requests
import json
import sys
from datetime import datetime
from time import sleep
import asyncio
import telegram
import cloudscraper

BOT_TOKEN = "5827311493:AAE-JDVE7CX5AXG-gvfO-zGI4H6MOwEWB4g"
bot = telegram.Bot(token=BOT_TOKEN)


def print_msg_time(message):
    print(f"|{datetime.now().strftime('%H:%M:%S')}| {message}")


target = "@Ron_Alert"
url = f'https://app.geckoterminal.com/api/p1/ronin/pools/0x363475ce45aef7ce55850d51872639464f993dd4/swaps'
scraper = cloudscraper.create_scraper()

# set up message counter dictionary
message_counts = {}


async def send_message():
    while True:
        try:
            response = scraper.get(url)
            if response.status_code != 200:
                print_msg_time(
                    f"Request failed with status code: {response.status_code}")
                sleep(10)
                continue

            trades = json.loads(response.content.decode('utf-8'))
            # print(trades["data"])
            # sys.exit()
            for trade in trades["data"]:
                trade_attributes = trade["attributes"]
                # print(trade["type"])
                # sys.exit()
                trade_type = trade["type"]

                if trade_type == "swap":
                    from_amount = float(
                        trade_attributes.get("from_token_amount", 0))
                    to_amount = float(
                        trade_attributes.get("to_token_amount", 0))

                    if from_amount < to_amount:
                        icon = "Buy 🟢"
                        price_info = f"🫐 Berry/USDC\n\nTX: {icon}\nPrice: {trade_attributes.get('price_to_in_usd')} USD\nspent: {to_amount} Berry\nVolume: {trade_attributes.get('to_token_total_in_usd')} USD\n\n[Address](https://app.roninchain.com/address/{trade_attributes.get('tx_from_address')}) || [TX](https://app.roninchain.com/tx/{trade_attributes.get('tx_hash')})\nTime : {trade_attributes.get('timestamp')}\n\nThis bot is still under development. If you have suggestions, you can send a message to @michiokun"

                    else:
                        icon = "Sell 🔴"
                        price_info = f"🫐 Berry/USDC\n\nTX: {icon}\nPrice: {trade_attributes.get('price_from_in_usd')} USD\nspent: {from_amount} Berry\nVolume: {trade_attributes.get('to_token_total_in_usd')} USD\n\n[Address](https://app.roninchain.com/address/{trade_attributes.get('tx_from_address')}) || [TX](https://app.roninchain.com/tx/{trade_attributes.get('tx_hash')})\nTime : {trade_attributes.get('timestamp')}\n\nThis bot is still under development. If you have suggestions, you can send a message to @michiokun"

                    # price_info = f"Berry/USDC\nTX: {icon}\nPrice: {trade_attributes.get('price_from_in_usd')} USD\nspent: {from_amount} Berry\nVolume: {trade_attributes.get('to_token_total_in_usd')} USD\n\n[Address](https://app.roninchain.com/address/{trade_attributes.get('tx_from_address')}) || [TX](https://app.roninchain.com/tx/{trade_attributes.get('tx_hash')})\nTime : {trade_attributes.get('timestamp')} This bot is still under development. If you have suggestions, you can send a message to @michiokun"

                    if price_info in message_counts:
                        message_counts[price_info] += 1
                        count = message_counts[price_info]

                        if count > 3:
                            print_msg_time(f"{price_info}\n")
                            continue
                    else:
                        message_counts[price_info] = 1
                        print_msg_time(f"{price_info}\n")
                        await bot.send_message(chat_id=target, text=price_info, disable_web_page_preview=True, parse_mode='Markdown')

                sleep(5)

        except Exception as e:
            print(e)

asyncio.run(send_message())