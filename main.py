﻿from datetime import datetime
import logging
from bot.bot import Bot
import consts as CONS
import creds
import threading

#TODO informar pagamento fatura

bot = Bot()
logging.basicConfig(filename=f'execution_{creds.env}.log', level=logging.INFO)

print("Bot iniciado | CTRL A+D para minimizar instância.")

if creds.env == 'PROD':
    x = threading.Thread(target=bot.batch)
    x.start()
    print("[New thread started]")

while True:
    bot.get_updates()
