#!/usr/bin/env python3
"""
utils/movimentacoes.py

Módulo responsável pela lógica de movimentações de ferramentas:
- retirada
- devolução
- adição
- subtração
- zeragem de estoque

Remove dependência circular movendo lógica de movimentação para este serviço.
"""
import logging
from typing import Optional, Dict

from database.database_utils import executar_query
from database.database import registrar_movimentacao as db_registrar_movimentacao, buscar_ferramenta_por_codigo

# Configuração do logger
logger = logging.getLogger(__name__)


def realizar_movimentacao(
    rfid: str,
    codigo_barra: str,
    acao: str,
    quantidade: int = 1,
    motivo: Optional[str] = None,
    operacoes: Optional[int] = None,
    avaliacao: Optional[int] = None
) -> Dict[str, object]:
    """
    Lógica central de movimentações (retirada, devolução, consumo, etc.).

    :param rfid: código RFID do usuário
    :param codigo_barra: código de barras da ferramenta
    :param acao: tipo de movimentação ('RETIRADA','DEVOLUCAO','ADICAO','SUBTRACAO')
    :param quantidade: quantidade a movimentar
    :param motivo: motivo para consumo
    :param operacoes: número de operações extras em consumo
    :param avaliacao: nota de avaliação em consumo
    :return: dict com chaves 'status' (bool) e 'mensagem' (str)
    """
    try:
        rfid_limpo = rfid.strip()
        codigo_limpo = codigo_barra.strip()
        # Busca ID do usuário a partir do RFID
        result = executar_query(
            "SELECT id FROM usuarios WHERE rfid = ?", (rfid_limpo,), fetch=True
        )
        if not result:
            return {"status": False, "mensagem": "⚠️ Usuário não encontrado!"}
        usuario_id = result[0][0]
        # Chama função de banco para registrar movimentação
        resp = db_registrar_movimentacao(
            usuario_id,
            codigo_limpo,
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


def retirar_ferramenta(rfid: str, codigo_barra: str, quantidade: int = 1) -> Dict[str, object]:
    """Retira uma ferramenta do estoque ativo."""
    return realizar_movimentacao(rfid, codigo_barra, "RETIRADA", quantidade)


def devolver_ferramenta(rfid: str, codigo_barra: str, quantidade: int = 1) -> Dict[str, object]:
    """Devolve uma ferramenta ao estoque ativo."""
    return realizar_movimentacao(rfid, codigo_barra, "DEVOLUCAO", quantidade)


def adicionar_ferramenta(rfid: str, codigo_barra: str, quantidade: int = 1) -> Dict[str, object]:
    """Adiciona quantidade ao estoque de almoxarifado."""
    return realizar_movimentacao(rfid, codigo_barra, "ADICAO", quantidade)


def subtrair_ferramenta(rfid: str, codigo_barra: str, quantidade: int = 1) -> Dict[str, object]:
    """Subtrai quantidade do estoque de almoxarifado."""
    return realizar_movimentacao(rfid, codigo_barra, "SUBTRACAO", quantidade)


def zerar_ferramenta(rfid: str, codigo_barra: str) -> Dict[str, object]:
    """
    Zera todo o estoque ativo de uma ferramenta marcando subtração do total armazenado.
    """
    # Busca dados da ferramenta para obter estoque atual
    dados = buscar_ferramenta_por_codigo(codigo_barra)
    if not dados:
        return {"status": False, "mensagem": "⚠️ Ferramenta não encontrada!"}
    qtd = dados.get("estoque_almoxarifado", 0)
    if qtd <= 0:
        return {"status": False, "mensagem": "⚠️ Estoque já está zerado!"}
    return realizar_movimentacao(rfid, codigo_barra, "SUBTRACAO", qtd)
