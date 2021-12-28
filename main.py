from aiogram import Bot, Dispatcher, dispatcher, executor, types
import logging
import asyncio
import websockets
import json
import os

GOTIFY_URL = os.environ.get('GOTIFY_URL')
GOTIFY_PORT = os.environ.get('GOTIFY_PORT')
APP_TOKEN = os.environ.get('GOTIFY_APP_TOKEN')
CLIENT_TOKEN = os.environ.get('GOTIFY_CLIENT_TOKEN')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

logging.basicConfig(level=logging.INFO)

telegram_bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(telegram_bot)


# Gotify Web Socket Methods

async def message_handler(websocket) -> None:
    async for message in websocket:
        logging.info(f"Message: {message}")
        message = json.loads(message)
        logging.info('Sending message: {} '.format(message))
        await telegram_bot.send_message(CHAT_ID, "{}: {}".format(message['title'], message['message']))

async def websocket_gotify(hostname: str, port: int, token: str) -> None:
    logging.info('Starting gotify websocket...')
    websocket_resource_url = f"wss://{hostname}:{port}/stream?token={token}"
    async with websockets.connect(websocket_resource_url) as websocket:
        await message_handler(websocket)


# Telegram Bot Methods

@dispatcher.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """ Send a message when the command /start or /help is issued. """
    logging.info('Welcome message to: @{} [{}]'.format(message.chat.username,message.chat.id))
    await message.reply('Hi! \n Gotify Bot')

@dispatcher.message_handler()
async def echo(message: types.Message):
    """ Echo the user message. """
    await message.reply(message.text)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(websocket_gotify(hostname=GOTIFY_URL,
                                      port=GOTIFY_PORT, 
                                      token=CLIENT_TOKEN))
    loop.create_task(executor.start_polling(dispatcher, skip_updates=True))
    loop.run_forever()
