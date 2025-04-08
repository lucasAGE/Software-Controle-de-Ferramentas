import sys
import os
from database.database_utils import executar_query
from database.database import registrar_movimentacao, buscar_ferramenta_por_codigo, criar_tabelas

# ----- Funções de Administração -----
def registrar_usuario(nome, rfid):
    """
    Registra um novo usuário no sistema.

    Parâmetros:
        nome (str): Nome do usuário.
        rfid (str): RFID do usuário.

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    try:
        nome, rfid = nome.strip(), rfid.strip()
        if not nome or not rfid:
            return "⚠️ Nome e RFID são obrigatórios!"
        query = "INSERT INTO usuarios (nome, rfid) VALUES (?, ?)"
        executar_query(query, (nome, rfid))
        return f"✅ Usuário {nome} registrado com sucesso!"
    except Exception as e:
        return f"⚠️ Erro ao registrar usuário: {e}"


def registrar_ferramenta(nome, codigo_barra, quantidade):
    """
    Registra uma nova ferramenta no sistema.

    Parâmetros:
        nome (str): Nome da ferramenta.
        codigo_barra (str): Código de barras da ferramenta.
        quantidade (int): Quantidade inicial da ferramenta.

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    try:
        nome, codigo_barra = nome.strip(), codigo_barra.strip()
        if not nome or not codigo_barra or quantidade < 0:
            return "⚠️ Nome, código de barra e quantidade válida são obrigatórios!"
        query = "INSERT INTO ferramentas (nome, codigo_barra, quantidade) VALUES (?, ?, ?)"
        executar_query(query, (nome, codigo_barra, quantidade))
        return f"✅ Ferramenta {nome} registrada com sucesso!"
    except Exception as e:
        return f"⚠️ Erro ao registrar ferramenta: {e}"


def registrar_maquina(nome, localizacao):
    """
    Registra uma nova máquina no sistema.

    Parâmetros:
        nome (str): Nome da máquina.
        localizacao (str): Localização da máquina.

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    try:
        nome, localizacao = nome.strip(), localizacao.strip()
        if not nome or not localizacao:
            return "⚠️ Nome e localização são obrigatórios!"
        query = "INSERT INTO maquinas (nome, localizacao) VALUES (?, ?)"
        executar_query(query, (nome, localizacao))
        return f"✅ Máquina {nome} registrada com sucesso!"
    except Exception as e:
        return f"⚠️ Erro ao registrar máquina: {e}"


# ----- Funções de Movimentação -----
def retirar_ferramenta(rfid, codigo_barra, quantidade=1):
    """
    Processa a retirada de uma ferramenta do estoque.

    Parâmetros:
        rfid (str): RFID do usuário.
        codigo_barra (str): Código de barras da ferramenta.
        quantidade (int, opcional): Quantidade a retirar. Padrão é 1.

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    return realizar_movimentacao(rfid, codigo_barra, "RETIRADA", quantidade)


def devolver_ferramenta(rfid, codigo_barra, quantidade=1):
    """
    Processa a devolução de uma ferramenta ao estoque.

    Parâmetros:
        rfid (str): RFID do usuário.
        codigo_barra (str): Código de barras da ferramenta.
        quantidade (int, opcional): Quantidade a devolver. Padrão é 1.

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    return realizar_movimentacao(rfid, codigo_barra, "DEVOLUCAO", quantidade)


def dar_baixa_ferramenta(codigo_barra):
    """
    Zera a quantidade de uma ferramenta, efetivamente dando baixa nela.

    Parâmetros:
        codigo_barra (str): Código de barras da ferramenta.

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    try:
        codigo_barra = codigo_barra.strip()
        if not codigo_barra:
            return "⚠️ Código de barra é obrigatório!"
        query = "UPDATE ferramentas SET quantidade = 0 WHERE codigo_barra = ?"
        executar_query(query, (codigo_barra,))
        return "✅ Ferramenta dada baixa com sucesso!"
    except Exception as e:
        return f"⚠️ Erro ao dar baixa na ferramenta: {e}"


def dar_alta_ferramenta(codigo_barra, quantidade):
    """
    Incrementa a quantidade de uma ferramenta no estoque.

    Parâmetros:
        codigo_barra (str): Código de barras da ferramenta.
        quantidade (int): Quantidade a ser adicionada.

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    try:
        codigo_barra = codigo_barra.strip()
        if not codigo_barra or quantidade <= 0:
            return "⚠️ Código de barra e quantidade válida são obrigatórios!"
        query = "UPDATE ferramentas SET quantidade = quantidade + ? WHERE codigo_barra = ?"
        executar_query(query, (quantidade, codigo_barra))
        return f"✅ Ferramenta {codigo_barra} atualizada com sucesso!"
    except Exception as e:
        return f"⚠️ Erro ao dar alta na ferramenta: {e}"


def realizar_movimentacao(rfid, codigo_barra, acao, quantidade=1, motivo=None, operacoes=None, avaliacao=None):
    """
    Processa a retirada, devolução ou consumo de uma ferramenta no banco de dados.

    Parâmetros:
        rfid (str): RFID do usuário.
        codigo_barra (str): Código de barras da ferramenta.
        acao (str): Ação a ser realizada ('RETIRADA', 'DEVOLUCAO' ou 'CONSUMO').
        quantidade (int, opcional): Quantidade da movimentação. Padrão é 1.
        motivo (str, opcional): Motivo do consumo (obrigatório para 'CONSUMO').
        operacoes (int, opcional): Número de operações realizadas (para 'CONSUMO').
        avaliacao (int, opcional): Nota de avaliação (1-5) quanto à qualidade/durabilidade (para 'CONSUMO').

    Retorna:
        dict ou str: Mensagem de sucesso ou erro.
    """
    try:
        rfid, codigo_barra = rfid.strip(), codigo_barra.strip()

        # Buscar ID do usuário
        query = "SELECT id FROM usuarios WHERE rfid = ?"
        usuario = executar_query(query, (rfid,), fetch=True)
        if not usuario:
            return "⚠️ Usuário não encontrado!"
        usuario_id = usuario[0][0]

        # Processa a movimentação utilizando a função centralizada do database.py,
        # repassando os dados extras caso a ação seja CONSUMO.
        resultado = registrar_movimentacao(usuario_id, codigo_barra, acao, quantidade, motivo, operacoes, avaliacao)
        return resultado
    except Exception as e:
        return f"⚠️ Erro ao realizar movimentação: {e}"


# ----- Inicialização -----
def main():
    """
    Função principal que inicializa o banco de dados e lança a interface gráfica.
    
    Atualiza o caminho do banco para o backup do dia, cria as tabelas, se necessário,
    e inicia o QApplication para exibir a interface.
    """
    try:
        from database.database import criar_tabelas
        from database.database_backup import verificar_backup
        from database import config

        # Atualiza o caminho do banco para o backup do dia
        config.DATABASE_CAMINHO = verificar_backup()

        if not os.path.exists(config.DATABASE_CAMINHO):
            print("📌 Banco de dados não encontrado. Criando novo...")
            criar_tabelas()
        else:
            print(f"✅ Banco de dados pronto para uso: {config.DATABASE_CAMINHO}")
    except Exception as e:
        print(f"⚠️ Erro na inicialização do banco de dados: {e}")

    # Inicializa o QApplication garantindo que não haja múltiplas instâncias
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    # Cria e exibe a janela principal (navegação entre telas)
    from interface.navegacao import Navegacao
    janela = Navegacao()
    janela.setWindowTitle("Controle de Ferramentas")
    janela.resize(800, 600)
    janela.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
