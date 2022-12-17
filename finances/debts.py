import json
import consts as CONS
from google.gsheets import GSheets
import finances.gsheets as GS
from datetime import datetime
from dateutil.relativedelta import relativedelta
import configparser
import re

DB = configparser.ConfigParser()
DB_NAME = CONS.DB_FILE_NAME

dictonary = {
    'Cartão Físico': ['card_present'],
    'Cartão Virtual': ['card_not_present'],
    '':['None']}

class Debts:

    def __init__(self,**kwargs):
        #TODO Analise do VALOR deeve sempre vir primeiro que a CATEGORIA
        
        self.nome = kwargs.get('nome')
        self.origem = kwargs.get('origem')
        self.valor = kwargs.get('valor')
        self.categoria = kwargs.get('categoria')
        self.data = kwargs.get('data')
        self._obs = ''
        self.obs = kwargs.get('obs')
        self.obs = kwargs.get('details')
        self.resp = kwargs.get('resp')
        self.ref = kwargs.get('ref')

    @property
    def origem(self):
        return self._origem
    
    @origem.setter #TODO flexibilizar
    def origem(self,a):
        if a not in CONS.ORIGEM:
            raise ValueError('origem value not known')
        self._origem = a
    
    @property
    def obs(self):
        return self._obs
    
    @obs.setter 
    def obs(self,pre_det):
        if isinstance(pre_det,str):
            pre_det = pre_det.replace('\n',' ')
            for x,i in dictonary.items():
                if pre_det in i:
                    self._obs += x

        elif isinstance(pre_det,dict):
            det = []
            if 'tags' in pre_det and pre_det['tags'] is not None:
                det.append('Tags:' + ','.join(pre_det['tags']))
            if 'footer' in pre_det and pre_det['footer'] is not None:
                det.append(str(pre_det['footer']).replace('\n',' '))
            if 'detail' in pre_det and pre_det['detail'] is not None:
                det.append(str(pre_det['detail']).replace('\n',' '))
            self._obs = ' | '.join(det)

    @property
    def categoria(self):
        return self._categoria
    ''' #TODO checagem agora é pelo KIND
    # Soma de todas as transações na NuConta
    # Observacão: As transações de saída não possuem o valor negativo, então deve-se olhar a propriedade "__typename".
    # TransferInEvent = Entrada
    # TransferOutEvent = Saída
    # TransferOutReversalEvent = Devolução
    '''
    @categoria.setter
    def categoria(self,a):
        categories = self.get_category()
        if a is None:
            a = 'nao categorizado'
        a = re.sub(r"[\n\t]*", "", a)           
        for key,cat in categories.items():
            if a in cat or a == key:
                a = key
                break
        if a not in categories.keys():
            self.save_category(a)
        self._categoria = a

    @property
    def valor(self):
        return self._valor
    
    @valor.setter
    def valor(self,a):
        try:
            self._valor = float(a)
        except ValueError:
            self._valor = 0
        except TypeError:
            self._valor = 0

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self,data):
        try:
            self._data = data
            if not isinstance(data,datetime):
                self._data = datetime.strptime(data,"%Y-%m-%d")
        except ValueError:
                self._data = datetime.strptime(data,"%d/%m/%Y")
        except TypeError:
                self._data = datetime.now()
    
    @property
    def ref(self):
        return self._ref

    @ref.setter
    def ref(self,data):
        '''
        Aceita 3 tipos de referência:
        int: Número do Mês
        str: Referência já formatada
        datetime: pega o mês da data informada.
        '''

        if isinstance(data,datetime):
            self._ref = CONS.MONTHS[datetime.strptime(data,"%m")]
        elif isinstance(data,int):
            if data > 12:
                data -= 12
            self._ref = CONS.MONTHS[data]
        else:
            self._ref =  data

    def save_category(self,cat):
        GSheets().append([cat],GS.Categories.table)
        cats = self.get_category()
        cats.update({cat:[]})
        DB.read(DB_NAME)
        cnfFile = open(DB_NAME, "w")
        DB.set("NUBANK","categories",json.dumps(cats))
        DB.write(cnfFile)
        cnfFile.close() 
    
    @staticmethod
    def get_category():
        DB.read(DB_NAME,encoding='utf-8')
        return json.loads(DB.get("NUBANK","categories"))


    def to_list(self):
        return [self.nome,
        self.origem,
        self.valor,
        self.categoria,
        self.data.strftime("%d/%m/%Y"),
        self.ref,
        self.obs,
        self.resp]

    @staticmethod
    def nubank_debts(jsn,ref_date):
        d_list = []

        #Compra parcelada
        count = 1
        amount = -int(jsn['amount'])/100
        if 'charges' in jsn['details']:
            count = jsn['details']['charges']['count']
            amount = -int(jsn['details']['charges']['amount'])/100
        for x in range(0,count):
            insert_date = datetime.strptime(jsn['time'],"%Y-%m-%dT%H:%M:%SZ")
            insert_date = insert_date + relativedelta(months=x)
            d_list.append(Debts(
                nome=jsn['description'],
                origem="Nubank",
                valor=amount,
                categoria=jsn['title'],
                data = insert_date,
                ref = ref_date+x,
                details=jsn['details']['subcategory'],
                resp='').to_list())
        return d_list
    
    @staticmethod
    def nuconta_debts(jsn,ref_date):
        d_list = []
        amount = -float(jsn['amount'])
        if jsn['kind'] == 'POSITIVE' or jsn['title'] == 'Resgate fundo':
            amount = float(jsn['amount'])

        d_list.append(Debts(
            nome=jsn['title'],
            origem="Nuconta",
            valor=amount,
            categoria='movimentação', #TODO implementar categoria
            data=datetime.strptime(jsn['postDate'],"%Y-%m-%d"),
            ref=ref_date,
            details=jsn).to_list())

        #Identificar Pagamento da Fatura e gerar registro NuBank
        if jsn['title'] == "Pagamento da fatura":
            d_list.append(Debts(
            nome=jsn['title'],
            origem="Nubank",
            valor=float(jsn['amount']),
            categoria='pagamento', 
            data=datetime.strptime(jsn['postDate'],"%Y-%m-%d"),
            ref=ref_date,
            details='').to_list())
        return d_list