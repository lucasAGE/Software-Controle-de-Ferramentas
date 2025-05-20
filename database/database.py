import sqlite3
from database.database_utils import executar_query


def criar_tabelas():
    """
    Cria as tabelas necessárias no banco de dados, caso não existam:

      - usuarios
      - ferramentas
      - logs
      - maquinas
    """
    tabelas = [
        # Usuários
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL,
            rfid TEXT UNIQUE NOT NULL,
            tipo TEXT NOT NULL
        )
        """,
        # Ferramentas (sem campo estoque_ativo estático)
        """
        CREATE TABLE IF NOT EXISTS ferramentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo_barra TEXT UNIQUE NOT NULL,
            estoque_almoxarifado INTEGER NOT NULL,
            consumivel TEXT NOT NULL DEFAULT 'NÃO'
        )
        """,
        # Logs de movimentação (ledger)
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            ferramenta_id INTEGER NOT NULL,
            acao TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            motivo TEXT,
            operacoes INTEGER,
            avaliacao INTEGER,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY(ferramenta_id) REFERENCES ferramentas(id)
        )
        """,
        # Máquinas
        """
        CREATE TABLE IF NOT EXISTS maquinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
        """
    ]

    try:
        for ddl in tabelas:
            executar_query(ddl)
        print("✅ Banco de dados configurado com sucesso!")
    except Exception as e:
        print(f"⚠️ Erro ao criar tabelas: {e}")


def buscar_ferramenta_por_codigo(codigo_barra: str):
    """
    Busca uma ferramenta pelo código de barras.

    Retorna dict com id, nome, estoque_almoxarifado e consumivel.
    """
    query = (
        "SELECT id, nome, estoque_almoxarifado, consumivel "
        "FROM ferramentas WHERE codigo_barra = ?"
    )
    resultado = executar_query(query, (codigo_barra,), fetch=True)
    if not resultado:
        return None

    fid, nome, est_alm, consumivel = resultado[0]
    return {
        "id": fid,
        "nome": nome,
        "estoque_almoxarifado": est_alm,
        "consumivel": consumivel.strip().upper()
    }


def registrar_movimentacao(
    usuario_id: int,
    codigo_barra: str,
    acao: str,
    quantidade: int,
    motivo: str = None,
    operacoes: int = None,
    avaliacao: int = None
) -> dict:
    """
    Registra movimentação de ferramentas no ledger e ajusta estoque_almoxarifado.

    Ações: RETIRADA, DEVOLUCAO, CONSUMO, ADICAO, SUBTRACAO.
    """
    # Busca dados da ferramenta
    ferramenta = buscar_ferramenta_por_codigo(codigo_barra)
    if not ferramenta:
        return {"status": False, "mensagem": "⚠️ Ferramenta não encontrada!"}

    fid = ferramenta["id"]
    est_alm = ferramenta["estoque_almoxarifado"]

    # Se for devolução, calcula saldo ativo via logs
    if acao == "DEVOLUCAO":
        saldo = executar_query(
            """
            SELECT COALESCE(
                SUM(CASE WHEN acao = 'RETIRADA' THEN quantidade
                         WHEN acao = 'DEVOLUCAO' THEN -quantidade ELSE 0 END)
            , 0)
            FROM logs
            WHERE usuario_id = ? AND ferramenta_id = ?
            """,
            (usuario_id, fid),
            fetch_one=True
        )
        saldo_ativo = saldo[0] if saldo else 0
    else:
        saldo_ativo = None

    # Validações
    if acao == "RETIRADA" and quantidade > est_alm:
        return {"status": False, "mensagem": "❌ Estoque insuficiente para retirada!"}
    if acao == "DEVOLUCAO" and quantidade > saldo_ativo:
        return {"status": False, "mensagem": "❌ Estoque ativo insuficiente para devolução!"}
    if acao == "CONSUMO":
        if motivo is None or operacoes is None or avaliacao is None:
            return {"status": False, "mensagem": "⚠️ Dados incompletos para consumo!"}
        if quantidade > est_alm:
            return {"status": False, "mensagem": "❌ Estoque insuficiente para consumo!"}
    if acao in ("ADICAO", "SUBTRACAO") and quantidade <= 0:
        return {"status": False, "mensagem": "⚠️ Quantidade deve ser maior que zero!"}

    try:
        # Insere no ledger
        sql_log = (
            "INSERT INTO logs (usuario_id, ferramenta_id, acao, quantidade, motivo, operacoes, avaliacao) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)"
        )
        executar_query(sql_log, (usuario_id, fid, acao, quantidade, motivo, operacoes, avaliacao))

        # Ajusta estoque_almoxarifado
        ajuste = "-" if acao in ("RETIRADA", "CONSUMO", "SUBTRACAO") else "+"
        if acao == "DEVOLUCAO" or acao == "ADICAO":
            ajuste = "+"

        executar_query(
            f"UPDATE ferramentas SET estoque_almoxarifado = estoque_almoxarifado {ajuste} ? WHERE codigo_barra = ?",
            (quantidade, codigo_barra)
        )

        return {"status": True, "mensagem": f"✅ {acao.capitalize()} de {quantidade} unidades realizado com sucesso!"}
    except Exception as e:
        return {"status": False, "mensagem": f"⚠️ Erro ao registrar movimentação: {e}"}


def buscar_ultimas_movimentacoes(limit: int = 10) -> list:
    """
    Recupera as últimas movimentações registradas.

    Retorna lista de tuplas: (data_hora, usuario_nome, codigo_barra,
    ferramenta_nome, acao, quantidade, motivo, operacoes, avaliacao).
    """
    query = """
    SELECT
        l.data_hora,
        u.nome     AS usuario_nome,
        f.codigo_barra,
        f.nome     AS ferramenta_nome,
        l.acao,
        l.quantidade,
        l.motivo,
        l.operacoes,
        l.avaliacao
    FROM logs l
    JOIN usuarios u  ON l.usuario_id    = u.id
    JOIN ferramentas f ON l.ferramenta_id = f.id
    ORDER BY l.data_hora DESC
    LIMIT ?
    """
    return executar_query(query, (limit,), fetch=True) or []
