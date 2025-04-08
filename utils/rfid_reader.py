import time
from database.database_utils import executar_query

def ler_rfid() -> str | None:
    """
    Lê o código RFID utilizando a entrada padrão, como se o leitor
    estivesse se comportando como um teclado.
    
    O usuário deverá digitar (ou o leitor enviará automaticamente) o código
    e pressionar Enter.
    """
    try:
        print("Aguardando leitura do RFID... (Digite o código e pressione Enter)")
        rfid_code = input().strip()
        if rfid_code:
            print(f"RFID lido: {rfid_code}")
            return rfid_code
        else:
            print("Nenhum código RFID lido.")
            return None
    except Exception as e:
        print(f"Erro ao ler RFID: {e}")
        return None

def get_user_from_rfid() -> str | None:
    """
    Lê o RFID via entrada padrão e consulta diretamente o banco de dados.
    
    Retorna:
        str: Nome do usuário, se encontrado.
        None: Se não encontrado ou em caso de erro.
    """
    try:
        rfid_code = ler_rfid()
        if not rfid_code:
            print("⚠️ Nenhum código RFID lido.")
            return None

        query = "SELECT nome FROM usuarios WHERE rfid = ?"
        user = executar_query(query, (rfid_code,), fetch_one=True)

        if user:
            print(f"✅ Usuário encontrado: {user[0]}")
            return user[0]
        else:
            print("⚠️ Usuário não encontrado!")
            return None
    except Exception as e:
        print(f"❌ Erro ao processar leitura RFID: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Teste de leitura RFID iniciado...")
    usuario = get_user_from_rfid()
    if usuario:
        print(f"👤 Usuário autenticado: {usuario}")
    else:
        print("⚠️ Nenhum usuário encontrado.")
