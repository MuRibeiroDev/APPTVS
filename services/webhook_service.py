"""
Serviço de Webhook
Responsável pelo envio de requisições para máquinas virtuais
"""

import json
import requests
from typing import Optional
from utils import log
import config


# Mapeamento de TVs para o Webhook (Nome -> ID numérico)
TV_WEBHOOK_MAP = {
    "Financeiro": "10", "FINANCEIRO": "10",
    "TV-JURIDICO": "13",
    "Operação 2 - TV2": "2", "OPERAÇÃO-2---TV2": "2",
    "TV 1 Painel - TV3": "3", "TV-1-PAINEL---TV3": "3",
    "TV 4 Painel - TV6": "6", "TV-4-PAINEL---TV6": "6",
    "Controladoria": "9", "CONTROLADORIA": "9",
    "TV 3 Painel - TV5": "5", "TV-3-PAINEL---TV5": "5",
    "TvCadastro": "14", "TVCADASTRO": "14",
    "Operação 1 - TV1": "1", "OPERAÇÃO-1---TV1": "1",
    "Antifraude": "8", "ANTIFRAUDE": "8",
    "Gestão Industria": "7", "GESTÃO-INDUSTRIA": "7",
    "TV 2 Painel - TV4": "4", "TV-2-PAINEL---TV4": "4",
    "Cobrança": "11", "COBRANÇA": "11",
    "TI02": "16",
    "TI03": "17",
    "TI01": "15"
}


class WebhookService:
    """Gerencia envio de webhooks para ligar máquinas virtuais"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or config.WEBHOOK_URL
    
    def enviar_comando_ligar(self, tv_nome: str) -> bool:
        """
        Envia webhook para ligar a máquina virtual de uma TV
        Formato: [{"output": "[{\"tv\": \"X\", \"mode\": \"Turn on\"}]"}]
        """
        try:
            tv_number = TV_WEBHOOK_MAP.get(tv_nome)
            
            if not tv_number:
                log(f"[{tv_nome}] TV não mapeada para webhook. Ignorando envio.", "WARNING")
                return False
            
            # Formato específico solicitado
            inner_json = json.dumps([{"tv": tv_number, "mode": "Turn on"}])
            webhook_data = [{"output": inner_json}]
            
            log(f"[{tv_nome}] Enviando webhook para ligar máquina virtual...", "INFO")
            response = requests.post(self.webhook_url, json=webhook_data, timeout=5)
            
            if response.status_code >= 400:
                log(f"[{tv_nome}] Erro no Webhook: {response.status_code}", "ERROR")
                return False
            else:
                log(f"[{tv_nome}] Webhook enviado (TV {tv_number}): {response.status_code} - Payload: {json.dumps(webhook_data)}", "SUCCESS")
                return True
                
        except Exception as e:
            log(f"[{tv_nome}] Erro ao enviar webhook: {e}", "ERROR")
            return False
    
    def tv_tem_webhook(self, tv_nome: str) -> bool:
        """Verifica se uma TV está mapeada para webhook"""
        return tv_nome in TV_WEBHOOK_MAP
