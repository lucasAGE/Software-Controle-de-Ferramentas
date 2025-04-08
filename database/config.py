import os


# Obtém o diretório APPDATA ou utiliza o diretório home como fallback
APPDATA = os.getenv("APPDATA") or os.path.expanduser("~")

# Diretório base para armazenar o banco de dados, backups e exportações
BASE_DIR = os.path.join(APPDATA, "Software Controle de Ferramentas")

# Caminho do banco de dados principal
DATABASE_CAMINHO = os.path.join(BASE_DIR, "database.db")

# Diretório para backups do banco de dados
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

# Diretório para exportações
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

# Caminho para a planilha (mesmo diretório base, conforme sua imagem)
PLANILHA_IP_CAMINHO = os.path.join(BASE_DIR, "Consulta Produtos IP.xlsx")

# Garante que os diretórios necessários existam
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)
