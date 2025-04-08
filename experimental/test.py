
import os
import pandas as pd
from database import config
from database.database_utils import executar_query
from database.database import criar_tabelas

def preparar_dados_teste():
    """
    Insere dados de teste nas tabelas 'usuarios' e 'maquinas'.
    Utiliza 'INSERT OR IGNORE' para evitar inserções duplicadas.
    """
    print("🧪 Inserindo dados de teste...")

    # Dados para a tabela 'usuarios'
    executar_query(
        "INSERT OR IGNORE INTO usuarios (nome, senha, rfid, tipo) VALUES (?, ?, ?, ?)",
        ("usuarioo", "senha", "0004254308", "operador")
    )
    executar_query(
        "INSERT OR IGNORE INTO usuarios (nome, senha, rfid, tipo) VALUES (?, ?, ?, ?)",
        ("administradorr", "senha", "0004279647", "admin")
    )

    

    # Dados para a tabela 'maquinas'
    executar_query(
        "INSERT OR IGNORE INTO maquinas (nome) VALUES (?)",
        ("VMC855",)
    )

    print("✅ Dados de teste inseridos com sucesso!")

def importar_ferramentas_da_planilha():
    """
    Lê a planilha 'Consulta Produtos IP.xlsx' (definida em config.PLANILHA_IP_CAMINHO)
    e insere cada linha na tabela 'ferramentas', mapeando:
      - codigo_barra  <- 'Ref. Sistema'
      - nome          <- 'Descrição'
      - quantidade    <- 0 (fixo)
      - consumivel    <- 'Consumível?' (padrão 'NÃO' se não encontrado)
    """
    print("🧪 Importando ferramentas da planilha...")

    planilha_caminho = config.PLANILHA_IP_CAMINHO
    if not os.path.exists(planilha_caminho):
        print(f"⚠️ Planilha não encontrada em: {planilha_caminho}")
        return

    try:
        df = pd.read_excel(planilha_caminho)
    except Exception as e:
        print(f"❌ Erro ao ler a planilha: {e}")
        return

    inseridos = 0
    for _, row in df.iterrows():
        ref_sistema = row.get('Ref. Sistema', '').strip()
        descricao = row.get('Descrição', '').strip()
        consumivel = str(row.get('Consumível?', 'NÃO')).strip().upper()

        if ref_sistema and descricao:
            executar_query(
                "INSERT OR IGNORE INTO ferramentas (nome, codigo_barra, quantidade, consumivel) VALUES (?, ?, ?, ?)",
                (descricao, ref_sistema, 0, consumivel)
            )
            inseridos += 1

    print(f"✅ Importação concluída! {inseridos} registros inseridos (ou ignorados se já existiam).")


def verificar_dados():
    """
    Verifica se os dados foram inseridos com sucesso, exibindo os registros
    das tabelas 'usuarios', 'ferramentas' e 'maquinas'.
    """
    tabelas = ['usuarios', 'ferramentas', 'maquinas']
    for tabela in tabelas:
        print(f"\n🔎 Verificando dados na tabela '{tabela}':")
        resultado = executar_query(f"SELECT * FROM {tabela}", fetch=True)
        if resultado:
            for linha in resultado:
                print(linha)
        else:
            print(f"Nenhum registro encontrado na tabela '{tabela}'.")

def main():
    # Cria as tabelas (se não existirem)
    criar_tabelas()

    # Insere dados de teste em outras tabelas
    preparar_dados_teste()

    # Importa dados de ferramentas a partir da planilha
    importar_ferramentas_da_planilha()

    

if __name__ == "__main__":
    main()
