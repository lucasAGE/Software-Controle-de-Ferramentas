import sys
import subprocess

if len(sys.argv) < 2:
    print("❌ Uso: python executar_modulo.py pacote.nome_do_modulo")
    print("Exemplo: python executar_modulo.py database.database_backup")
    print("\n📦 Exemplos disponíveis:")

    print("""
# 📁 Módulos da pasta database
python executar_modulo.py database.database
python executar_modulo.py database.database_utils
python executar_modulo.py database.database_backup
python executar_modulo.py database.scheduler
          
# 📁 Módulos da pasta interface
python executar_modulo.py interface.interface_grafica
python executar_modulo.py interface.navegacao
python executar_modulo.py interface.painel
python executar_modulo.py interface.telalogin

# 📁 Módulos da pasta experimental (scripts de teste e manutenção)
python executar_modulo.py experimental.test
python executar_modulo.py experimental.clean

# 📁 Módulos de utilitários (linha de comando)
python executar_modulo.py utils.barcode_reader
python executar_modulo.py utils.rfid_reader
python executar_modulo.py utils.consulta_planilha

# 📁 Módulos de utilitários (linha de comando)
python executar_modulo.py app
          
# ❗ Observação:
# Use sempre nomes no formato pacote.arquivo_sem_extensão
# Este script deve ser executado a partir da raiz do projeto
""")
    sys.exit(1)

modulo = sys.argv[1]

try:
    subprocess.run(["python", "-m", modulo], check=True)
except subprocess.CalledProcessError as e:
    print(f"❌ Erro ao executar o módulo '{modulo}': {e}")
