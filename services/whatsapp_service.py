"""
Serviço de WhatsApp
Responsável pela integração com Evolution API
"""

import requests
from typing import Optional
from utils import log
import config


class WhatsAppService:
    """Gerencia comunicação com Evolution API para enviar mensagens"""
    
    def __init__(self):
        self.api_url = config.EVOLUTION_API_URL
        self.api_key = config.EVOLUTION_API_KEY
        self.instance = config.EVOLUTION_INSTANCE
        self.numero_autorizado = config.WHATSAPP_AUTORIZADO
    
    def _get_headers(self) -> dict:
        """Retorna headers para requisições à Evolution API"""
        return {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
    
    def enviar_mensagem(self, numero: str, texto: str) -> bool:
        """
        Envia mensagem de texto via WhatsApp
        
        Args:
            numero: Número do destinatário (ex: 5562992626506)
            texto: Texto da mensagem
            
        Returns:
            True se enviado com sucesso
        """
        try:
            url = f"{self.api_url}/message/sendText/{self.instance}"
            
            payload = {
                "number": numero,
                "text": texto
            }
            
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 201 or response.status_code == 200:
                log(f"[WhatsApp] Mensagem enviada para {numero}", "SUCCESS")
                return True
            else:
                log(f"[WhatsApp] Erro ao enviar mensagem: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            log(f"[WhatsApp] Erro ao enviar mensagem: {e}", "ERROR")
            return False
    
    def esta_autorizado(self, numero: str) -> bool:
        """Verifica se o número está autorizado a enviar comandos"""
        # Remove caracteres especiais para comparação
        numero_limpo = numero.replace("@s.whatsapp.net", "").replace("+", "").replace("-", "").replace(" ", "")
        autorizado_limpo = self.numero_autorizado.replace("+", "").replace("-", "").replace(" ", "")
        
        return numero_limpo == autorizado_limpo
    
    def enviar_mensagem_autorizado(self, texto: str) -> bool:
        """Envia mensagem para o número autorizado"""
        return self.enviar_mensagem(self.numero_autorizado, texto)
