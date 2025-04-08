import os
import pandas as pd

def buscar_ferramenta_por_ip(ip_codigo: str) -> dict | None:
    """
    Busca na planilha 'Consulta Produtos IP.xlsx' os dados correspondentes ao código de IP informado.

    Args:
        ip_codigo (str): Código de referência a ser buscado (a busca é feita em caixa alta).

    Returns:
        dict: Dados do produto encontrados com as chaves "descricao", "codigo", "un_estoque", "tipo" e "classificacao".
        None: Caso a planilha não seja encontrada, ocorra erro na leitura ou nenhum resultado seja encontrado.
    """
    # Define o caminho até a planilha
    pasta_dados = os.path.join(os.path.dirname(__file__), 'dados')
    caminho_planilha = os.path.join(pasta_dados, "Consulta Produtos IP.xlsx")

    if not os.path.exists(caminho_planilha):
        print("⚠️ Planilha de consulta não encontrada.")
        return None

    try:
        df = pd.read_excel(caminho_planilha)
    except Exception as e:
        print(f"❌ Erro ao ler a planilha: {e}")
        return None

    # Realiza a busca filtrando o DataFrame pelo código de IP convertido para maiúsculas
    resultado = df[df['Ref. Sistema'] == ip_codigo.upper()]
    
    if not resultado.empty:
        info = resultado.iloc[0]
        return {
            "descricao": info.get("Descrição", ""),
            "codigo": info.get("Código", ""),
            "un_estoque": info.get("Un. Estoque", ""),
            "tipo": info.get("Tipo", ""),
            "classificacao": info.get("Classificação", ""),
            "consumivel": str(info.get("Consumível", "")).strip().upper()
        }
    else:
        return None
