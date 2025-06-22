import sys, glob, importlib, logging, logging.config, pytz, asyncio
import threading, time, requests
from pathlib import Path
from pyrogram import Client, idle
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from Script import script 
from datetime import date, datetime 
from aiohttp import web
from plugins import web_server

from SMDBOTz.bot import SMDBOTzBot
from SMDBOTz.util.keepalive import ping_server
from SMDBOTz.bot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)
SMDBOTzBot.start()
loop = asyncio.get_event_loop()

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)

def ping_loop():
    while True:
        try:
            r = requests.get(URL, timeout=10)
            if r.status_code == 200:
                print("🍁 ᴘɪɴɢ sᴜᴄᴄᴇssғᴜʟ")
            else:
                print(f"👹 ᴘɪɴɢ ғᴀɪʟᴇᴅ: {r.status_code}")
        except Exception as e:
            print(f"❌ ᴇxᴄᴇᴘᴛɪᴏɴ ᴅᴜʀɪɴɢ ᴘɪɴɢ: {e}")
        time.sleep(120)
threading.Thread(target=ping_loop, daemon=True).start()

async def start():
    print('\n')
    print('Initalizing Your SMD_BOTz')
    bot_info = await SMDBOTzBot.get_me()
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("SMD_BOTz Imported => " + plugin_name)
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    me = await SMDBOTzBot.get_me()
    temp.BOT = SMDBOTzBot
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    logging.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    try:
        await SMDBOTzBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    except:
        print("Make Your Bot Admin In Log Channel With Full Rights")
    for ch in CHANNELS:
        try:
            k = await SMDBOTzBot.send_message(chat_id=ch, text="**Bot Restarted**")
            await k.delete()
        except:
            print("Make Your Bot Admin In File Channels With Full Rights")
    try:
        k = await SMDBOTzBot.send_message(chat_id=AUTH_CHANNEL, text="**Bot Restarted**")
        await k.delete()
    except:
        print("Make Your Bot Admin In Force Subscribe Channel With Full Rights")
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    await idle()


if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
