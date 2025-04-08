import sqlite3
from database.config import DATABASE_CAMINHO

def executar_query(query: str, params: tuple = None, fetch: bool = False, fetch_one: bool = False):
    """
    Executa uma query no banco de dados SQLite.

    Args:
        query (str): A query SQL a ser executada.
        params (tuple, optional): Parâmetros para a query. Defaults to ().
        fetch (bool, optional): Se True, retorna todos os resultados (fetchall).
        fetch_one (bool, optional): Se True, retorna apenas o primeiro resultado (fetchone).

    Returns:
        O resultado da query, ou None se não houver resultado ou ocorrer erro.
    """
    params = params or ()
    try:
        with sqlite3.connect(DATABASE_CAMINHO) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = None

            return result

    except sqlite3.Error as e:
        print(f"❌ Erro ao executar query: {e}\n→ Query: {query}")
        return None
