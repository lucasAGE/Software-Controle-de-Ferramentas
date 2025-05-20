import sqlite3
from typing import List, Tuple
from database.config import DATABASE_CAMINHO


def executar_query(query: str,
                     params: Tuple = (),
                     fetch: bool = False,
                     fetch_one: bool = False):
    """
    Executa uma query no banco SQLite.

    Args:
        query (str): SQL a executar.
        params (tuple): Parâmetros para a query.
        fetch (bool): True para cursor.fetchall().
        fetch_one (bool): True para cursor.fetchone().

    Returns:
        Resultado da query ou None.
    """
    try:
        with sqlite3.connect(DATABASE_CAMINHO) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch_one:
                return cursor.fetchone()
            if fetch:
                return cursor.fetchall()
            conn.commit()
            return None
    except sqlite3.Error as e:
        print(f"❌ Erro ao executar query: {e}\n→ Query: {query}\n→ Params: {params}")
        return None


def buscar_estoque_ativo_usuario(rfid_usuario: str) -> List[Tuple[int, str, str, int]]:
    """
    Retorna o estoque ativo das ferramentas para o usuário via RFID.

    Saldo = SUM(CASE WHEN acao='RETIRADA' THEN quantidade
                     WHEN acao='DEVOLUCAO' THEN -quantidade ELSE 0 END)
    Args:
        rfid_usuario (str): Código RFID.

    Returns:
        Lista de (ferramenta_id, nome, codigo_barra, saldo) com saldo>0.
    """
    # Converte RFID em usuário_id
    usuario = executar_query(
        "SELECT id FROM usuarios WHERE rfid = ?",
        (rfid_usuario,),
        fetch_one=True
    )
    if not usuario:
        return []
    usuario_id = usuario[0]

    # Calcula saldo ativo por ferramenta
    sql = (
        "SELECT l.ferramenta_id, f.nome, f.codigo_barra, "
        "SUM(CASE WHEN l.acao = 'RETIRADA' THEN l.quantidade "
        "WHEN l.acao = 'DEVOLUCAO' THEN -l.quantidade ELSE 0 END) AS saldo "
        "FROM logs l "
        "JOIN ferramentas f ON l.ferramenta_id = f.id "
        "WHERE l.usuario_id = ? "
        "GROUP BY l.ferramenta_id "
        "HAVING saldo > 0"
    )
    resultados = executar_query(sql, (usuario_id,), fetch=True)
    return resultados or []
