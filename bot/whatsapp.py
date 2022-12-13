from datetime import datetime
import json
import logging

import requests
import creds

class WhatsApp():
    access_token = None
    access_token_expires = datetime.now()
    access_token_did_expire = True
    base_url = "https://graph.facebook.com" #{}/{}/messages"

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bearer_token = creds.wp_bearer
        self.next_token = {}
        self.ver = 'v15.0'
        self.phone = '113533338265661'

    def __get_token_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bearer_token}"
        }
    
    def __get_resource(self, url,query_params):
        headers = self.__get_token_headers()
        r = requests.get(url, headers=headers,params=query_params)
        if r.status_code not in range(200, 299):
            print(f'Endpoint Response Code:{str(r.status_code)} {r.text}\n\nHeaders: {headers}\n\nQuery: {query_params}')
            logging.error(f'{datetime.now()} -GET WhatsApp API: {str(r.status_code)} {r.text}')
            return {}
        return r.json()
    
    def __post_resource(self, url,body):
        headers = self.__get_token_headers()
        r = requests.post(url, headers=headers,json=body)
        if r.status_code not in range(200, 299):
            print(f'Endpoint Response Code:{str(r.status_code)} {r.text}\n\nHeaders: {headers}\n\Body: {body}')
            logging.error(f'{datetime.now()} - POST WhatsApp API: {str(r.status_code)} {r.text}')
            return {}
        return r.json()
    
    def send_message(self,message,template=False):
        url = f'{self.base_url}/{self.ver}/{self.phone}/messages'
        params = {
            "messaging_product": "whatsapp",
            "to": "5531998070614",
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }

        resp = self.__post_resource(url,params)
        if resp == {}:
            return []
        return resp
