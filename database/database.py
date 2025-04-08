from database.database_utils import executar_query


def criar_tabelas():
    """
    Cria as tabelas necessárias no banco de dados, caso não existam.
    
    As tabelas criadas são:
      - usuarios
      - ferramentas
      - logs
      - maquinas
    """
    tabelas = [
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL,
            rfid TEXT UNIQUE NOT NULL,
            tipo TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ferramentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo_barra TEXT UNIQUE NOT NULL,
            quantidade INTEGER NOT NULL,
            estoque_ativo INTEGER NOT NULL DEFAULT 0,
            consumivel TEXT NOT NULL DEFAULT 'NÃO'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            ferramenta_id INTEGER NOT NULL,
            acao TEXT NOT NULL,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            quantidade INTEGER,
            motivo TEXT,
            operacoes INTEGER,
            avaliacao INTEGER,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY(ferramenta_id) REFERENCES ferramentas(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS maquinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            localizacao TEXT
        )
        """
    ]
    try:
        for tabela in tabelas:
            executar_query(tabela)
        print("✅ Banco de dados configurado com sucesso!")
    except Exception as e:
        print(f"⚠️ Erro ao criar tabelas: {e}")


def buscar_ferramenta_por_codigo(codigo_barra):
    """
    Busca uma ferramenta pelo código de barras.

    Parâmetros:
        codigo_barra (str): Código de barras da ferramenta.

    Retorna:
        dict: Dados da ferramenta (id, nome, quantidade, estoque_ativo, consumivel) se encontrada; caso contrário, None.
    """
    query = """
    SELECT id, nome, quantidade, estoque_ativo, consumivel
    FROM ferramentas
    WHERE codigo_barra = ?
    """
    try:
        resultado = executar_query(query, (codigo_barra,), fetch=True)
        if resultado:
            ferramenta_id, nome, quantidade, estoque_ativo, consumivel = resultado[0]
            return {
                "id": ferramenta_id,
                "nome": nome,
                "quantidade": quantidade,
                "estoque_ativo": estoque_ativo,
                "consumivel": consumivel.strip().upper()  # Esperado: 'SIM' ou 'NÃO'
            }
    except Exception as e:
        print(f"⚠️ Erro ao buscar ferramenta: {e}")
    return None



def registrar_movimentacao(usuario_id, codigo_barra, acao, quantidade, motivo=None, operacoes=None, avaliacao=None):
    """
    Registra uma movimentação de ferramenta e atualiza os estoques (total e ativo) conforme a ação.

    Parâmetros:
        usuario_id (int): ID do usuário que realiza a operação.
        codigo_barra (str): Código de barras da ferramenta.
        acao (str): Ação realizada ('RETIRADA', 'DEVOLUCAO' ou 'CONSUMO').
        quantidade (int): Quantidade a ser movimentada.
        motivo (str, opcional): Motivo da operação, necessário para CONSUMO.
        operacoes (int, opcional): Número de operações realizadas (para consumo).
        avaliacao (int, opcional): Nota de 1 a 5 quanto à qualidade/durabilidade (para consumo).

    Retorna:
        dict: {'status': bool, 'mensagem': str}
    """
    ferramenta = buscar_ferramenta_por_codigo(codigo_barra)
    if not ferramenta:
        return {"status": False, "mensagem": "⚠️ Ferramenta não encontrada!"}

    ferramenta_id = ferramenta["id"]

    try:
        if acao == "RETIRADA":
            query_log = "INSERT INTO logs (usuario_id, ferramenta_id, acao, quantidade) VALUES (?, ?, ?, ?)"
            executar_query(query_log, (usuario_id, ferramenta_id, acao, quantidade))

            query_update = """
            UPDATE ferramentas 
            SET quantidade = quantidade - ?, 
                estoque_ativo = estoque_ativo + ?
            WHERE codigo_barra = ?
            """
            executar_query(query_update, (quantidade, quantidade, codigo_barra))

        elif acao == "DEVOLUCAO":
            query_log = "INSERT INTO logs (usuario_id, ferramenta_id, acao, quantidade) VALUES (?, ?, ?, ?)"
            executar_query(query_log, (usuario_id, ferramenta_id, acao, quantidade))

            query_update = """
            UPDATE ferramentas 
            SET quantidade = quantidade + ?, 
                estoque_ativo = estoque_ativo - ?
            WHERE codigo_barra = ?
            """
            executar_query(query_update, (quantidade, quantidade, codigo_barra))

        elif acao == "CONSUMO":
            if motivo is None or operacoes is None or avaliacao is None:
                return {"status": False, "mensagem": "⚠️ Dados incompletos para consumo!"}

            query_log = """
            INSERT INTO logs (usuario_id, ferramenta_id, acao, quantidade, motivo, operacoes, avaliacao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            executar_query(query_log, (usuario_id, ferramenta_id, acao, quantidade, motivo, operacoes, avaliacao))

            # Consumo: estoque total ↓, estoque_ativo permanece inalterado
            query_update = """
            UPDATE ferramentas 
            SET quantidade = quantidade - ?
            WHERE codigo_barra = ?
            """
            executar_query(query_update, (quantidade, codigo_barra))

        else:
            return {"status": False, "mensagem": "⚠️ Ação inválida!"}

        return {"status": True, "mensagem": f"✅ Movimentação '{acao}' realizada com sucesso!"}

    except Exception as e:
        return {"status": False, "mensagem": f"⚠️ Erro ao registrar movimentação: {e}"}



def buscar_ultimas_movimentacoes(limit=10):
    """
    Recupera as últimas movimentações registradas.
    
    Parâmetros:
        limit (int): Número máximo de registros a serem retornados (padrão é 10).
    
    Retorna:
        list: Lista de registros com detalhes da movimentação. Em caso de erro, retorna uma lista vazia.
    """
    query = """
    SELECT l.data_hora, u.nome AS usuario_nome, f.codigo_barra, f.nome AS ferramenta_nome, 
           l.acao, l.quantidade, l.motivo, l.operacoes, l.avaliacao
    FROM logs l
    JOIN usuarios u ON l.usuario_id = u.id
    JOIN ferramentas f ON l.ferramenta_id = f.id
    ORDER BY l.data_hora DESC
    LIMIT ?
    """
    try:
        resultados = executar_query(query, (limit,), fetch=True)
        return resultados
    except Exception as e:
        print(f"⚠️ Erro ao buscar movimentações: {e}")
        return []
