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
    
    def enviar_comando_wallpaper(self, tv_nome: str, base64_image: str) -> bool:
        """
        Envia webhook para alterar o wallpaper de uma TV
        Formato: [{"output": "[{\"tv\": \"X\", \"mode\": \"Change wallpaper\", \"base64\": \"...\"}]"}]
        """
        try:
            tv_number = TV_WEBHOOK_MAP.get(tv_nome)
            
            if not tv_number:
                log(f"[{tv_nome}] TV não mapeada para webhook. Ignorando envio.", "WARNING")
                return False
            
            # Formato específico solicitado
            inner_json = json.dumps([{"tv": tv_number, "mode": "Change wallpaper", "base64": base64_image}])
            webhook_data = [{"output": inner_json}]
            
            # Log do payload (com base64 truncado para não poluir)
            base64_preview = base64_image[:50] + "..." if len(base64_image) > 50 else base64_image
            payload_preview = json.dumps([{"output": json.dumps([{"tv": tv_number, "mode": "Change wallpaper", "base64": base64_preview}])}])
            log(f"[{tv_nome}] Enviando webhook para alterar wallpaper...", "INFO")
            log(f"[{tv_nome}] Payload: {payload_preview}", "INFO")
            
            response = requests.post(self.webhook_url, json=webhook_data, timeout=30)
            
            if response.status_code >= 400:
                log(f"[{tv_nome}] Erro no Webhook wallpaper: {response.status_code}", "ERROR")
                return False
            else:
                log(f"[{tv_nome}] Webhook wallpaper enviado (TV {tv_number}): {response.status_code}", "SUCCESS")
                return True
                
        except Exception as e:
            log(f"[{tv_nome}] Erro ao enviar webhook wallpaper: {e}", "ERROR")
            return False
    
    def listar_bis(self, tv_nome: str) -> dict:
        """
        Lista os BIs (URLs) atuais de uma TV
        GET request para obter links abertos
        """
        try:
            tv_number = TV_WEBHOOK_MAP.get(tv_nome)
            
            if not tv_number:
                log(f"[{tv_nome}] TV não mapeada para webhook. Ignorando.", "WARNING")
                return {"success": False, "error": "TV não mapeada"}
            
            headers = {
                "Authorization": f"Basic {config.BI_WEBHOOK_AUTH}",
                "User-Agent": "Audax-View/1.0"
            }
            
            log(f"[{tv_nome}] Buscando BIs atuais (TV {tv_number})...", "INFO")
            
            # Usa files para enviar como multipart/form-data em GET
            # Isso simula o comportamento do curl --form
            response = requests.get(
                config.BI_WEBHOOK_URL,
                headers=headers,
                files={"TV": (None, tv_number)},
                timeout=10
            )
            
            log(f"[{tv_nome}] Resposta status: {response.status_code}", "INFO")
            
            # Verifica se é um erro real ou apenas "sem dados"
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    # Trata "No item to return was found" como lista vazia
                    if error_data.get("message") == "No item to return was found":
                        log(f"[{tv_nome}] Nenhum BI configurado nesta TV", "INFO")
                        return {"success": True, "bis": []}
                except:
                    pass
                
                log(f"[{tv_nome}] Erro ao listar BIs: {response.status_code} - {response.text}", "ERROR")
                return {"success": False, "error": f"Status {response.status_code}"}
            
            # Tenta parsear a resposta
            try:
                data = response.json()
                log(f"[{tv_nome}] BIs obtidos: {data}", "SUCCESS")
                return {"success": True, "bis": data}
            except:
                log(f"[{tv_nome}] Resposta: {response.text}", "INFO")
                return {"success": True, "bis": response.text}
                
        except Exception as e:
            log(f"[{tv_nome}] Erro ao listar BIs: {e}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def editar_bis(self, tv_nome: str, urls: list) -> bool:
        """
        Edita os BIs (URLs) de uma TV
        POST request para trocar links
        Args:
            tv_nome: Nome da TV
            urls: Lista de URLs (ex: ["https://link1.com", "https://link2.com"])
        """
        try:
            tv_number = TV_WEBHOOK_MAP.get(tv_nome)
            
            if not tv_number:
                log(f"[{tv_nome}] TV não mapeada para webhook. Ignorando.", "WARNING")
                return False
            
            headers = {
                "User-Agent": "Audax-View/1.0"
            }
            
            # Formata as URLs como array JSON
            urls_json = json.dumps(urls)
            
            log(f"[{tv_nome}] Editando BIs (TV {tv_number})...", "INFO")
            log(f"[{tv_nome}] Payload: TV={tv_number}, currentcontent={urls_json}", "INFO")
            
            # Usa files para enviar como multipart/form-data (igual ao curl --form)
            response = requests.post(
                config.BI_WEBHOOK_URL,
                headers=headers,
                files={
                    "TV": (None, tv_number),
                    "currentcontent": (None, urls_json)
                },
                timeout=10
            )
            
            log(f"[{tv_nome}] Resposta status: {response.status_code}", "INFO")
            
            if response.status_code >= 400:
                log(f"[{tv_nome}] Erro ao editar BIs: {response.status_code} - {response.text}", "ERROR")
                return False
            
            log(f"[{tv_nome}] BIs editados com sucesso: {response.status_code}", "SUCCESS")
            return True
                
        except Exception as e:
            log(f"[{tv_nome}] Erro ao editar BIs: {e}", "ERROR")
            return False
    
    def abrir_bi(self, tv_nome: str) -> dict:
        """
        Abre o BI na TV (envia comando Turn on para a máquina virtual)
        Formato: [{"output": "[{\"tv\": \"X\", \"mode\": \"Turn on\"}]"}]
        """
        try:
            tv_number = TV_WEBHOOK_MAP.get(tv_nome)
            
            if not tv_number:
                log(f"[{tv_nome}] TV não mapeada para webhook. Ignorando.", "WARNING")
                return {"success": False, "error": "TV não mapeada"}
            
            # Formato idêntico ao de ligar com BI
            inner_json = json.dumps([{"tv": tv_number, "mode": "Turn on"}])
            webhook_data = [{"output": inner_json}]
            
            log(f"[{tv_nome}] Enviando webhook para abrir BI (Turn on)...", "INFO")
            response = requests.post(self.webhook_url, json=webhook_data, timeout=5)
            
            if response.status_code >= 400:
                log(f"[{tv_nome}] Erro ao abrir BI: {response.status_code}", "ERROR")
                return {"success": False, "error": f"Status {response.status_code}"}
            
            log(f"[{tv_nome}] BI aberto com sucesso: {response.status_code}", "SUCCESS")
            return {"success": True, "message": "BI aberto"}
                
        except Exception as e:
            log(f"[{tv_nome}] Erro ao abrir BI: {e}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def fechar_bi(self, tv_nome: str) -> dict:
        """
        Fecha o BI na TV (envia comando Turn off para a máquina virtual)
        Formato: [{"output": "[{\"tv\": \"X\", \"mode\": \"Turn off\"}]"}]
        """
        try:
            tv_number = TV_WEBHOOK_MAP.get(tv_nome)
            
            if not tv_number:
                log(f"[{tv_nome}] TV não mapeada para webhook. Ignorando.", "WARNING")
                return {"success": False, "error": "TV não mapeada"}
            
            # Formato idêntico ao de ligar, mas com "Turn off"
            inner_json = json.dumps([{"tv": tv_number, "mode": "Turn off"}])
            webhook_data = [{"output": inner_json}]
            
            log(f"[{tv_nome}] Enviando webhook para fechar BI (Turn off)...", "INFO")
            response = requests.post(self.webhook_url, json=webhook_data, timeout=5)
            
            if response.status_code >= 400:
                log(f"[{tv_nome}] Erro ao fechar BI: {response.status_code}", "ERROR")
                return {"success": False, "error": f"Status {response.status_code}"}
            
            log(f"[{tv_nome}] BI fechado com sucesso: {response.status_code}", "SUCCESS")
            return {"success": True, "message": "BI fechado"}
                
        except Exception as e:
            log(f"[{tv_nome}] Erro ao fechar BI: {e}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def tv_tem_webhook(self, tv_nome: str) -> bool:
        """Verifica se uma TV está mapeada para webhook"""
        return tv_nome in TV_WEBHOOK_MAP
    
    def enviar_webhook(self, tvs: Optional[list] = None) -> bool:
        """
        Envia webhook para ligar máquinas virtuais de múltiplas TVs
        Args:
            tvs: Lista de nomes de TVs para ligar. Se None, liga todas as TVs mapeadas
        Returns:
            True se pelo menos um webhook foi enviado com sucesso
        """
        if tvs is None:
            # Se não especificado, usa todas as TVs do mapeamento
            tvs = list(set(TV_WEBHOOK_MAP.keys()))
        
        sucesso = False
        for tv_nome in tvs:
            if self.enviar_comando_ligar(tv_nome):
                sucesso = True
        
        return sucesso
