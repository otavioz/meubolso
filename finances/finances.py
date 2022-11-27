from datetime import datetime
from google.gsheets import GSheets
import consts as CONS
from finances.nubank import Nubank
from finances.debts import Debts
import finances.gsheets as GS
import configparser

class Finances:

    def __init__(self) -> None:
        self.gsheets = GSheets()
        self.nu = Nubank()
        self.db = configparser.ConfigParser()
        self.db_name = CONS.DB_FILE_NAME
        
        self.sheet_data={
            'nucard':'E4',
            'mb':'E5',
            'others':'E6',
            'nuacc':'E7',
            'debts':'E8',
            'stotal':'E11',
            'total':'E12'
        }


    def debt(self,**kwargs):
        return Debts(**kwargs)

    def get_actual_month(self):
        today = datetime.now()
        if today.day < self.get_close_day():
            return today.month
        return today.month + 1

    def last_close_date(self):
        cs = self.get_close_day()
        today = datetime.now()
        m = today.month
        if today.day < cs:
            m =  today.month - 1
        return today.replace(day=cs).replace(month=m)

    def list_origem(self):
        list_o = {}
        for o in CONS.ORIGEM:
            list_o.update({o:0})
        return list_o
    
    def list_cat(self):
        list_c = {}
        for o in Debts.get_category():
            list_c.update({o:0})
        return list_c
        
    def save_debt(self,debts,list_=False):
        self.gsheets.append(debts,GS.Debts.table,list_=list_)
    
    def read_debts(self,month=None):
        month = CONS.MONTHS[self.get_actual_month()] if month==None else CONS.MONTHS[month]
        model = GS.Debts
        d_list = []
        for d in self.gsheets.get(model.table,majorDimension='ROWS')['values']:
            if d[model.ref] ==  month:
                d_list.append(Debts(
                        nome=d[model.name],
                        origem=d[model.origin],
                        valor=d[model.value],
                        categoria=d[model.category],
                        data=d[model.date],
                        ref=d[model.ref],
                        obs=d[model.obs] if len(d)>6 else '',
                        resp=d[model.resp] if len(d)>7 else ''))
        return d_list

    def get_all(self):
        pass

    def summary(self,type=None):
        pass

    def monthly_limit(self,origin='Nubank'):
        model = GS.Limits
        for l in self.gsheets.get(model.table,majorDimension='ROWS')['values']:
            if l[model.name] == origin:
                return float(l[model.max_value])
        return 0

    def get_card_statements(self,date=None):
        close_day = self.__get_last_cs() if date == None else date
        bills_list = []
        cd = self.get_close_day()
        #TODO checar de adicionar já em lista para insert
        for t in self.nu.get_bills():
            date = datetime.strptime(t['time'],"%Y-%m-%dT%H:%M:%SZ")
            if date.date() >= close_day.date():
                    ref = date.month if date.day < cd else date.month + 1
                    ref = CONS.MONTHS[ref]
                    bills_list.append(Debts(
                    nome=t['description'],
                    origem="Nubank",
                    valor=-float(t['amount'])/100,
                    categoria=t['title'],
                    data=date,
                    ref = ref,
                    details=t['details']).to_list())
        self.__save_last_date('last_card_statements',datetime.now())
        return bills_list

    def get_bank_statement(self,date=None):
        close_day = self.__get_last_bs() if date == None else date
        bs_list = []
        date = close_day
        cd = self.get_close_day()
        transactions = self.nu.get_transactions()
        page_info = transactions['pageInfo'] #TODO implementar auto paginação
        for t in transactions['edges']:
            t = t['node']
            date = datetime.strptime(t['postDate'],"%Y-%m-%d")
            if date.date() >= close_day.date():
                    ref = date.month if date.day < cd else date.month + 1
                    ref = CONS.MONTHS[ref]
                    bs_list.append(Debts(
                    nome=t['title'],
                    origem="Nuconta",
                    valor=float(t['amount']) if t['kind'] == 'POSITIVE' else -float(t['amount']),
                    categoria='movimentação', #TODO implementar categoria
                    data=date,
                    ref = ref,
                    details=f'{t["footer"]} - {t["detail"]}').to_list())
        self.__save_last_date('last_bank_statement',datetime.now())
        return bs_list

    def get_close_day(self):
        self.db.read(self.db_name)
        return int(self.db.get('NUBANK',"close_day"))

    def __get_last_bs(self):
        self.db.read(self.db_name)
        date = self.db.get("NUBANK","last_bank_statement")
        return datetime.strptime(date,"%Y-%m-%dT%H:%M:%SZ")
    
    def __get_last_cs(self):
        self.db.read(self.db_name)
        date = self.db.get("NUBANK","last_card_statements")
        return datetime.strptime(date,"%Y-%m-%dT%H:%M:%SZ")

    def __save_last_date(self,field,date):
        self.db.read(self.db_name)
        cnfFile = open(self.db_name, "w")
        self.db.set("NUBANK",field,date.strftime("%Y-%m-%dT%H:%M:%SZ"))
        self.db.write(cnfFile)
        cnfFile.close() 

    def __save(self,field,data):
        self.db.read('db/nu.cfg')
        cnfFile = open('db/nu.cfg', "w",encoding="utf-8")
        self.db.set("NUBANK",field,str(data))
        self.db.write(cnfFile)
        cnfFile.close()





