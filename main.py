import sys
import os

from database.database_utils import executar_query
from database.database import (
    registrar_movimentacao,
    buscar_ferramenta_por_codigo,
    criar_tabelas
)

# ----- Funções de Administração -----

def registrar_usuario(nome: str, senha: str, rfid: str, tipo: str) -> str:
    """
    Registra um novo usuário no sistema.

    Parâmetros:
        nome   (str): Nome do usuário.
        senha  (str): Senha (deve chegar já hash ou cifrada).
        rfid   (str): RFID do usuário.
        tipo   (str): Tipo do usuário ("admin", "operador", etc.).

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    try:
        nome = nome.strip()
        senha = senha.strip()
        rfid = rfid.strip()
        tipo = tipo.strip()

        if not (nome and senha and rfid and tipo):
            return "⚠️ Nome, Senha, RFID e Tipo são obrigatórios!"

        query = """
            INSERT INTO usuarios (nome, senha, rfid, tipo)
            VALUES (?, ?, ?, ?)
        """
        executar_query(query, (nome, senha, rfid, tipo))
        return f"✅ Usuário '{nome}' registrado com sucesso!"
    except Exception as e:
        return f"⚠️ Erro ao registrar usuário: {e}"


def registrar_ferramenta(
    nome: str,
    codigo_barra: str,
    estoque_almoxarifado: int,
    estoque_ativo: int,
    consumivel: str
) -> str:
    """
    Registra uma nova ferramenta no sistema.

    Parâmetros:
        nome                 (str): Nome da ferramenta.
        codigo_barra         (str): Código de barras único.
        estoque_almoxarifado (int): Quantidade inicial no almoxarifado.
        estoque_ativo        (int): Quantidade inicial em uso.
        consumivel           (str): "SIM" ou "NÃO".

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    try:
        nome = nome.strip()
        codigo_barra = codigo_barra.strip()

        if not nome or not codigo_barra or estoque_almoxarifado < 0:
            return ("⚠️ Nome, código de barras e quantidade válida "
                    "para o almoxarifado são obrigatórios!")

        # Normaliza estoque ativo
        if isinstance(estoque_ativo, str):
            estoque_ativo = estoque_ativo.strip()
            estoque_ativo = int(estoque_ativo) if estoque_ativo.isdigit() else 0

        consumivel = consumivel.strip().upper()
        if consumivel not in ("SIM", "NÃO"):
            return "⚠️ O campo Consumível deve ser 'SIM' ou 'NÃO'!"

        query = """
            INSERT INTO ferramentas
                (nome, codigo_barra, estoque_almoxarifado, estoque_ativo, consumivel)
            VALUES (?, ?, ?, ?, ?)
        """
        executar_query(
            query,
            (nome, codigo_barra, estoque_almoxarifado, estoque_ativo, consumivel)
        )
        return f"✅ Ferramenta '{nome}' registrada com sucesso!"
    except Exception as e:
        return f"⚠️ Erro ao registrar ferramenta: {e}"


def registrar_maquina(nome: str) -> str:
    """
    Registra uma nova máquina no sistema.

    Parâmetros:
        nome (str): Nome da máquina.

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    try:
        nome = nome.strip()
        if not nome:
            return "⚠️ O nome da máquina é obrigatório!"

        query = "INSERT INTO maquinas (nome) VALUES (?)"
        executar_query(query, (nome,))
        return f"✅ Máquina '{nome}' registrada com sucesso!"
    except Exception as e:
        return f"⚠️ Erro ao registrar máquina: {e}"


# ----- Funções de Movimentação -----

def retirar_ferramenta(rfid: str, codigo_barra: str, quantidade: int = 1) -> str:
    """
    Processa a retirada de uma ferramenta.
    """
    return realizar_movimentacao(rfid, codigo_barra, "RETIRADA", quantidade)


def devolver_ferramenta(rfid: str, codigo_barra: str, quantidade: int = 1) -> str:
    """
    Processa a devolução de uma ferramenta.
    """
    return realizar_movimentacao(rfid, codigo_barra, "DEVOLUCAO", quantidade)


def adicionar_ferramenta(rfid: str, codigo_barra: str, quantidade: int = 1) -> str:
    """
    Incrementa estoque e registra ação 'ADICAO'.
    """
    return realizar_movimentacao(rfid, codigo_barra, "ADICAO", quantidade)


def subtrair_ferramenta(rfid: str, codigo_barra: str, quantidade: int = 1) -> str:
    """
    Decrementa estoque e registra ação 'SUBTRACAO'.
    """
    return realizar_movimentacao(rfid, codigo_barra, "SUBTRACAO", quantidade)


def zerar_ferramenta(rfid: str, codigo_barra: str) -> str:
    """
    Zera o estoque almoxarifado e registra ação 'SUBTRACAO'
    com a quantidade total atual.
    """
    dados = buscar_ferramenta_por_codigo(codigo_barra)
    if not dados:
        return "⚠️ Ferramenta não encontrada!"

    quantidade = dados["estoque_almoxarifado"]
    if quantidade <= 0:
        return "⚠️ Estoque já está zerado!"

    return realizar_movimentacao(rfid, codigo_barra, "SUBTRACAO", quantidade)


def realizar_movimentacao(
    rfid: str,
    codigo_barra: str,
    acao: str,
    quantidade: int = 1,
    motivo: str = None,
    operacoes: int = None,
    avaliacao: int = None
) -> str:
    """
    Processa RETIRADA, DEVOLUCAO, CONSUMO, ADICAO e SUBTRACAO,
    delegando ao registrar_movimentacao e retornando a mensagem.
    """
    try:
        rfid = rfid.strip()
        codigo_barra = codigo_barra.strip()

        result = executar_query(
            "SELECT id FROM usuarios WHERE rfid = ?",
            (rfid,),
            fetch=True
        )
        if not result:
            return "⚠️ Usuário não encontrado!"
        usuario_id = result[0][0]

        resp = registrar_movimentacao(
            usuario_id,
            codigo_barra,
            acao,
            quantidade,
            motivo,
            operacoes,
            avaliacao
        )
        return resp.get("mensagem") if isinstance(resp, dict) else resp
    except Exception as e:
        return f"⚠️ Erro ao realizar movimentação: {e}"


# ----- Inicialização -----

def main():
    """
    Inicializa o banco (backup e tabelas) e inicia a interface gráfica.
    """
    try:
        from database.database_backup import verificar_backup
        from database import config

        config.DATABASE_CAMINHO = verificar_backup()

        if not os.path.exists(config.DATABASE_CAMINHO):
            print("📌 Banco de dados não encontrado. Criando novo...")
            criar_tabelas()
        else:
            print(f"✅ Banco pronto: {config.DATABASE_CAMINHO}")
    except Exception as e:
        print(f"⚠️ Erro na inicialização do banco: {e}")

    from PyQt5.QtWidgets import QApplication
    from interface.navegacao import Navegacao

    app = QApplication.instance() or QApplication(sys.argv)
    janela = Navegacao()
    janela.setWindowTitle("Controle de Ferramentas")
    janela.resize(800, 600)
    janela.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
