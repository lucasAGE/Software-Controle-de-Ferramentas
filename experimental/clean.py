import os
import shutil
from database import config


def deletar_banco():
    db_path = config.DATABASE_CAMINHO
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Banco de dados removido com sucesso!")
    else:
        print("Banco de dados não encontrado.")

def limpar_backups():
    backup_dir = config.BACKUP_DIR
    if os.path.exists(backup_dir):
        # Remove o diretório de backups e recria-o vazio
        shutil.rmtree(backup_dir)
        os.makedirs(backup_dir, exist_ok=True)
        print("Backups removidos com sucesso!")
    else:
        print("Diretório de backups não encontrado.")

def limpar_exportacoes():
    export_dir = config.EXPORT_DIR
    if os.path.exists(export_dir):
        # Remove o diretório de exportações e recria-o vazio
        shutil.rmtree(export_dir)
        os.makedirs(export_dir, exist_ok=True)
        print("Exportações removidas com sucesso!")
    else:
        print("Diretório de exportações não encontrado.")

if __name__ == "__main__":
    deletar_banco()
    limpar_backups()
    limpar_exportacoes()
    print("Limpeza completa!")
