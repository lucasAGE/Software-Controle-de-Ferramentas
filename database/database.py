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
            estoque_almoxarifado INTEGER NOT NULL,
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


def buscar_ferramenta_por_codigo(codigo_barra):
    """
    Busca uma ferramenta pelo código de barras.

    Parâmetros:
        codigo_barra (str): Código de barras da ferramenta.

    Retorna:
        dict ou None: {
            "id": int,
            "nome": str,
            "estoque_almoxarifado": int,
            "estoque_ativo": int,
            "consumivel": "SIM" ou "NÃO"
        } se encontrada; caso contrário, None.
    """
    query = """
        SELECT id, nome, estoque_almoxarifado, estoque_ativo, consumivel
          FROM ferramentas
         WHERE codigo_barra = ?
    """
    try:
        resultado = executar_query(query, (codigo_barra,), fetch=True)
        if not resultado:
            return None

        fid, nome, est_alm, est_ativo, consumivel = resultado[0]
        return {
            "id": fid,
            "nome": nome,
            "estoque_almoxarifado": est_alm,
            "estoque_ativo": est_ativo,
            "consumivel": consumivel.strip().upper()
        }
    except Exception as e:
        print(f"⚠️ Erro ao buscar ferramenta: {e}")
        return None


def registrar_movimentacao(
    usuario_id,
    codigo_barra,
    acao,
    quantidade,
    motivo=None,
    operacoes=None,
    avaliacao=None
):
    """
    Registra movimentação de ferramentas.

    Ações suportadas:
      - RETIRADA
      - DEVOLUCAO
      - CONSUMO
      - ADICAO
      - SUBTRACAO

    Valida estoque, insere em logs e atualiza tabela ferramentas.

    Retorna:
        dict: {"status": bool, "mensagem": str}
    """
    ferramenta = buscar_ferramenta_por_codigo(codigo_barra)
    if not ferramenta:
        return {"status": False, "mensagem": "⚠️ Ferramenta não encontrada!"}

    fid = ferramenta["id"]
    est_alm = ferramenta["estoque_almoxarifado"]
    est_ativo = ferramenta["estoque_ativo"]

    # Validações iniciais
    if acao == "RETIRADA":
        if quantidade > est_alm:
            return {"status": False, "mensagem": "❌ Estoque insuficiente para retirada!"}

    elif acao == "DEVOLUCAO":
        if quantidade > est_ativo:
            return {"status": False, "mensagem": "❌ Estoque ativo insuficiente para devolução!"}

    elif acao == "CONSUMO":
        if motivo is None or operacoes is None or avaliacao is None:
            return {"status": False, "mensagem": "⚠️ Dados incompletos para consumo!"}
        if quantidade > est_alm:
            return {"status": False, "mensagem": "❌ Estoque insuficiente para consumo!"}

    elif acao in ("ADICAO", "SUBTRACAO"):
        if quantidade <= 0:
            return {"status": False, "mensagem": "⚠️ Quantidade deve ser maior que zero!"}

    else:
        return {"status": False, "mensagem": "⚠️ Ação inválida!"}

    try:
        # RETIRADA
        if acao == "RETIRADA":
            executar_query(
                "INSERT INTO logs (usuario_id, ferramenta_id, acao, quantidade) VALUES (?,?,?,?)",
                (usuario_id, fid, acao, quantidade)
            )
            executar_query(
                """
                UPDATE ferramentas
                   SET estoque_almoxarifado = estoque_almoxarifado - ?,
                       estoque_ativo        = estoque_ativo + ?
                 WHERE codigo_barra = ?
                """,
                (quantidade, quantidade, codigo_barra)
            )
            return {"status": True, "mensagem": f"✅ Retirada de {quantidade} unidades realizada com sucesso!"}

        # DEVOLUCAO
        if acao == "DEVOLUCAO":
            executar_query(
                "INSERT INTO logs (usuario_id, ferramenta_id, acao, quantidade) VALUES (?,?,?,?)",
                (usuario_id, fid, acao, quantidade)
            )
            executar_query(
                """
                UPDATE ferramentas
                   SET estoque_almoxarifado = estoque_almoxarifado + ?,
                       estoque_ativo        = estoque_ativo - ?
                 WHERE codigo_barra = ?
                """,
                (quantidade, quantidade, codigo_barra)
            )
            return {"status": True, "mensagem": f"✅ Devolução de {quantidade} unidades realizada com sucesso!"}

        # CONSUMO
        if acao == "CONSUMO":
            executar_query(
                """
                INSERT INTO logs
                       (usuario_id, ferramenta_id, acao, quantidade, motivo, operacoes, avaliacao)
                VALUES (?,?,?,?,?,?,?)
                """,
                (usuario_id, fid, acao, quantidade, motivo, operacoes, avaliacao)
            )
            executar_query(
                "UPDATE ferramentas SET estoque_almoxarifado = estoque_almoxarifado - ? WHERE codigo_barra = ?",
                (quantidade, codigo_barra)
            )
            return {"status": True, "mensagem": f"✅ Consumo de {quantidade} unidades realizado com sucesso!"}

        # ADICAO
        if acao == "ADICAO":
            executar_query(
                "INSERT INTO logs (usuario_id, ferramenta_id, acao, quantidade) VALUES (?,?,?,?)",
                (usuario_id, fid, acao, quantidade)
            )
            executar_query(
                "UPDATE ferramentas SET estoque_almoxarifado = estoque_almoxarifado + ? WHERE codigo_barra = ?",
                (quantidade, codigo_barra)
            )
            return {"status": True, "mensagem": f"✅ Adição de {quantidade} unidades realizada com sucesso!"}

        # SUBTRACAO
        if acao == "SUBTRACAO":
            executar_query(
                "INSERT INTO logs (usuario_id, ferramenta_id, acao, quantidade) VALUES (?,?,?,?)",
                (usuario_id, fid, acao, quantidade)
            )
            executar_query(
                "UPDATE ferramentas SET estoque_almoxarifado = estoque_almoxarifado - ? WHERE codigo_barra = ?",
                (quantidade, codigo_barra)
            )
            return {"status": True, "mensagem": f"✅ Subtração de {quantidade} unidades realizada com sucesso!"}

        # Caso nenhuma ação seja tratada (não deveria ocorrer)
        return {"status": False, "mensagem": "⚠️ Ação não processada!"}

    except Exception as e:
        return {"status": False, "mensagem": f"⚠️ Erro ao registrar movimentação: {e}"}


def buscar_ultimas_movimentacoes(limit=10):
    """
    Recupera as últimas movimentações registradas.

    Parâmetros:
        limit (int): Número máximo de registros (padrão: 10).

    Retorna:
        list: Tuplas com (data_hora, usuario_nome, codigo_barra,
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
          JOIN usuarios u
            ON l.usuario_id = u.id
          JOIN ferramentas f
            ON l.ferramenta_id = f.id
         ORDER BY l.data_hora DESC
         LIMIT ?
    """
    try:
        return executar_query(query, (limit,), fetch=True)
    except Exception as e:
        print(f"⚠️ Erro ao buscar movimentações: {e}")
        return []
