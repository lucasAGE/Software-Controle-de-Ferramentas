import os
import logging
from typing import Optional

import pandas as pd
from database.config import PLANILHA_IP_CAMINHO
from database.database_utils import executar_query

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def preparar_dados_teste() -> None:
    """Insere usuários e máquinas de teste no banco."""
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

def importar_ferramentas_da_planilha() -> None:
    """Lê planilha e importa ferramentas para o banco."""
    logger.info("Importando ferramentas da planilha…")
    caminho = PLANILHA_IP_CAMINHO
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

    col_consumivel = next((c for c in ("Consumível?", "Consumível") if c in df.columns), None)
    inseridos = 0
    for row in df.itertuples(index=False):
        ref_sistema = str(getattr(row, 'Ref. Sistema', '')).strip()
        descricao   = str(getattr(row, 'Descrição', '')).strip()
        consumivel_raw = getattr(row, col_consumivel) if col_consumivel else "NÃO"
        consumivel = str(consumivel_raw).strip().upper()
        consumivel_flag = 1 if consumivel.startswith("S") else 0

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
    preparar_dados_teste()
    importar_ferramentas_da_planilha()
