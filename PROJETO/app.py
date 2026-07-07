import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)

# flash() guarda mensagens na sessão, e toda sessão do Flask precisa de uma chave secreta pra funcionar
app.secret_key = 'chave-secreta-academia-2024'

# Pega o caminho da pasta desse arquivo, pra funcionar de qualquer lugar que rodar o projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(BASE_DIR, 'database', 'academia.db')


def conectar():
    """
    Abre uma conexao com o banco de dados SQLite.

    O 'row_factory = sqlite3.Row' faz cada linha devolvida pelo banco
    se comportar quase como um dicionario, entao a gente consegue
    escrever linha['nome'] (ou ate linha.nome dentro do HTML) em vez
    de ficar contando a posicao de cada coluna.
    """
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


# Valores válidos dos select dos formulários, centralizados aqui pra não repetir em vários lugares
DURACOES_VALIDAS = ('1', '3', '6', '12')
NIVEIS_VALIDOS = ('Iniciante', 'Intermediário', 'Avançado', 'Todos os níveis')
PRECO_MINIMO = 50
PRECO_MAXIMO = 900


def validar_dados_plano(form, unidades, modalidades):
    """
    Confere se os dados enviados pelo formulario (adicionar OU editar)
    fazem sentido antes de irem pro banco.

    Devolve uma LISTA DE ERROS (textos). Se a lista vier vazia, deu
    tudo certo e pode salvar.

    Por que validar de novo aqui, se o HTML ja tem "required", "min" e
    "max"? Porque a validacao do HTML so protege o formulario em si.
    Qualquer pessoa pode mandar uma requisicao direto pra "/adicionar"
    (por fora do navegador) e pular essas regras. A validacao que
    realmente protege o banco tem que estar aqui, no Python.
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


# rota da ágina inicial
@app.route('/')
def home():
    return render_template('home.html')


# rota que permite listar os planos
@app.route('/listar')
def listar():
    busca = request.args.get('busca', '')
    modalidade_id = request.args.get('modalidade', '')

    conexao = conectar()

    # comando pra trazer o nome da unidade e da modalidade junto com o plano numa única busca
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
        sql += ' AND (plano.nome LIKE ? OR unidade.nome LIKE ?)'
        termo = f'%{busca}%'
        parametros += [termo, termo]

    if modalidade_id:
        sql += ' AND plano.modalidade_id = ?'
        parametros.append(modalidade_id)

    planos = conexao.execute(sql, parametros).fetchall()
    modalidades = conexao.execute('SELECT * FROM modalidade').fetchall()
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
    plano = conexao.execute('''
        SELECT plano.*,
               unidade.nome AS unidade_nome,
               modalidade.nome AS modalidade_nome
        FROM plano
        JOIN unidade ON plano.unidade_id = unidade.id
        JOIN modalidade ON plano.modalidade_id = modalidade.id
        WHERE plano.id = ?
    ''', (id,)).fetchone()
    conexao.close()

    # Se não existe plano com o id informado, mostra a página 404 customizada
    if plano is None:
        abort(404)

    return render_template('detalhes.html', plano=plano)


# rota para adicionar planos
@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    conexao = conectar()
    unidades = conexao.execute('SELECT * FROM unidade').fetchall()
    modalidades = conexao.execute('SELECT * FROM modalidade').fetchall()

    if request.method == 'POST':
        erros = validar_dados_plano(request.form, unidades, modalidades)

        if erros:
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

        conexao.execute('''
            INSERT INTO plano (nome, duracao, nivel, preco, descricao, unidade_id, modalidade_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
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
        conexao.close()

        flash(f'Plano "{request.form["nome"]}" adicionado com sucesso!', 'sucesso')
        return redirect(url_for('listar'))

    # GET: mostra o formulario vazio (valores={} = nenhum campo preenchido)
    conexao.close()
    return render_template('adicionar.html', unidades=unidades, modalidades=modalidades, valores={})


# rota para editar planos que já existem
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conexao = conectar()
    plano = conexao.execute('SELECT * FROM plano WHERE id = ?', (id,)).fetchone()

    if plano is None:
        conexao.close()
        abort(404)

    unidades = conexao.execute('SELECT * FROM unidade').fetchall()
    modalidades = conexao.execute('SELECT * FROM modalidade').fetchall()

    if request.method == 'POST':
        erros = validar_dados_plano(request.form, unidades, modalidades)

        if erros:
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

        conexao.execute('''
            UPDATE plano
            SET nome = ?, duracao = ?, nivel = ?, preco = ?, descricao = ?,
                unidade_id = ?, modalidade_id = ?
            WHERE id = ?
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
    conexao.close()
    return render_template('editar.html', plano=plano, unidades=unidades, modalidades=modalidades, valores=valores)


# rota para excluir planos
@app.route('/excluir/<int:id>')
def excluir(id):
    conexao = conectar()
    plano = conexao.execute('SELECT * FROM plano WHERE id = ?', (id,)).fetchone()

    if plano is None:
        conexao.close()
        abort(404)

    nome_plano = plano['nome']  # guarda o nome antes de apagar, pra usar na mensagem

    conexao.execute('DELETE FROM plano WHERE id = ?', (id,))
    conexao.commit()
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
