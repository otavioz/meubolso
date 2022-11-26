
from datetime import datetime

class Chat():

    def __init__(self,chat_id,language_code):
        self.update_id = None
        self.chat_id = chat_id
        self._message = None
        self.language_code = language_code
        self._history = []       #Histórico de Mensagens

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self,a):
        if self._message is not None:
            self._history.insert(0,a)
        self._message = a
    
    @property
    def len(self):
        return len(self._history)


    def new_message(self,text,to_,from_,update_id=None,chat_id=None,type_="In",category="General"):
        self.update_id = update_id if update_id is not None else self.update_id
        date = datetime.now()
        language_code = self.language_code
        return Message(text,to_,from_,update_id,type_,category,date,language_code)

        #return Message(text=text,
        #            to_=to_,
        #            id_=id_,
        #            from_=from_,
        #            update_id=self.update_id,
        #            date=date,
        #            language_code=language_code,
        #            reply_markup=reply_markup,
        #            callback_data=callback_data)

    def reply(self,input,output):
        m = Message()
        m.from_ = input.to_
        m.to_ = input.from_
        m.date = datetime.now()
        m.language_code = self.language_code
        m.reply = input if 'reply' in output else None
        if "message" in output:
            m.text = output['message']
        if "channel_post" in output:
            m.text = output['channel_post']
        if "reply_markup" in output:
            m.reply_markup = output['reply_markup']
        if "poll_answer" in output:
            pass
        self.message = m
        return m

    def clear(self):
        self.history = self.history[10:]

class Message():

    def __init__(self,**kwargs):
        self._id = kwargs.get('_id')
        self.message_id = kwargs.get('message_id')
        self.text = kwargs.get('text')
        self.chat_id = kwargs.get('chat_id')
        self.to_ = kwargs.get('to_')
        self.from_ = kwargs.get('from_')
        self.update_id = kwargs.get('update_id')
        self.type_ = kwargs.get('type_')
        self.category = kwargs.get('category')
        self.reply = kwargs.get('reply')
        self.date = kwargs.get('date')
        self.language_code = kwargs.get('language_code')
        self.reply_markup= kwargs.get('reply_markup')
        self.image_file= kwargs.get('image_file')
        self.concatenate= kwargs.get('concatenate')
        self.reply_markup = kwargs.get('reply_markup') 
        self.callback_data = kwargs.get('callback_data')
    
    def set_message(self,message):
        self.update_id = message['update_id']
        self.to_ = 'bot'
        if "message" in message:
            self._id = message['message']['message_id']
            self.chat_id = message['message']['chat']['id']
            self.from_ = message['message']['from']['id']
            self.date = message['message']['date']
            self.language_code = message['message']['from']['language_code']
            self.text = message['message']['text']
        elif "edited_message" in message:
            self._id = message['edited_message']['message_id']
            self.chat_id = message['edited_message']['chat']['id']
            self.from_ = message['edited_message']['from']['id']
            self.date = message['edited_message']['message']['date']
            self.language_code = message['edited_message']['from']['language_code']
            self.text = message['edited_message']['text']
        elif "channel_post" in message:
            self._id = message['channel_post']['message_id']
            self.chat_id = message['channel_post']['message']['chat']['id']
            self.from_ = message['channel_post']['from']['id']
            self.date = message['channel_post']['message']['date']
            self.language_code = message['channel_post']['from']['language_code']
            self.text = message['channel_post']['text']
        elif "edited_channel_post" in message:
            self._id = message['edited_channel_post']['message_id']
            self.chat_id = message['message']['chat']['id']
            self.from_ = message['edited_channel_post']['from']['id']
            self.date = message['edited_channel_post']['message']['date']
            self.language_code = message['edited_channel_post']['from']['language_code']
            self.text = message['edited_channel_post']['text']
        elif "callback_query" in message:
            self._id = message['callback_query']['message']['message_id']
            self.chat_id = message['callback_query']['message']['chat']['id']
            self.from_ = message['callback_query']['message']['from']['id']
            self.date = message['callback_query']['message']['date']
            self.language_code = message['callback_query']['from']['language_code']
            self.reply_markup =  message['callback_query']['message']['reply_markup']['inline_keyboard']
            self.text = message['callback_query']['data']
            for i in self.reply_markup:
                if i[0]['callback_data'] == self.text:
                    self.callback_data = i[0]['text']
                    break
        elif "poll_answer" in message:
            pass
        else:
            raise ValueError(f'Mensagem não identificada {message}')


    def __str__(self) -> str:
        return f'_id : {self._id}\ntext: {self.text}\nto_ : {self.to_ }\nfrom_: {self.from_}\nupdate_id: {self.update_id}\ntype_: {self.type_}\ncategory: {self.category}\nreply: {self.reply}\ndate: {self.date}\nlanguage_code: {self.language_code}\nreply_markup: {self.reply_markup}\nimage_file: {self.image_file}\nconcatenate: {self.concatenate}\ncallback_data: {self.callback_data}'
