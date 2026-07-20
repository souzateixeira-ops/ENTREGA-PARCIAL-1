import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from criar_banco import criar_banco, criar_tabelas

app = Flask(__name__)

# flash() guarda mensagens na sessão, e toda sessão do Flask precisa de uma chave secreta pra funcionar
app.secret_key = 'chave-secreta-academia-2024'

criar_banco()
criar_tabelas()

# Dados de conexão com o PostgreSQL (ajuste USER e PASSWORD conforme o seu pgAdmin)DB_HOST = 'localhost'
DB_HOST = 'localhost' 
DB_PORT = '5432'
DB_NAME = 'academia'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

def conectar():
      """
      Abre uma conexão com o banco de dados PostgreSQL.
  
      O 'cursor_factory=psycopg2.extras.RealDictCursor' faz cada linha
      virar um dicionário, então dá pra usar linha['nome'] nos templates.
      """
      conexao = psycopg2.connect(
          host=DB_HOST,
          port=DB_PORT,
          dbname=DB_NAME,
          user=DB_USER,
          password=DB_PASSWORD,
          cursor_factory=psycopg2.extras.RealDictCursor
      )
      return conexao

# Valores válidos dos selects do formulário
DURACOES_VALIDAS = ('1', '3', '6', '12')
NIVEIS_VALIDOS = ('Iniciante', 'Intermediário', 'Avançado', 'Todos os níveis')
PRECO_MINIMO = 50
PRECO_MAXIMO = 900


def validar_dados_plano(form, unidades, modalidades):
    """
    Valida os dados do formulário (adicionar ou editar) antes de salvar no banco.
    Retorna uma lista de erros — se vier vazia, pode salvar.

    Validamos de novo aqui (mesmo com "required"/"min"/"max" no HTML)
    porque a validação do HTML pode ser burlada por quem envia a
    requisição direto, fora do navegador.
    """
    erros = []

    if not form.get('nome', '').strip():
        erros.append('O nome do plano é obrigatório.')

    if not form.get('descricao', '').strip():
        erros.append('A descrição é obrigatória.')

    ids_unidades_validas = [str(u['id']) for u in unidades]
    if form.get('unidade', '') not in ids_unidades_validas:
        erros.append('Selecione uma unidade válida.')

    ids_modalidades_validas = [str(m['id']) for m in modalidades]
    if form.get('modalidade', '') not in ids_modalidades_validas:
        erros.append('Selecione uma modalidade válida.')

    if form.get('duracao', '') not in DURACOES_VALIDAS:
        erros.append('Selecione uma duração válida.')

    if form.get('nivel', '') not in NIVEIS_VALIDOS:
        erros.append('Selecione um nível válido.')

    preco_texto = form.get('preco', '')
    try:
        preco = float(preco_texto)
        if preco < PRECO_MINIMO or preco > PRECO_MAXIMO:
            erros.append(f'A mensalidade deve estar entre R$ {PRECO_MINIMO},00 e R$ {PRECO_MAXIMO},00.')
    except ValueError:
        erros.append('Informe um valor de mensalidade válido (apenas números).')

    return erros


# rota da página inicial
@app.route('/')
def home():
    return render_template('home.html')


# rota que lista os planos
@app.route('/listar')
def listar():
    busca = request.args.get('busca', '')
    modalidade_id = request.args.get('modalidade', '')

    conexao = conectar()
    cursor = conexao.cursor()

# traz o nome da unidade e da modalidade junto com o plano numa busca só.
    sql = '''
        SELECT plano.*,
               unidade.nome AS unidade_nome,
               modalidade.nome AS modalidade_nome
        FROM plano
        JOIN unidade ON plano.unidade_id = unidade.id
        JOIN modalidade ON plano.modalidade_id = modalidade.id
        WHERE 1 = 1
    '''
    parametros = []

    if busca:
        sql += ' AND (plano.nome ILIKE %s OR unidade.nome ILIKE %s)'
        termo = f'%{busca}%'
        parametros += [termo, termo]

    if modalidade_id:
        sql += ' AND plano.modalidade_id = %s'
        parametros.append(modalidade_id)

    cursor.execute(sql, parametros)
    planos = cursor.fetchall()

    cursor.execute('SELECT * FROM modalidade')
    modalidades = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        'listar.html',
        planos=planos,
        busca=busca,
        modalidade_id=modalidade_id,
        modalidades=modalidades
    )


