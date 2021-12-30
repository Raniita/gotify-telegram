from aiogram import Bot, Dispatcher, dispatcher, executor, types, md
from aiogram.utils.emoji import emojize
import logging
import asyncio
import websockets
import requests
import json
import os

GOTIFY_URL = os.environ.get('GOTIFY_URL')
GOTIFY_PORT = os.environ.get('GOTIFY_PORT')
APP_TOKEN = os.environ.get('GOTIFY_APP_TOKEN')
CLIENT_TOKEN = os.environ.get('GOTIFY_CLIENT_TOKEN')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

logging.basicConfig(level=logging.INFO)

telegram_bot = Bot(token=TELEGRAM_TOKEN, parse_mode=types.ParseMode.MARKDOWN_V2)
dispatcher = Dispatcher(telegram_bot)


# Gotify Web Socket Methods

async def message_handler(websocket) -> None:
    async for message in websocket:
        logging.info(f"Message: {message}")
        message = json.loads(message)
        logging.info('Sending message: {} '.format(message))
        await telegram_bot.send_message(CHAT_ID, "{}: {}".format(message['title'], message['message']))

async def websocket_gotify(hostname: str, port: int, token: str) -> None:
    logging.info('Starting Gotify Websocket...')
    websocket_resource_url = f"wss://{hostname}:{port}/stream?token={token}"
    async with websockets.connect(websocket_resource_url) as websocket:
        logging.info("Connected to Gotify Websocket: {}:{}".format(GOTIFY_URL, GOTIFY_PORT))
        await message_handler(websocket)


# Telegram Bot Methods

@dispatcher.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """ Send a message when the command /start or /help is issued. """
    logging.info('Welcome message to: @{}<{}>'.format(message.chat.username,message.chat.id))
    await message.reply("Hi! \nI'm Gotify Bot")


@dispatcher.message_handler(commands=['send'])
async def send_notification(message: types.Message):
    """ Send Notification to Gotify Server """
    
    await types.ChatActions.typing()

    # Check if APP_TOKEN is defined
    if APP_TOKEN != None:
        url = "{}:{}/message?token={}".format(GOTIFY_URL, GOTIFY_PORT, APP_TOKEN)

        resp = requests.post(url, json={
            "message": 'Test message',
            "priority": 10,
            "title": 'test title'
        })

        logging.info('Gotify Notification Sent!. Response: {}'.format(resp))

        await telegram_bot.send_message(message.chat.id, 'Gotify Sent!')
    else:
        logging.error('Gotify APP_TOKEN not defined')
        
        content = []
        content.append(md.text(md.code('GOTIFY_APP_TOKEN'), ' not defined'))

        await telegram_bot.send_message(message.chat.id, content)


@dispatcher.message_handler(commands=['about'])
async def send_about(message: types.Message):
    """ Send info about the bot """
    await types.ChatActions.typing()    # Send typing... to user
    
    content = []
    logging.info('Sending about to: @{}<{}>'.format(message.chat.username, message.chat.id))
    content.append([md.text('Gotify Client for Telegram. Connected to:', GOTIFY_URL, md.text(':check_mark:'))])

    

    await telegram_bot.send_message(message.chat.id, emojize(md.text(*content, sep='\n')), parse_mode=types.ParseMode.MARKDOWN_V2)


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
