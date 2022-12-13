import re
from finances.finances import Finances
from datetime import timedelta, datetime
import os
from pathlib import Path


class FO:

    def __init__(self) -> None:
        self.f = Finances()

    def insert_last_bills(self):
        bs = []
        
        bs.extend(self.f.get_bank_statement())
        bs.extend(self.f.get_card_statements())
        bs = sorted(bs, key=lambda kv: datetime.strptime(kv[4], '%d/%m/%Y'), reverse=True)
        self.f.save_debt(bs,list_=True)
        return bs

    def insert_from_csv(self):
        directory = str(Path().absolute())+'\csv'
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            lists = []
            with open(file_path,  mode="r", encoding='utf-8-sig') as f:
                filelines = f.readlines()
                header = filelines.pop(0)
                origem = 'Nubank' if 'date,category,title,amount' in header else 'Nuconta'
                for line in filelines:
                    line = re.sub(r"[\n\t]*", "", line).split(',')
                    if origem == 'Nubank':
                        date_ = datetime.strptime(line[0],"%Y-%m-%d")
                        if date_.day >= self.f.get_close_day():
                            month = date_.month+1
                        else :
                            month = date_.month

                        debt = self.f.debt(
                            nome = line[2],
                            origem = origem,
                            valor = line[3],
                            categoria = line[1],
                            ref = month,
                            data = date_)
                        lists.append(debt.to_list())

                    elif origem == 'Nuconta':
                        date_ = datetime.strptime(line[0],"%d/%m/%Y")
                        if date_.day >= self.f.get_close_day():
                            month = date_.month+1
                        else :
                            month = date_.month

                        tittle = line[3].split(' -',1)[0]
                        det = line[3].replace(tittle,'')
                        debt = self.f.debt(
                            nome = tittle,
                            origem = origem,
                            valor = line[1],
                            categoria = tittle,
                            data = date_,
                            ref = month,
                            obs = det)
                        lists.append(debt.to_list())
            os.remove(file_path)
            self.f.save_debt(lists,list_=True)
        

    def finances(self,m):
        step = len(m)
        if step == 1:
            message = "Escolha uma das opções:\n"
            command_list = {
            "summ":"Resumo do mês",
            #"invoice":"Extrato",
            "ins":"Inserir últimas transações",
            "inv":"Visualizar fatura do mês",
            "li":"Alterar limite de consumo",
            "day":"Alterar dia de fechamento da fatura Nubank",
            "/cancel":"Nenhuma das opções"}

            reply_markup = {"inline_keyboard":[]}
            for key,text in command_list.items():                 
                reply_markup["inline_keyboard"].append([{"text":text,"callback_data":f"/f;{key}"}])
            return {'message':message, 'reply_markup':reply_markup}
        elif step == 2:
            if m[1] == 'summ':
                return {'message':self.get_summary()}
            elif m[1] == 'ins':
                trns = self.insert_last_bills()
                return {'message':f'{len(trns)} transações foram inseridas.'}
        elif step == 3:
            pass
        else:
            raise ValueError("Mensagem incorreta.")
    
    def get_summary(self):
        bill_list = self.f.list_origem()
        cat_list = self.f.list_cat()

        limite = self.f.monthly_limit()
        debts = self.f.read_debts()
        if len(debts) == 0:
            return 'Nenhum registro de gasto encontrado.'
        weighty = debts[0]
        for bill in debts:
            bill_list[bill.origem] += bill.valor
            if bill.origem == 'Nubank':
                cat_list[bill.categoria] += bill.valor
                if bill.valor < weighty.valor:
                    weighty = bill

        cat_list = sorted(cat_list.items(), key=lambda kv: kv[1], reverse=False)

        #TODO a maior numero de compras por categoria, soma do valor e nome da categoria
        amount = round(-bill_list["Nubank"] / limite * 100,2)
        now_day = int(datetime.now().strftime("%d"))
        if now_day <= 16:
            data = str(round((now_day + 14)/30*100,2))
        else:
            data = str(round((now_day - 16)/30*100,2))

        message = f'Fatura do Nubank no valor de R${round(-bill_list["Nubank"],2)}, cerca de {amount}% do limite de R${limite} no período de {data}% do mês.'\
            f'\nCompra mais significativa é a <b>{weighty.nome}</b> no valor de R${-weighty.valor} feita no dia {weighty.data.strftime("%d/%m/%Y")}.'\
            f'\n<b>{cat_list[0][0]}</b> foi a categoria com mais gastos, totalizando R${-cat_list[0][1]}.'\
            f'\nTransações na NuConta totalizam R${-bill_list["Nuconta"]}.'
        return message

