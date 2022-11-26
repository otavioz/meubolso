import consts as CONS
import creds
from bot.chat import Chat,Message
import orchestrator.orchestrator as Orch
from googleapiclient import errors
import requests
import json
from datetime import timedelta, datetime
import time as ttime
import logging
import traceback

#TODO Subir para GIT PRIVADO
#TODO criptografia credenciais nubank
#TODO checkin automático Oracle

# https://api.telegram.org/bot1118783038:AAE8OQ4KX63PoURwi360wZRj32d0mcgBbOI/getUpdates

class Bot:

    def __init__(self):
        self.token = creds.bot_token
        self.base = "https://api.telegram.org/bot{}/".format(self.token)
        self.update_id = None
        self.chats = {} # {chat_id: Chat()}
        self.start_hour = "05"

    def batch(self):
        while True:
            try:
                now = datetime.now()
                if now.strftime("%H") == self.start_hour and now.strftime("%M") == "50":  #Atualizar Planilha
                    ttime.sleep(59)
                    logging.info(f'{datetime.now()} - Iniciando processamento batch.')
                    Orch.automatic_functions()
                    logging.info(f'{datetime.now()} - Finalizado processamento batch.')
            except errors.HttpError as e:
                logging.error(f'{datetime.now()} - Chamada API Google {e}')
            except UnicodeDecodeError as e:
                logging.error(f'{datetime.now()} - Erro na leitura de arquivo csv: {e}')
            except Exception as e:
                logging.error(f'{datetime.now()} - Erro no processamento batch: {traceback.format_exc()}')

    def get_updates(self):
        #TODO checar se timeout esta funcionando
        url = self.base + "getUpdates?timeout=100"
        if self.update_id:
            url = url + "&offset={}".format(self.update_id + 1)
        resp = json.loads(requests.get(url).content.decode('utf-8'))
        if not resp["ok"]:
            logging.error(f'{datetime.now()} - Erro chamar getUpdates: {resp}')
        else:
            for result in resp["result"]:
                message = Message()
                message.set_message(result)
                self.update_id = message.update_id
                ch_id = message.chat_id
                #Checa se é um NOVO chat
                if ch_id not in self.chats.keys():
                    self.chats.update({ch_id:Chat(ch_id,message.language_code)})

                #Salva mensagem
                self.chats[ch_id].message = message

                #Valida se última mensagem foi com reply_markup para deletá-lo
                if message.reply_markup is not None:
                    self.__remove_keyboard(message)

                #Envia mensagens de reposta
                for r in Orch.get_reply(message):
                    resp = self.chats[ch_id].reply(message,r)
                    self.send_message(resp,ch_id)

                #Valida cache do histórico #TODO Validar reply guloso
                if self.chats[ch_id].len > 30:
                    self.chats[ch_id].clear()

    def send_message(self, message,chat_id):
        self.__send_action("typing",chat_id)
        params = {
            "chat_id": chat_id,
            "text": message.text,
            "parse_mode": "html"
        }

        if message.reply_markup is not None:
            params.update({"reply_markup": json.dumps(message.reply_markup)})

        if message.image_file is not None:
            r = requests.get(f'{self.base}sendPhoto?chat_id={chat_id}&photo={message.image_file}')
            self.__verificar_erro(chat_id, r, "Ocorreu um erro a enviar uma imagem.")

        if message.text is not None:
            r = requests.get(f'{self.base}sendMessage', params=params)
            self.__verificar_erro(chat_id, r)


    def __remove_keyboard(self,input):
        r = requests.get(f'{self.base}editMessageReplyMarkup?chat_id={input.chat_id}&message_id={input._id}&reply_markup={json.dumps({"inline_keyboard": [[]]})}')
        if self.__verificar_erro(input.chat_id, r):
            requests.get(f'{self.base}sendMessage?chat_id={input.chat_id}&text=✔️ {input.callback_data}')

    def __send_action(self, action,chat_id):
        url = f'{self.base}sendChatAction?chat_id={chat_id}&action={action}'
        if action is not None:
            requests.get(url)

    def __verificar_erro(self, chat_id, res, message=None):
        r = json.loads(res.content.decode('utf-8'))
        if not r["ok"]:
            url = f'{self.base}sendMessage?chat_id={chat_id}&parse_mode=html&text=<b>[{r["error_code"]}]</b> {message if message else "Um erro aconteceu!! 😵😵"}'
            print(f'{datetime.now()} [{r["error_code"]}] {r["description"]}')
            logging.error(f'{datetime.now()} - Erro na chamada da API Telegram: {r}')
            requests.get(url)
            return False
        return True
