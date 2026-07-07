import sqlite3

# Esse script lê o schema.sql e usa ele pra criar o banco de dados.
conn = sqlite3.connect('database/academia.db')

with open('database/schema.sql', encoding='utf-8') as arquivo:
    conn.executescript(arquivo.read())

conn.commit()
conn.close()

print('Banco de dados criado com sucesso!')