"""
Serviço de Agendamento
Gerencia tarefas agendadas (renovação de token, keep alive)
"""

import schedule
import threading
import time
import importlib
from typing import Optional, Callable
from utils import log
from utils.renovador_token import RenovadorTokenSmartThings
from controllers import SmartThingsTV
from controllers.tv_control import pressionar_enter
import config


class SchedulerService:
    """Gerencia todas as tarefas agendadas do sistema"""
    
    def __init__(self, tv_service):
        self.tv_service = tv_service
        self.renovador_token = RenovadorTokenSmartThings()
        self.scheduler_thread: Optional[threading.Thread] = None
    
    def iniciar_renovacao_token(self, horario: str = '02:00'):
        """Agenda renovação automática de token"""
        def renovar_e_recarregar():
            log("[TOKEN] Iniciando renovação automática...", "INFO")
            resultado = self.renovador_token.renovar()
            if resultado:
                importlib.reload(config)
                self.tv_service.recarregar_token()
                log("[TOKEN] Token renovado e configuração recarregada!", "SUCCESS")
                log(f"[TOKEN] Novo token: {config.ACCESS_TOKEN[:20]}...", "INFO")
            else:
                log("[TOKEN] Falha na renovação automática", "ERROR")
            return resultado
        
        schedule.every().day.at(horario).do(renovar_e_recarregar)
        log(f"[TOKEN] Renovação agendada para {horario}", "SUCCESS")
    
    def iniciar_keep_alive(self, intervalo_minutos: int = 5, setores_ignorar: list = None):
        """Agenda execução periódica de keep alive"""
        if setores_ignorar is None:
            setores_ignorar = config.KEEP_ALIVE_IGNORE_SETORES
        
        def executar_keep_alive():
            log("[KEEP-ALIVE] Iniciando ciclo de verificação...", "INFO")
            tv_client = SmartThingsTV(config.ACCESS_TOKEN)
            
            def processar_tv(nome, info):
                try:
                    setor = info.get("setor", "")
                    if setor in setores_ignorar or "REUNIÃO" in nome.upper() or "REUNIAO" in nome.upper():
                        return
                    
                    tv_id = info["id"] if isinstance(info, dict) else info
                    
                    # Verifica se está ligada
                    status = tv_client.obter_status(tv_id)
                    is_on = False
                    if status:
                        try:
                            switch = status['components']['main']['switch']['switch']['value']
                            is_on = (switch == 'on')
                        except:
                            pass
                    
                    if is_on:
                        log(f"[KEEP-ALIVE] Executando em {nome}...", "INFO")
                        pressionar_enter(tv_client, tv_id, nome, delay=10)
                        pressionar_enter(tv_client, tv_id, nome, delay=0)
                        
                except Exception as e:
                    log(f"[KEEP-ALIVE] Erro em {nome}: {e}", "ERROR")
            
            # Processa em lotes de 2
            tvs_list = list(self.tv_service.obter_tvs().items())
            batch_size = 2
            
            for i in range(0, len(tvs_list), batch_size):
                batch = tvs_list[i:i + batch_size]
                threads = []
                
                log(f"[KEEP-ALIVE] Processando lote {i//batch_size + 1} ({len(batch)} TVs)...", "INFO")
                
                for nome, info in batch:
                    t = threading.Thread(target=processar_tv, args=(nome, info))
                    threads.append(t)
                    t.start()
                
                for t in threads:
                    t.join()
            
            log("[KEEP-ALIVE] Ciclo finalizado.", "INFO")
        
        schedule.every(intervalo_minutos).minutes.do(executar_keep_alive)
        log(f"[KEEP-ALIVE] Agendado para rodar a cada {intervalo_minutos} minutos", "SUCCESS")
    
    def iniciar_scheduler(self):
        """Inicia a thread de execução do scheduler"""
        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        if self.scheduler_thread is None or not self.scheduler_thread.is_alive():
            self.scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
            self.scheduler_thread.start()
            log("[SCHEDULER] Thread de agendamento iniciada", "SUCCESS")
    
    def parar_scheduler(self):
        """Para todas as tarefas agendadas"""
        schedule.clear()
        log("[SCHEDULER] Todas as tarefas agendadas foram canceladas", "INFO")
