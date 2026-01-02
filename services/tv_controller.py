"""
Controlador de TVs
Gerencia operações de controle e execução de sequências
"""

import threading
import time
from typing import Optional
from controllers import SmartThingsTV
from controllers.tv_control import pressionar_enter
from utils import log
from .webhook_service import WebhookService
from .sequence_mapper import SequenceMapper
import config


class TVController:
    """Controla operações de TVs (ligar, desligar, sequências)"""
    
    def __init__(self, tv_service, webhook_service: Optional[WebhookService] = None):
        self.tv_service = tv_service
        self.webhook_service = webhook_service or WebhookService()
        self.sequence_mapper = SequenceMapper()
    
    def toggle_tv(self, tv_nome: str) -> bool:
        """
        Toggle de uma TV: se ligada desliga, se desligada liga + executa sequência
        """
        if not self.tv_service.tv_existe(tv_nome):
            log(f"[{tv_nome}] TV não encontrada", "ERROR")
            return False
        
        try:
            tv = SmartThingsTV(config.ACCESS_TOKEN)
            tv_info = self.tv_service.obter_tv(tv_nome)
            tv_id = tv_info["id"] if isinstance(tv_info, dict) else tv_info
            
            # Verifica status atual
            status_data = tv.obter_status(tv_id)
            is_on = False
            
            if status_data:
                try:
                    switch_value = status_data['components']['main']['switch']['switch']['value']
                    is_on = (switch_value == 'on')
                except (KeyError, TypeError):
                    pass
            
            # Toggle
            if is_on:
                log(f"[{tv_nome}] Desligando TV...", "INFO")
                tv._executar_comando_com_retry(tv_id, "switch", "off", max_tentativas=3, delay_retry=[10, 15])
            else:
                # Envia webhook para ligar máquina virtual
                self.webhook_service.enviar_comando_ligar(tv_nome)
                
                # Executa sequência de inicialização
                self.sequence_mapper.executar_sequencia(tv, tv_id, tv_nome)
            
            return True
        except Exception as e:
            log(f"[{tv_nome}] Erro no toggle: {e}", "ERROR")
            return False
    
    def ligar_tv(self, tv_nome: str, enviar_webhook: bool = True) -> bool:
        """
        Liga uma TV específica (força ligar, não faz toggle)
        
        Args:
            tv_nome: Nome da TV
            enviar_webhook: Se True, envia webhook para ligar BI. Se False, apenas liga a TV
        """
        if not self.tv_service.tv_existe(tv_nome):
            log(f"[{tv_nome}] TV não encontrada", "ERROR")
            return False
        
        try:
            tv = SmartThingsTV(config.ACCESS_TOKEN)
            tv_info = self.tv_service.obter_tv(tv_nome)
            tv_id = tv_info["id"] if isinstance(tv_info, dict) else tv_info
            
            log(f"[{tv_nome}] Iniciando processo de ligar TV...", "INFO")
            
            # Envia webhook para ligar máquina virtual (apenas se solicitado)
            if enviar_webhook:
                self.webhook_service.enviar_comando_ligar(tv_nome)
            else:
                log(f"[{tv_nome}] Webhook ignorado (BI já está ligado)", "INFO")
            
            # Executa sequência de inicialização
            self.sequence_mapper.executar_sequencia(tv, tv_id, tv_nome)
            
            return True
        except Exception as e:
            log(f"[{tv_nome}] Erro ao ligar: {e}", "ERROR")
            return False
    
    def reconectar_tv(self, tv_nome: str) -> bool:
        """Executa sequência de reconexão: Enter -> Wait 10s -> Enter"""
        if not self.tv_service.tv_existe(tv_nome):
            log(f"[{tv_nome}] TV não encontrada", "ERROR")
            return False
        
        try:
            tv = SmartThingsTV(config.ACCESS_TOKEN)
            tv_info = self.tv_service.obter_tv(tv_nome)
            tv_id = tv_info["id"] if isinstance(tv_info, dict) else tv_info
            
            log(f"[{tv_nome}] Iniciando reconexão (Enter + 10s + Enter)...", "INFO")
            pressionar_enter(tv, tv_id, tv_nome, delay=10)
            pressionar_enter(tv, tv_id, tv_nome, delay=0)
            log(f"[{tv_nome}] Reconexão finalizada!", "SUCCESS")
            
            return True
        except Exception as e:
            log(f"[{tv_nome}] Erro na reconexão: {e}", "ERROR")
            return False
    
    def toggle_todas(self, enviar_webhook: bool = True) -> bool:
        """
        Executa toggle em todas as TVs em blocos de 2 com intervalo de 20s
        
        Args:
            enviar_webhook: Se True, envia webhook para ligar BIs. Se False, apenas liga TVs
        """
        def executar_todas():
            tvs = list(self.tv_service.obter_tvs().keys())
            total_tvs = len(tvs)
            
            if enviar_webhook:
                log(f"Iniciando toggle de {total_tvs} TVs em blocos de 2 (COM webhook para BIs)...", "INFO")
            else:
                log(f"Iniciando toggle de {total_tvs} TVs em blocos de 2 (SEM webhook - BIs já ligados)...", "INFO")
            
            # Processa em blocos de 2
            for i in range(0, total_tvs, 2):
                bloco = tvs[i:i+2]
                bloco_num = (i // 2) + 1
                
                log(f"[BLOCO {bloco_num}] Processando TVs: {', '.join(bloco)}", "INFO")
                
                threads = []
                for tv_nome in bloco:
                    t = threading.Thread(target=self._toggle_tv_interno, args=(tv_nome, enviar_webhook))
                    threads.append(t)
                    t.start()
                
                # Aguarda threads do bloco atual terminarem
                for t in threads:
                    t.join()
                
                # Aguarda 20 segundos antes do próximo bloco (exceto no último)
                if i + 2 < total_tvs:
                    log(f"[BLOCO {bloco_num}] Concluído. Aguardando 20 segundos...", "SUCCESS")
                    time.sleep(20)
            
            log("Todas as sequências finalizadas!", "SUCCESS")
        
        thread = threading.Thread(target=executar_todas)
        thread.daemon = True
        thread.start()
        return True
    
    def _toggle_tv_interno(self, tv_nome: str, enviar_webhook: bool) -> bool:
        """Método interno para toggle com controle de webhook"""
        if not self.tv_service.tv_existe(tv_nome):
            log(f"[{tv_nome}] TV não encontrada", "ERROR")
            return False
        
        try:
            tv = SmartThingsTV(config.ACCESS_TOKEN)
            tv_info = self.tv_service.obter_tv(tv_nome)
            tv_id = tv_info["id"] if isinstance(tv_info, dict) else tv_info
            
            # Verifica status atual
            status_data = tv.obter_status(tv_id)
            is_on = False
            
            if status_data:
                try:
                    switch_value = status_data['components']['main']['switch']['switch']['value']
                    is_on = (switch_value == 'on')
                except (KeyError, TypeError):
                    pass
            
            # Toggle
            if is_on:
                log(f"[{tv_nome}] Desligando TV...", "INFO")
                tv._executar_comando_com_retry(tv_id, "switch", "off", max_tentativas=3, delay_retry=[10, 15])
            else:
                # Envia webhook apenas se solicitado
                if enviar_webhook:
                    self.webhook_service.enviar_comando_ligar(tv_nome)
                else:
                    log(f"[{tv_nome}] Webhook ignorado (BI já está ligado)", "INFO")
                
                # Executa sequência de inicialização
                self.sequence_mapper.executar_sequencia(tv, tv_id, tv_nome)
            
            return True
        except Exception as e:
            log(f"[{tv_nome}] Erro no toggle: {e}", "ERROR")
            return False
