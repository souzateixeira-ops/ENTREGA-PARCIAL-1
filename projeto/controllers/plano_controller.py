from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.plano import Plano
from models.unidade import Unidade
from models.modalidade import Modalidade

# Esse Blueprint cuida de tudo relacionado a "plano":
# listar, ver detalhes, adicionar, editar e excluir.
plano_bp = Blueprint('plano', __name__)


# Só pra não espalhar os mesmos valores "mágicos" em vários lugares
# do código. Esses são exatamente os valores que aparecem nos <select>
# dos formulários (adicionar.html e editar.html).
DURACOES_VALIDAS = ('1', '3', '6', '12')
NIVEIS_VALIDOS = ('Iniciante', 'Intermediário', 'Avançado', 'Todos os níveis')
PRECO_MINIMO = 50
PRECO_MAXIMO = 900


def validar_dados_plano(form, unidades, modalidades):
    """
    Confere se os dados enviados por um formulário (adicionar OU editar)
    fazem sentido antes de irem pro banco.

    Devolve uma LISTA DE ERROS (strings). Se a lista vier vazia, é porque
    passou em tudo e pode salvar.

    Por que validar de novo aqui, se o HTML já tem "required", "min" e
    "max"? Porque validação de HTML só protege o formulário em si — ela
    não protege a ROTA. Qualquer pessoa pode mandar uma requisição POST
    direto pra "/adicionar" (por fora do formulário, por exemplo com
    curl ou Postman) e pular todas as regras do navegador. A validação
    de verdade tem que estar no back-end.
    """
    erros = []

    # --- Nome do plano ---
    if not form.get('nome', '').strip():
        erros.append('O nome do plano é obrigatório.')

    # --- Descrição ---
    if not form.get('descricao', '').strip():
        erros.append('A descrição é obrigatória.')

    # --- Unidade: tem que vir preenchida e apontar pra uma unidade que exista ---
    ids_unidades_validas = [u.id for u in unidades]
    unidade_id = form.get('unidade', '')
    if not unidade_id.isdigit() or int(unidade_id) not in ids_unidades_validas:
        erros.append('Selecione uma unidade válida.')

    # --- Modalidade: mesma ideia da unidade ---
    ids_modalidades_validas = [m.id for m in modalidades]
    modalidade_id = form.get('modalidade', '')
    if not modalidade_id.isdigit() or int(modalidade_id) not in ids_modalidades_validas:
        erros.append('Selecione uma modalidade válida.')

    # --- Duração: só aceitamos as opções que existem no select (1, 3, 6 ou 12 meses) ---
    if form.get('duracao', '') not in DURACOES_VALIDAS:
        erros.append('Selecione uma duração válida.')

    # --- Nível: só aceitamos as opções que existem no select ---
    if form.get('nivel', '') not in NIVEIS_VALIDOS:
        erros.append('Selecione um nível válido.')

    # --- Preço: precisa ser um número dentro da faixa permitida ---
    preco_str = form.get('preco', '')
    try:
        preco = float(preco_str)
        if preco < PRECO_MINIMO or preco > PRECO_MAXIMO:
            erros.append(f'A mensalidade deve estar entre R$ {PRECO_MINIMO},00 e R$ {PRECO_MAXIMO},00.')
    except ValueError:
        erros.append('Informe um valor de mensalidade válido (apenas números).')

    return erros


# ROTA 1: Listar todos os planos (com busca e filtro por modalidade)
@plano_bp.route('/listar')
def listar():
    busca = request.args.get('busca', '')
    modalidade_id = request.args.get('modalidade', '')

    query = Plano.query

    if busca:
        termo = f'%{busca}%'
        query = query.join(Unidade).filter(
            db.or_(Plano.nome.ilike(termo), Unidade.nome.ilike(termo))
        )

    if modalidade_id:
        query = query.filter(Plano.modalidade_id == int(modalidade_id))

    planos = query.all()
    modalidades = Modalidade.query.all()   # pra montar o filtro no HTML

    return render_template(
        'listar.html',
        planos=planos,
        busca=busca,
        modalidade_id=modalidade_id,
        modalidades=modalidades
    )


