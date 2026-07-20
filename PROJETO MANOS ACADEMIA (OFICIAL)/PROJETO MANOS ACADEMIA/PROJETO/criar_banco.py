import os
import psycopg2
from psycopg2 import sql

# Dados de conexão com o PostgreSQL
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'academia'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'


def criar_banco():
    """
    Cria o banco 'academia' caso ele não exista.
    """
    conexao = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname='postgres',
        user=DB_USER,
        password=DB_PASSWORD
    )

    conexao.autocommit = True
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (DB_NAME,)
    )

    if cursor.fetchone() is None:
        cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME))
        )
        print(f'Banco "{DB_NAME}" criado.')
    else:
        print(f'Banco "{DB_NAME}" já existe.')

    cursor.close()
    conexao.close()


def tabelas_existem():
    """
    Verifica se a tabela 'plano' já existe no banco.
    """
    conexao = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'plano'
        )
    """)
    existe = cursor.fetchone()[0]

    cursor.close()
    conexao.close()

    return existe



def criar_tabelas():
    """
    Cria as tabelas executando o schema.sql, mas só na primeira vez —
    se as tabelas já existirem, não faz nada.
    """
    if tabelas_existem():
        print('Tabelas já existem, mantendo os dados atuais.')
        return

    conexao = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = conexao.cursor()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ARQUIVO_SQL = os.path.join(BASE_DIR, 'database', 'schema.sql')

    with open(ARQUIVO_SQL, 'r', encoding='utf-8') as arquivo:
        cursor.execute(arquivo.read())

    conexao.commit()

    cursor.close()
    conexao.close()


if __name__ == '__main__':
    criar_banco()
    criar_tabelas()
    print("Banco configurado com sucesso!")