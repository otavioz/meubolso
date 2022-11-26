#import views.games as Games
from orchestrator.finances import FO
from pynubank import exception
from googleapiclient import errors
from datetime import datetime
import logging
import traceback

#import models.message as Message

fo = FO()

def automatic_functions():
    fo.insert_last_bills()

def get_reply(input):
    try:
        message = input.text
        ret = None
        if "/cancel" in message:
            ret = "Como desejar. 🌪️🌪️"
        elif message.startswith("/g"):
            ret = None
        elif message.startswith("/f"):
            ret = fo.finances(message.split(";"))
        else:
            ret = "Não entendi o que você procura."
        
        #Tratar Retorno
        if isinstance(ret,str):
            return [{'message':ret}]
        elif isinstance(ret,list):
            return ret
        elif isinstance(ret,dict):
            return [ret]
        elif ret == None:
            return [{'message':"🤚🏼👷🏽‍♂️🚧 Funcionalidade não implementada🚧"}]
            
    except errors.HttpError as e: #TODO melhorar
        logging.error(f'{datetime.now()} - Falha no processamento de resposta: {traceback.format_exc()}')
        return [{'message':"Google API está indisponível."}]
    except exception.NuRequestException as e:
        logging.error(f'{datetime.now()} - Falha no processamento de resposta: {traceback.format_exc()}')
        return [{'message':"Nubank API está indisponível."}]    
    except ValueError as e:
        logging.error(f'{datetime.now()} - Falha no processamento de resposta: {traceback.format_exc()}')
        return [{'message':"Falha na formatação de valores. Consulte o LOG."}]
    except Exception as e:
        logging.error(f'{datetime.now()} - Falha no processamento de resposta: {traceback.format_exc()}')
        return [{'message':"Falha na formatação da reposta. Consulte o LOG."}]
    
        