# rota para ver os detalhes dos planos
@app.route('/plano/<int:id>')
def detalhes(id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT plano.*,
               unidade.nome AS unidade_nome,
               modalidade.nome AS modalidade_nome
        FROM plano
        JOIN unidade ON plano.unidade_id = unidade.id
        JOIN modalidade ON plano.modalidade_id = modalidade.id
        WHERE plano.id = %s
    ''', (id,))
    plano = cursor.fetchone()
    cursor.close()
    conexao.close()

    # Se não existe plano com o id informado, mostra a página 404 customizada
    if plano is None:
        abort(404)

    return render_template('detalhes.html', plano=plano)


# rota para adicionar planos
@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM unidade')
    unidades = cursor.fetchall()
    cursor.execute('SELECT * FROM modalidade')
    modalidades = cursor.fetchall()

    if request.method == 'POST':
        erros = validar_dados_plano(request.form, unidades, modalidades)

        if erros:
            cursor.close()
            conexao.close()
            for erro in erros:
                flash(erro, 'erro')
            # Devolve pro mesmo formulário, mantendo os dados que a pessoa já tinha digitado
            return render_template(
                'adicionar.html',
                unidades=unidades,
                modalidades=modalidades,
                valores=request.form
            )

        cursor.execute('''
            INSERT INTO plano (nome, duracao, nivel, preco, descricao, unidade_id, modalidade_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            request.form['nome'],
            int(request.form['duracao']),
            request.form['nivel'],
            float(request.form['preco']),
            request.form['descricao'],
            int(request.form['unidade']),
            int(request.form['modalidade']),
        ))
        conexao.commit()
        cursor.close()
        conexao.close()

        flash(f'Plano "{request.form["nome"]}" adicionado com sucesso!', 'sucesso')
        return redirect(url_for('listar'))

  # Quando a pessoa só abre a página (sem enviar o formulário), mostra ele vazio    
    cursor.close()
    conexao.close()
    return render_template('adicionar.html', unidades=unidades, modalidades=modalidades, valores={})


# rota para editar planos que já existem
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM plano WHERE id = %s', (id,))
    plano = cursor.fetchone()

    if plano is None:
        cursor.close()
        conexao.close()
        abort(404)

    cursor.execute('SELECT * FROM unidade')
    unidades = cursor.fetchall()
    cursor.execute('SELECT * FROM modalidade')
    modalidades = cursor.fetchall()

    if request.method == 'POST':
        erros = validar_dados_plano(request.form, unidades, modalidades)

        if erros:
            cursor.close()
            conexao.close()
            for erro in erros:
                flash(erro, 'erro')
            # delvolve para o formulário com as alterções feitas
            return render_template(
                'editar.html',
                plano=plano,
                unidades=unidades,
                modalidades=modalidades,
                valores=request.form
            )

        cursor.execute('''
            UPDATE plano
            SET nome = %s, duracao = %s, nivel = %s, preco = %s, descricao = %s,
                unidade_id = %s, modalidade_id = %s
            WHERE id = %s
        ''', (
            request.form['nome'],
            int(request.form['duracao']),
            request.form['nivel'],
            float(request.form['preco']),
            request.form['descricao'],
            int(request.form['unidade']),
            int(request.form['modalidade']),
            id
        ))
        conexao.commit()
        cursor.close()
        conexao.close()

        flash(f'Plano "{request.form["nome"]}" atualizado com sucesso!', 'sucesso')
        return redirect(url_for('listar'))

    # GET: monta valores com os dados atuais do plano, pra abrir o formulário já preenchido.
    valores = {
        'unidade': str(plano['unidade_id']),
        'nome': plano['nome'],
        'duracao': str(plano['duracao']),
        'nivel': plano['nivel'],
        'preco': plano['preco'],
        'modalidade': str(plano['modalidade_id']),
        'descricao': plano['descricao'],
    }
    cursor.close()
    conexao.close()
    return render_template('editar.html', plano=plano, unidades=unidades, modalidades=modalidades, valores=valores)


# rota para excluir planos
@app.route('/excluir/<int:id>')
def excluir(id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM plano WHERE id = %s', (id,))
    plano = cursor.fetchone()

    if plano is None:
        cursor.close()
        conexao.close()
        abort(404)

    nome_plano = plano['nome']  # guarda o nome antes de apagar, pra usar na mensagem

    cursor.execute('DELETE FROM plano WHERE id = %s', (id,))
    conexao.commit()
    cursor.close()
    conexao.close()

    flash(f'Plano "{nome_plano}" excluído com sucesso!', 'sucesso')
    return redirect(url_for('listar'))


# rotas para o tratamento de erros
@app.errorhandler(404)
def pagina_nao_encontrada(erro):
    return render_template('404.html'), 404


@app.errorhandler(500)
def erro_interno_do_servidor(erro):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)