import sqlite3

# Lê o schema.sql e cria o banco, só precisa rodar uma vez 

conexao = sqlite3.connect('database/academia.db')

with open('database/schema.sql', encoding='utf-8') as arquivo:
    conexao.executescript(arquivo.read())

conexao.commit()
conexao.close()

print('Banco de dados criado com sucesso!')
