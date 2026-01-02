"""
Funções auxiliares para controle das TVs
"""

import time
from utils.logger import log


def ligar_tv(tv, tv_id, nome_tv, delay=10):
    """Liga a TV"""
    log(f"[{nome_tv}] Ligando TV...")
    tv._executar_comando_com_retry(tv_id, "switch", "on", max_tentativas=3, delay_retry=[10, 15])
    time.sleep(delay)


def pressionar_home(tv, tv_id, nome_tv, delay=5):
    """Pressiona o botão HOME"""
    log(f"[{nome_tv}] BOTÃO HOME")
    tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["HOME", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
    time.sleep(delay)


def pressionar_enter(tv, tv_id, nome_tv, delay=5):
    """Pressiona o botão ENTER"""
    log(f"[{nome_tv}] ENTER")
    tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["OK", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
    time.sleep(delay)


def pressionar_cima(tv, tv_id, nome_tv, delay=5):
    """Pressiona a SETA CIMA"""
    log(f"[{nome_tv}] SETA CIMA")
    tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["UP", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
    time.sleep(delay)


def pressionar_baixo(tv, tv_id, nome_tv, delay=5):
    """Pressiona a SETA BAIXO"""
    log(f"[{nome_tv}] SETA BAIXO")
    tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["DOWN", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
    time.sleep(delay)


def pressionar_esquerda(tv, tv_id, nome_tv, delay=5):
    """Pressiona a SETA ESQUERDA"""
    log(f"[{nome_tv}] SETA ESQUERDA")
    tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["LEFT", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
    time.sleep(delay)


def pressionar_direita(tv, tv_id, nome_tv, delay=5):
    """Pressiona a SETA DIREITA"""
    log(f"[{nome_tv}] SETA DIREITA")
    tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["RIGHT", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
    time.sleep(delay)
