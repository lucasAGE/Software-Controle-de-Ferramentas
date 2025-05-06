import threading
import schedule
import time
import logging
from typing import Dict

from database.database_backup import realizar_backup
import database.config as config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Horários de início de cada turno (configurável)
TURNOS: Dict[str, str] = {
    "1turno": "06:00",
    "2turno": "14:00",
    "3turno": "22:00",
}

_config_lock = threading.Lock()
_stop_event = threading.Event()

def _backup_e_troca(turno: str) -> None:
    """Executa backup para o turno informado e atualiza config.DATABASE_CAMINHO."""
    try:
        novo_db = realizar_backup(turno=turno)
    except Exception:
        logger.exception("Erro ao executar backup para %s", turno)
        return

    if novo_db:
        with _config_lock:
            config.DATABASE_CAMINHO = novo_db
        logger.info("Banco atualizado para %s: %s", turno, novo_db)
    else:
        logger.error("Falha ao gerar backup para %s", turno)

def agendar_backups() -> None:
    """Agenda backups diários para cada turno."""
    for turno, horario in TURNOS.items():
        schedule.every().day.at(horario).do(_backup_e_troca, turno)
        logger.info("Backup agendado para %s às %s", turno, horario)

def iniciar_agendador_em_thread() -> threading.Thread:
    """
    Inicia o agendador em thread daemon.
    Retorna o objeto Thread para possível controle externo.
    """
    agendar_backups()
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return t

def _loop() -> None:
    """Loop interno que roda pendências até stop_event ser sinalizado."""
    while not _stop_event.is_set():
        schedule.run_pending()
        time.sleep(30)

def stop_agendador() -> None:
    """Sinaliza para a thread de agendamento parar."""
    _stop_event.set()

if __name__ == "__main__":
    iniciar_agendador_em_thread()
    try:
        # Mantém o script ativo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Parando agendador…")
        stop_agendador()
