import sys
import os
from database.database_utils import executar_query
from database.database import registrar_movimentacao, buscar_ferramenta_por_codigo, criar_tabelas

# ----- Funções de Administração -----
def registrar_usuario(nome, senha, rfid, tipo):
    """
    Registra um novo usuário no sistema.

    Parâmetros:
        nome (str): Nome do usuário.
        senha (str): Senha do usuário já transformada (por exemplo, hash).
        rfid (str): RFID do usuário.
        tipo (str): Tipo do usuário (ex: "admin", "usuario", etc.).

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    try:
        # Remove espaços em branco dos dados
        nome = nome.strip()
        senha = senha.strip()
        rfid = rfid.strip()
        tipo = tipo.strip()

        # Validação dos campos obrigatórios
        if not nome or not senha or not rfid or not tipo:
            return "⚠️ Nome, Senha, RFID e Tipo são obrigatórios!"

        query = "INSERT INTO usuarios (nome, senha, rfid, tipo) VALUES (?, ?, ?, ?)"
        executar_query(query, (nome, senha, rfid, tipo))
        return f"✅ Usuário {nome} registrado com sucesso!"
    except Exception as e:
        return f"⚠️ Erro ao registrar usuário: {e}"



def registrar_ferramenta(nome, codigo_barra, estoque_almoxarifado, estoque_ativo, consumivel):
    """
    Registra uma nova ferramenta no sistema.

    Parâmetros:
        nome (str): Nome da ferramenta.
        codigo_barra (str): Código de barras da ferramenta.
        estoque_almoxarifado (int): Quantidade inicial no almoxarifado.
        estoque_ativo (int ou str): Quantidade do estoque ativo.
        consumivel (str): Indica se a ferramenta é consumível ("SIM" ou "NÃO").

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    try:
        # Remove espaços em branco
        nome = nome.strip()
        codigo_barra = codigo_barra.strip()
        
        # Validação dos campos obrigatórios
        if not nome or not codigo_barra or estoque_almoxarifado < 0:
            return "⚠️ Nome, código de barras e uma quantidade válida para o almoxarifado são obrigatórios!"

        # Conversão e validação do estoque ativo
        try:
            if isinstance(estoque_ativo, str) and estoque_ativo.strip():
                estoque_ativo = int(estoque_ativo.strip())
            elif not isinstance(estoque_ativo, int):
                estoque_ativo = 0
        except ValueError:
            return "⚠️ Estoque ativo deve ser um número inteiro!"

        # Tratar o campo consumível
        consumivel = consumivel.strip().upper()  # Converte para maiúsculas para manter consistência
        if consumivel not in ["SIM", "NÃO"]:
            return "⚠️ O campo Consumível deve ser 'SIM' ou 'NÃO'!"

        query = """
            INSERT INTO ferramentas (nome, codigo_barra, estoque_almoxarifado, estoque_ativo, consumivel)
            VALUES (?, ?, ?, ?, ?)
        """
        executar_query(query, (nome, codigo_barra, estoque_almoxarifado, estoque_ativo, consumivel))
        return f"✅ Ferramenta {nome} registrada com sucesso!"
    except Exception as e:
        return f"⚠️ Erro ao registrar ferramenta: {e}"



def registrar_maquina(nome):
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
    Zera a quantidade do estoque almoxarifado de uma ferramenta, efetivamente dando baixa nela.

    Parâmetros:
        codigo_barra (str): Código de barras da ferramenta.

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    try:
        codigo_barra = codigo_barra.strip()
        if not codigo_barra:
            return "⚠️ Código de barra é obrigatório!"
        query = "UPDATE ferramentas SET estoque_almoxarifado = 0 WHERE codigo_barra = ?"
        executar_query(query, (codigo_barra,))
        return "✅ Ferramenta dada baixa com sucesso!"
    except Exception as e:
        return f"⚠️ Erro ao dar baixa na ferramenta: {e}"


def dar_alta_ferramenta(codigo_barra, quantidade):
    """
    Incrementa a quantidade do estoque almoxarifado de uma ferramenta.

    Parâmetros:
        codigo_barra (str): Código de barras da ferramenta.
        quantidade (int): Quantidade a ser adicionada ao almoxarifado.

    Retorna:
        str: Mensagem de sucesso ou erro.
    """
    try:
        codigo_barra = codigo_barra.strip()
        if not codigo_barra or quantidade <= 0:
            return "⚠️ Código de barra e quantidade válida são obrigatórios!"
        query = "UPDATE ferramentas SET estoque_almoxarifado = estoque_almoxarifado + ? WHERE codigo_barra = ?"
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
