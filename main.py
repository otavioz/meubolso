from datetime import datetime
import logging
from bot.bot import Bot
import consts as CONS
import creds
import threading

bot = Bot()
logging.basicConfig(filename=f'execution_{creds.env}.log', level=logging.INFO)

print("Bot iniciado | CTRL A+D para minimizar instância.")

if creds.env == 'PROD':
    x = threading.Thread(target=bot.batch)
    x.start()
    print("[New thread started]")

while True:
    #try:
    bot.get_updates()
    #except Exception as e:
    #    logging.error(f'{datetime.now()} - Erro no processamento. {e}')
