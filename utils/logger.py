"""
Sistema de logging para o controle de TVs
"""

import threading
from datetime import datetime
from collections import deque

# Sistema de logs
LOGS = deque(maxlen=500)  # Mantém os últimos 500 logs
LOGS_LOCK = threading.Lock()


def log(mensagem, tipo="INFO", silent=False):
    """Adiciona uma mensagem ao log com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "tipo": tipo,
        "mensagem": mensagem
    }
    with LOGS_LOCK:
        LOGS.append(log_entry)
    if not silent:
        print(f"[{timestamp}] [{tipo}] {mensagem}", flush=True)
