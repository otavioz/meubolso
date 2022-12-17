
base = 'Geral'
debt = '2023'

class Arrears:
    table = f'{base}!B5:F35'
    name = 0
    value = 1
    reason = 2
    status = 3
    last_att = 4

class Limits:
    table = f'{base}!H4:K10'
    name = 0
    max_value = 1
    value = 2
    origin = 3

class Categories:
    table = f'{base}!M4:P35'
    name = 0 
    is_active = 1
    value_1 = 2
    value_2 = 3

class Debts:
    table = f'{debt}!A14:H900'
    name = 0
    origin = 1
    value = 2
    category = 3
    date = 4
    ref = 5
    obs = 6
    resp = 7