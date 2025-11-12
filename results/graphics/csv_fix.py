files = [
    'highcost_h3.csv',
    'highcost_h6.csv',
    'lowcost_h3.csv',
    'lowcost_h6.csv'
]

for file in files:
    with open("results/"+file, 'r', encoding='utf-8') as con:
        file_content = con.read()
        file_content = file_content.replace('instances/', '\ninstances/')
    with open("results/"+file, 'w', encoding='utf-8') as con:
        con.write(file_content)