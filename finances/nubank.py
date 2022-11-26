from datetime import timedelta, datetime
from pynubank import Nubank as Nu, MockHttpClient
import consts as CONS
import creds

class Nubank:

    def __init__(self):
        if creds.env == 'DEV':
            self.nu = Nu(MockHttpClient()) #Ambiente de TESTE
            self.prod = False
        else:
            self.nu = Nu()                #Ambiente de Produção
            self.prod = True
        self.nu.authenticate_with_cert(creds.nu_log, creds.nu_pas, 'keys/cert.p12')

    def get_bills(self):
        return self.nu.get_card_statements()
    
    def get_transactions(self):
        return self.nu.get_account_statements()
    
    def get_bill_details(self,debt):
        return self.nu.get_card_statement_details(debt)
