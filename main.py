#!/usr/bin/env python3
"""
main.py

Inicialização do banco de dados (backup, agendamento, esquema e dados iniciais)
 e execução da interface gráfica do Sistema de Controle de Ferramentas.
"""

import sys
import os
import logging
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
from database.initial_data import importar_ferramentas_da_planilha, preparar_dados_teste


# Configuração básica de logs
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)


# ----- Funções de Administração -----

def registrar_usuario(nome: str, senha: str, rfid: str, tipo: str) -> str:
    """
    Registra um novo usuário no sistema.
    """
    try:
        nome, senha, rfid, tipo = (campo.strip() for campo in (nome, senha, rfid, tipo))
        if not (nome and senha and rfid and tipo):
            return "⚠️ Nome, Senha, RFID e Tipo são obrigatórios!"
        query = (
            "INSERT INTO usuarios (nome, senha, rfid, tipo)"
            " VALUES (?, ?, ?, ?)"
        )
        executar_query(query, (nome, senha, rfid, tipo))
        return f"✅ Usuário '{nome}' registrado com sucesso!"
    except Exception as e:
        logger.exception("Erro ao registrar usuário")
        return f"⚠️ Erro ao registrar usuário: {e}"


def registrar_ferramenta(
    nome: str,
    codigo_barra: str,
    estoque_almoxarifado: int,
    consumivel: str
) -> str:
    """
    Registra uma nova ferramenta no sistema.
    """
    try:
        nome, codigo = nome.strip(), codigo_barra.strip()
        if not nome or not codigo or estoque_almoxarifado < 0:
            return ("⚠️ Nome, código de barras e quantidade válida para o almoxarifado são obrigatórios!")
        consumivel = consumivel.strip().upper()
        if consumivel not in ("SIM", "NÃO"):
            return "⚠️ O campo Consumível deve ser 'SIM' ou 'NÃO'!"

        query = (
            "INSERT INTO ferramentas"
            " (nome, codigo_barra, estoque_almoxarifado, consumivel)"
            " VALUES (?, ?, ?, ?)"
        )
        executar_query(query, (nome, codigo, estoque_almoxarifado, consumivel))
        return f"✅ Ferramenta '{nome}' registrada com sucesso!"
    except Exception as e:
        logger.exception("Erro ao registrar ferramenta")
        return f"⚠️ Erro ao registrar ferramenta: {e}"


def registrar_maquina(nome: str) -> str:
    """
    Registra uma nova máquina no sistema.
    """
    try:
        nome = nome.strip()
        if not nome:
            return "⚠️ O nome da máquina é obrigatório!"
        query = "INSERT INTO maquinas (nome) VALUES (?)"
        executar_query(query, (nome,))
        return f"✅ Máquina '{nome}' registrada com sucesso!"
    except Exception as e:
        logger.exception("Erro ao registrar máquina")
        return f"⚠️ Erro ao registrar máquina: {e}"


# ----- Funções de Movimentação -----

def realizar_movimentacao(
    rfid: str,
    codigo_barra: str,
    acao: str,
    quantidade: int = 1,
    motivo: Optional[str] = None,
    operacoes: Optional[int] = None,
    avaliacao: Optional[int] = None
) -> dict:
    """
    Lógica central de movimentações (retirada, devolução, consumo, etc.).
    """
    try:
        rfid, codigo_barra = rfid.strip(), codigo_barra.strip()
        # Busca ID do usuário
        result = executar_query(
            "SELECT id FROM usuarios WHERE rfid = ?",
            (rfid,),
            fetch=True
        )
        if not result:
            return {"status": False, "mensagem": "⚠️ Usuário não encontrado!"}
        usuario_id = result[0][0]

        resp = db_registrar_movimentacao(
            usuario_id,
            codigo_barra,
            acao,
            quantidade,
            motivo,
            operacoes,
            avaliacao
        )
        return resp
    except Exception as e:
        logger.exception("Erro ao realizar movimentação")
        return {"status": False, "mensagem": f"⚠️ Erro ao realizar movimentação: {e}"}


def retirar_ferramenta(rfid: str, codigo_barra: str, quantidade: int = 1) -> dict:
    return realizar_movimentacao(rfid, codigo_barra, "RETIRADA", quantidade)


def devolver_ferramenta(rfid: str, codigo_barra: str, quantidade: int = 1) -> dict:
    return realizar_movimentacao(rfid, codigo_barra, "DEVOLUCAO", quantidade)


def adicionar_ferramenta(rfid: str, codigo_barra: str, quantidade: int = 1) -> dict:
    return realizar_movimentacao(rfid, codigo_barra, "ADICAO", quantidade)


def subtrair_ferramenta(rfid: str, codigo_barra: str, quantidade: int = 1) -> dict:
    return realizar_movimentacao(rfid, codigo_barra, "SUBTRACAO", quantidade)


def zerar_ferramenta(rfid: str, codigo_barra: str) -> dict:
    dados = buscar_ferramenta_por_codigo(codigo_barra)
    if not dados:
        return {"status": False, "mensagem": "⚠️ Ferramenta não encontrada!"}
    qtd = dados["estoque_almoxarifado"]
    if qtd <= 0:
        return {"status": False, "mensagem": "⚠️ Estoque já está zerado!"}
    return realizar_movimentacao(rfid, codigo_barra, "SUBTRACAO", qtd)


# ----- Inicialização do Banco e Interface -----

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
            importar_ferramentas_da_planilha()
            preparar_dados_teste()
        else:
            logger.info("Banco pronto em %s", config.DATABASE_CAMINHO)
    except Exception:
        logger.exception("Falha na inicialização do banco")


def main() -> int:
    """
    Ponto de entrada: prepara banco e executa a interface Qt.
    """
    init_database()

    from interface.navegacao import Navegacao

    app = QApplication.instance() or QApplication(sys.argv)
    janela = Navegacao()
    janela.setWindowTitle("Controle de Ferramentas")
    janela.resize(800, 600)
    janela.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