# ROTA 2: Ver os detalhes de um plano específico
@plano_bp.route('/plano/<int:id>')
def detalhes(id):
    # Se o ID não existir, get_or_404 já dispara um erro 404,
    # que agora cai na nossa página customizada (ver app.py).
    plano = Plano.query.get_or_404(id)
    return render_template('detalhes.html', plano=plano)


# ROTA 3: Adicionar um plano novo
@plano_bp.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    unidades = Unidade.query.all()
    modalidades = Modalidade.query.all()

    if request.method == 'POST':
        erros = validar_dados_plano(request.form, unidades, modalidades)

        if erros:
            # Mostra cada erro encontrado pro usuário (mensagem "flash")
            # e devolve ele pro MESMO formulário, com os dados que ele
            # já tinha digitado (pra não ter que preencher tudo de novo).
            for erro in erros:
                flash(erro, 'erro')
            return render_template(
                'adicionar.html',
                unidades=unidades,
                modalidades=modalidades,
                valores=request.form
            )

        # Passou na validação: agora sim pode criar o registro.
        novo_plano = Plano(
            nome=request.form['nome'],
            duracao=int(request.form['duracao']),
            nivel=request.form['nivel'],
            preco=float(request.form['preco']),
            descricao=request.form['descricao'],
            unidade_id=int(request.form['unidade']),
            modalidade_id=int(request.form['modalidade'])
        )
        db.session.add(novo_plano)
        db.session.commit()

        flash(f'Plano "{novo_plano.nome}" adicionado com sucesso!', 'sucesso')
        return redirect(url_for('plano.listar'))

    # GET: mostra o formulário vazio (valores={} = nenhum campo pré-preenchido)
    return render_template('adicionar.html', unidades=unidades, modalidades=modalidades, valores={})


# ROTA 4: Editar um plano que já existe
@plano_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    plano = Plano.query.get_or_404(id)
    unidades = Unidade.query.all()
    modalidades = Modalidade.query.all()

    if request.method == 'POST':
        erros = validar_dados_plano(request.form, unidades, modalidades)

        if erros:
            for erro in erros:
                flash(erro, 'erro')
            # Devolve pro formulário de edição com o que a pessoa
            # tinha digitado (request.form), não com os dados antigos
            # do banco, senão ela perderia a alteração que fez.
            return render_template(
                'editar.html',
                plano=plano,
                unidades=unidades,
                modalidades=modalidades,
                valores=request.form
            )

        plano.nome = request.form['nome']
        plano.duracao = int(request.form['duracao'])
        plano.nivel = request.form['nivel']
        plano.preco = float(request.form['preco'])
        plano.descricao = request.form['descricao']
        plano.unidade_id = int(request.form['unidade'])
        plano.modalidade_id = int(request.form['modalidade'])
        db.session.commit()

        flash(f'Plano "{plano.nome}" atualizado com sucesso!', 'sucesso')
        return redirect(url_for('plano.listar'))

    # GET: monta 'valores' a partir do que já está salvo no banco.
    # Assim o template sempre lê os campos de "valores" (não importa se é
    # a primeira vez abrindo o formulário ou se voltou de um erro de validação).
    valores = {
        'unidade': str(plano.unidade_id),
        'nome': plano.nome,
        'duracao': str(plano.duracao),
        'nivel': plano.nivel,
        'preco': plano.preco,
        'modalidade': str(plano.modalidade_id),
        'descricao': plano.descricao,
    }
    return render_template('editar.html', plano=plano, unidades=unidades, modalidades=modalidades, valores=valores)


# ROTA 5: Excluir um plano
@plano_bp.route('/excluir/<int:id>')
def excluir(id):
    # get_or_404 também protege essa rota: se o ID não existir,
    # mostra a página 404 customizada em vez de quebrar com erro 500.
    plano = Plano.query.get_or_404(id)
    nome_plano = plano.nome  # guarda o nome antes de apagar, pra usar na mensagem

    db.session.delete(plano)
    db.session.commit()

    flash(f'Plano "{nome_plano}" excluído com sucesso!', 'sucesso')
    return redirect(url_for('plano.listar'))