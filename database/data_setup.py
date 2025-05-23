#!/usr/bin/env python3
import sys
import os
import logging
from typing import Optional

import pandas as pd
from database.config import PLANILHA_IP_CAMINHO
from database.database import criar_tabelas
from database.database_utils import executar_query

# Configura logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def resource_path(rel_path: str) -> str:
    """
    Retorna o caminho absoluto para um recurso, seja em dev ou no bundle PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, rel_path)


def setup_database(include_test_data: bool = False) -> None:
    """
    Cria o schema do banco e, se desejado, popula dados de teste e importa planilha.
    :param include_test_data: insere usuários e máquinas de teste se True
    """
    # Cria esquema (tabelas)
    criar_tabelas()
    logger.info("Banco de dados inicializado.")

    # Insere dados de teste
    if include_test_data:
        seed_test_data()

    # Importa ferramentas da planilha
    import_tools_from_excel()


def seed_test_data() -> None:
    """
    Insere usuários e máquinas de teste com INSERT OR IGNORE.
    """
    logger.info("Inserindo dados de teste…")
    testers = [
        ("usuarioo", "senha", "0004254308", "operador"),
        ("administradorr", "senha", "0004279647", "admin"),
    ]
    for nome, senha, rfid, tipo in testers:
        executar_query(
            "INSERT OR IGNORE INTO usuarios (nome, senha, rfid, tipo) VALUES (?, ?, ?, ?)",
            (nome, senha, rfid, tipo)
        )
    executar_query(
        "INSERT OR IGNORE INTO maquinas (nome) VALUES (?)",
        ("VMC855",)
    )
    logger.info("Dados de teste inseridos com sucesso.")


def import_tools_from_excel() -> None:
    """
    Lê a planilha configurada em config.PLANILHA_IP_CAMINHO e importa ferramentas.
    """
    logger.info("Importando ferramentas da planilha…")
    caminho = resource_path(PLANILHA_IP_CAMINHO)
    if not os.path.exists(caminho):
        logger.error("Planilha não encontrada em: %s", caminho)
        return

    try:
        df = pd.read_excel(caminho)
    except FileNotFoundError:
        logger.error("Arquivo não existe: %s", caminho)
        return
    except ValueError as e:
        logger.error("Formato inválido na planilha: %s", e)
        return
    except Exception:
        logger.exception("Falha ao ler a planilha")
        return

    if df.empty:
        logger.warning("Planilha sem registros.")
        return

    col_consumivel: Optional[str] = next(
        (c for c in ("Consumível?", "Consumível") if c in df.columns),
        None
    )

    inseridos = 0
    for row in df.itertuples(index=False):
        ref_sistema = str(getattr(row, 'Ref. Sistema', '')).strip()
        descricao = str(getattr(row, 'Descrição', '')).strip()
        raw = getattr(row, col_consumivel) if col_consumivel else "NÃO"
        consumivel_flag = 1 if str(raw).strip().upper().startswith("S") else 0

        if not (ref_sistema and descricao):
            continue

        executar_query(
            """
            INSERT OR IGNORE INTO ferramentas
              (nome, codigo_barra, estoque_almoxarifado, consumivel)
            VALUES (?, ?, ?, ?)
            """,
            (descricao, ref_sistema, 0, consumivel_flag)
        )
        inseridos += 1

    logger.info("Importação concluída: %d itens processados.", inseridos)


if __name__ == "__main__":
    # Testa rotinas de setup
    setup_database(include_test_data=True)
