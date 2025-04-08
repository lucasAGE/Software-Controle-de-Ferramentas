import threading
import time
import schedule
from datetime import datetime
from database.database_backup import realizar_backup

TURNOS = {
    "1turno": "06:00",
    "2turno": "14:00",
    "3turno": "22:00",
}

def agendar_backups():
    for turno, horario in TURNOS.items():
        schedule.every().day.at(horario).do(realizar_backup, turno=turno)
        print(f"⏰ Backup do {turno} agendado para {horario}")

def iniciar_agendador_em_thread():
    agendar_backups()
    def loop():
        while True:
            schedule.run_pending()
            time.sleep(30)
    t = threading.Thread(target=loop, daemon=True)
    t.start()
