from datetime import datetime
import logging
import time
from bot.bot import Bot
import consts as CONS
import creds
import threading
from requests import exceptions
#TODO informar pagamento fatura

bot = Bot()
logging.basicConfig(filename=f'execution_{creds.env}.log', level=logging.INFO)

print("CTRL A+D para minimizar instância.")

if creds.env == 'PROD':
    x = threading.Thread(target=bot.batch)
    x.start()
    print("[batch thread started]")

print("[telegram bot running]")
while True:
    try:
        bot.get_updates()
    except exceptions.ConnectionError as e:
        logging.error(f'{datetime.now()} - Erro telegram.getUpdates: {e}')
        time.sleep(60) #sleep 1min

