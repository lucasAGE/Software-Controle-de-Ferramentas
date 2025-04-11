from database.database_utils import executar_query

def read_barcode():
    """
    Solicita ao usuário a leitura do código de barras.
    Retorna o código lido ou None se estiver vazio.
    """
    print("📡 Aguardando leitura do código de barras... (Escaneie agora)")
    barcode = input("Código de Barras: ").strip()
    if not barcode:
        print("⚠️ Nenhum código de barras lido.")
        return None
    return barcode

def search_item_by_barcode(barcode):
    """
    Busca no banco de dados o item correspondente ao código de barras informado.
    Retorna um dicionário com os dados do item ou None se não for encontrado.
    """
    query = "SELECT id, nome, estoque_almoxarifado FROM ferramentas WHERE codigo_barra = ?"
    resultado = executar_query(query, (barcode,), fetch=True)
    if resultado and resultado[0]:
        item_id, nome, estoque_almoxarifado = resultado[0]
        return {"id": item_id, "nome": nome, "estoque_almoxarifado": estoque_almoxarifado}
    return None

def get_item_from_barcode():
    """
    Orquestra a leitura e a busca do item a partir do código de barras.
    Retorna os dados do item (dicionário) ou None, caso não encontre.
    """
    try:
        barcode = read_barcode()
        if not barcode:
            return None

        item = search_item_by_barcode(barcode)
        if item:
            print(f"✅ Item encontrado: {item['nome']} (Estoque Almoxarifado disponível: {item['estoque_almoxarifado']})")
            return item
        else:
            print("⚠️ Código de barras não encontrado no banco de dados.")
            return None

    except KeyboardInterrupt:
        print("\n❌ Operação interrompida pelo usuário.")
        return None
    except Exception as e:
        print(f"❌ Erro ao processar código de barras: {e}")
        return None

if __name__ == '__main__':
    get_item_from_barcode()
