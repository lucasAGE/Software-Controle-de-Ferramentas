#!/usr/bin/env python3
"""
main.py

Inicialização do banco de dados (backup, agendamento, esquema e dados iniciais)
 e execução da interface gráfica do Sistema de Controle de Ferramentas.
"""

import sys
import os
import logging
import argparse
from typing import Optional

from PyQt5.QtWidgets import QApplication

import database.config as config
from database.database_utils import executar_query
from database.database import (
    criar_tabelas,
    registrar_movimentacao as db_registrar_movimentacao,
    buscar_ferramenta_por_codigo
)
from database.database_backup import verificar_backup
from database.scheduler import iniciar_agendador_em_thread
from database.data_setup import seed_test_data, import_tools_from_excel
from interface.navegacao import Navegacao


from utils.movimentacoes import realizar_movimentacao
from utils.movimentacoes import retirar_ferramenta
from utils.movimentacoes import devolver_ferramenta
from utils.movimentacoes import adicionar_ferramenta
from utils.movimentacoes import subtrair_ferramenta
from utils.movimentacoes import zerar_ferramenta


# Configuração básica de logs
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)


# ----- Inicialização do Banco -----

def init_database() -> None:
    """
    1) Recupera/cria backup do turno atual.
    2) Inicia o agendador de backups.
    3) Se for primeira execução, cria esquema e importa dados iniciais.
    """
    base_db = config.DATABASE_CAMINHO
    try:
        novo_path = verificar_backup()
        config.DATABASE_CAMINHO = novo_path
        iniciar_agendador_em_thread()
        if not os.path.exists(base_db):
            logger.info("Primeiro uso: criando esquema e importando dados iniciais…")
            criar_tabelas()
            import_tools_from_excel()
            seed_test_data()
        else:
            logger.info("Banco pronto em %s", config.DATABASE_CAMINHO)
    except Exception:
        logger.exception("Falha na inicialização do banco")

# ----- Ponto de Entrada -----

def main() -> int:
    """
    Ponto de entrada: inicializa banco e executa a interface Qt.
    Use o flag --setup para inserir dados de teste e importar planilha apenas na primeira execução.
    """
    parser = argparse.ArgumentParser(description="Controle de Ferramentas")
    parser.add_argument(
        '--setup', action='store_true',
        help='Inserir dados de teste e importar dados da planilha'
    )
    args = parser.parse_args()

    init_database()
    if args.setup:
        seed_test_data()
        import_tools_from_excel()

    app = QApplication.instance() or QApplication(sys.argv)
    janela = Navegacao()
    janela.setWindowTitle("Controle de Ferramentas")
    janela.resize(800, 600)
    janela.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
