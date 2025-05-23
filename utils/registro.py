#!/usr/bin/env python3
"""
utils/registration.py

Módulo para registro de usuários, ferramentas e máquinas.
Remove dependência de 'main' e evita import circular.
"""
import logging
from typing import Tuple

from database.database_utils import executar_query

# Configuração do logger
erlogger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def registrar_usuario(nome: str, senha: str, rfid: str, tipo: str) -> str:
    """
    Registra um novo usuário no sistema.

    :param nome: nome completo do usuário
    :param senha: senha do usuário
    :param rfid: código RFID único
    :param tipo: tipo de usuário ('operador' ou 'admin')
    :return: mensagem de sucesso ou erro
    """
    try:
        nome_valido, senha_valida, rfid_valido, tipo_valido = (
            campo.strip() for campo in (nome, senha, rfid, tipo)
        )
        if not (nome_valido and senha_valida and rfid_valido and tipo_valido):
            return "⚠️ Nome, Senha, RFID e Tipo são obrigatórios!"
        query = (
            "INSERT INTO usuarios (nome, senha, rfid, tipo)"
            " VALUES (?, ?, ?, ?)"
        )
        executar_query(query, (nome_valido, senha_valida, rfid_valido, tipo_valido))
        return f"✅ Usuário '{nome_valido}' registrado com sucesso!"
    except Exception as e:
        erlogger.exception("Erro ao registrar usuário")
        return f"⚠️ Erro ao registrar usuário: {e}"


def registrar_ferramenta(
    nome: str,
    codigo_barra: str,
    estoque_almoxarifado: int,
    consumivel: str
) -> str:
    """
    Registra uma nova ferramenta no sistema.

    :param nome: descrição da ferramenta
    :param codigo_barra: código de barras único
    :param estoque_almoxarifado: quantidade inicial em almoxarifado
    :param consumivel: 'SIM' ou 'NÃO'
    :return: mensagem de sucesso ou erro
    """
    try:
        nome_valido = nome.strip()
        codigo_valido = codigo_barra.strip()
        if not nome_valido or not codigo_valido or estoque_almoxarifado < 0:
            return "⚠️ Nome, código de barras e quantidade válida são obrigatórios!"
        consumivel_flag = consumivel.strip().upper()
        if consumivel_flag not in ("SIM", "NÃO"):
            return "⚠️ O campo Consumível deve ser 'SIM' ou 'NÃO'!"
        query = (
            "INSERT INTO ferramentas"
            " (nome, codigo_barra, estoque_almoxarifado, consumivel)"
            " VALUES (?, ?, ?, ?)"
        )
        executar_query(query, (nome_valido, codigo_valido, estoque_almoxarifado, consumivel_flag))
        return f"✅ Ferramenta '{nome_valido}' registrada com sucesso!"
    except Exception as e:
        erlogger.exception("Erro ao registrar ferramenta")
        return f"⚠️ Erro ao registrar ferramenta: {e}"


def registrar_maquina(nome: str) -> str:
    """
    Registra uma nova máquina no sistema.

    :param nome: nome da máquina
    :return: mensagem de sucesso ou erro
    """
    try:
        nome_valido = nome.strip()
        if not nome_valido:
            return "⚠️ O nome da máquina é obrigatório!"
        query = "INSERT INTO maquinas (nome) VALUES (?)"
        executar_query(query, (nome_valido,))
        return f"✅ Máquina '{nome_valido}' registrada com sucesso!"
    except Exception as e:
        erlogger.exception("Erro ao registrar máquina")
        return f"⚠️ Erro ao registrar máquina: {e}"
