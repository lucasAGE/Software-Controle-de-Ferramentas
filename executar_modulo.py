import sys
import subprocess

if len(sys.argv) < 2:
    print("❌ Uso: python executar_modulo.py pacote.nome_do_modulo")
    print("Exemplo: python executar_modulo.py database.database_backup")
    print("\n📦 Exemplos disponíveis:")

    print("""
# 📁 database
python executar_modulo.py database.__init__
python executar_modulo.py database.config
python executar_modulo.py database.database
python executar_modulo.py database.database_backup
python executar_modulo.py database.database_utils
python executar_modulo.py database.scheduler

# 📁 estoque
python executar_modulo.py estoque.__init__
python executar_modulo.py estoque.estoque

# 📁 experimental
python executar_modulo.py experimental.__init__
python executar_modulo.py experimental.clean
python executar_modulo.py experimental.test

# 📁 interface
python executar_modulo.py interface.interface_grafica
python executar_modulo.py interface.navegacao
python executar_modulo.py interface.painel
python executar_modulo.py interface.telalogin

# 📁 interface.telas
python executar_modulo.py telas.__init__
python executar_modulo.py telas.admin
python executar_modulo.py telas.cadastro
python executar_modulo.py telas.exportacao
python executar_modulo.py telas.movimentacao
python executar_modulo.py telas.tela_login_manual
python executar_modulo.py telas.tela_login_rfid

# 📁 utils
python executar_modulo.py utils.__init__
python executar_modulo.py utils.barcode_reader
python executar_modulo.py utils.consulta_planilha
python executar_modulo.py utils.rfid_reader

# 📄 Arquivos principais
python executar_modulo.py app
python executar_modulo.py main

          
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
