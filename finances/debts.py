import json
import consts as CONS
from google.gsheets import GSheets
from datetime import datetime
import configparser


DB = configparser.ConfigParser()
DB_NAME = CONS.DB_FILE_NAME

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
    
    @obs.setter #TODO flexibilizar
    def obs(self,pre_det):
        if isinstance(pre_det,str):
            self._obs += pre_det
        elif isinstance(pre_det,dict):
            det = []
            if 'subcategory' in pre_det:
                det.append('Cartão Físico' if pre_det['subcategory'] == "card_present" else 'Cartão Virtual')
            if 'tags' in pre_det:
                det.append('Tags:' + ','.join(pre_det['tags']))
            self._obs = ';'.join(det)

    @property
    def categoria(self):
        return self._categoria
    '''
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
            
        if a == 'TransferInEvent':
            self.valor = -self._valor
            
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

    def save_category(self,cat):
        range_ = f'Geral!M2:M35'
        GSheets().append([cat],range_)
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