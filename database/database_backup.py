import os
import shutil
import datetime
from database.config import BACKUP_DIR, DATABASE_CAMINHO

# Cria o diretório de backup, se não existir.
os.makedirs(BACKUP_DIR, exist_ok=True)

TURNOS = {
    "1turno": datetime.time(6, 0),
    "2turno": datetime.time(13, 0),
    "3turno": datetime.time(21, 0),
}

def get_turno_atual():
    agora = datetime.datetime.now().time()
    for nome, hora in reversed(TURNOS.items()):
        if agora >= hora:
            return nome
    return "1turno"

def get_backup_filename(data=None, turno=None):
    if data is None:
        data = datetime.date.today()
    if turno is None:
        turno = get_turno_atual()
    return f"backup_{data}_{turno}.db"

def realizar_backup(turno=None):
    """
    Cria um backup com base no turno atual (ou turno forçado).
    """
    if turno is None:
        turno = get_turno_atual()
    data = datetime.date.today()
    backup_filename = get_backup_filename(data, turno)
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    if not os.path.exists(DATABASE_CAMINHO):
        print("❌ Erro: O banco de dados original não foi encontrado. Nenhum backup realizado.")
        return

    try:
        shutil.copy(DATABASE_CAMINHO, backup_path)
        print(f"✅ Backup ({turno}) realizado com sucesso: {backup_path}")
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return

    limpar_backups_antigos()

def limpar_backups_antigos():
    """
    Remove backups com mais de 90 dias.
    """
    hoje = datetime.date.today()
    for filename in os.listdir(BACKUP_DIR):
        if not filename.endswith(".db"):
            continue
        try:
            partes = filename.replace("backup_", "").replace(".db", "").split("_")
            data_str = partes[0]
            data = datetime.datetime.strptime(data_str, "%Y-%m-%d").date()
            if (hoje - data).days > 90:
                os.remove(os.path.join(BACKUP_DIR, filename))
                print(f"🗑️ Backup antigo removido: {filename}")
        except Exception as e:
            print(f"❌ Erro ao verificar backup '{filename}': {e}")

def verificar_backup():
    """
    Verifica se há backup para o turno atual do dia.
    Se não houver, copia o mais recente disponível e usa como base.
    """
    data_hoje = datetime.date.today()
    turno_atual = get_turno_atual()
    backup_filename = get_backup_filename(data_hoje, turno_atual)
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    if os.path.exists(backup_path):
        print(f"✅ Backup do turno atual já existe: {backup_path}")
        return backup_path

    # Buscar o backup mais recente disponível (anterior)
    backups_existentes = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")],
        key=lambda f: os.path.getmtime(os.path.join(BACKUP_DIR, f)),
        reverse=True
    )

    if not backups_existentes:
        print("⚠️ Nenhum backup anterior encontrado. Criando novo...")
        realizar_backup(turno_atual)
        return backup_path

    ultimo_backup = backups_existentes[0]
    ultimo_backup_path = os.path.join(BACKUP_DIR, ultimo_backup)

    try:
        shutil.copy(ultimo_backup_path, backup_path)
        print(f"🆕 Backup do turno atual criado a partir de '{ultimo_backup}': {backup_path}")
    except Exception as e:
        print(f"❌ Erro ao copiar backup '{ultimo_backup}' para hoje: {e}")

    return backup_path

if __name__ == "__main__":
    verificar_backup()
