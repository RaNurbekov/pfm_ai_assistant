from dotenv import load_dotenv
import os
import asyncio
from telegram import Bot

load_dotenv()

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

print(f"Token: {token[:20]}...")
print(f"Chat ID: {chat_id}")
print(f"Chat ID type: {type(chat_id)}")

async def test():
    bot = Bot(token=token)
    # Convert to integer
    await bot.send_message(
        chat_id=int(chat_id),
        text='Hello from PFM Bot!'
    )
    print('SUCCESS!')

asyncio.run(test())