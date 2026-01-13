"""
Classe para interação com a API SmartThings
"""

import time
import requests
from utils.logger import log


class SmartThingsTV:
    """Cliente para controle de TVs Samsung via SmartThings API"""
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.smartthings.com/v1"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def obter_status(self, device_id):
        """Obtém o status atual do dispositivo"""
        url = f"{self.base_url}/devices/{device_id}/status"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                log("⚠️  TOKEN EXPIRADO! Gere um novo token em: https://account.smartthings.com/tokens", "ERROR")
                return None
            else:
                log(f"Erro ao obter status (HTTP {response.status_code}): {response.text}", "ERROR")
                return None
        except Exception as e:
            log(f"Exceção ao obter status: {e}", "ERROR")
            return None
    
    def _executar_comando_com_retry(self, device_id, capability, command, arguments=None, max_tentativas=5, delay_retry=2):
        """Executa um comando com retry automático em caso de erro"""
        delays = delay_retry if isinstance(delay_retry, list) else [delay_retry] * (max_tentativas - 1)
        
        for tentativa in range(1, max_tentativas + 1):
            url = f"{self.base_url}/devices/{device_id}/commands"
            
            payload = {
                "commands": [
                    {
                        "component": "main",
                        "capability": capability,
                        "command": command
                    }
                ]
            }
            
            if arguments:
                payload["commands"][0]["arguments"] = arguments
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                log(f"✓ Comando '{command}' executado com sucesso", "SUCCESS")
                return True
            else:
                log(f"✗ Tentativa {tentativa}/{max_tentativas} falhou: {response.status_code}", "ERROR")
                
                # Se falhar 5 vezes com erro 409, aborta a execução
                if response.status_code == 409 and tentativa >= 5:
                    log(f"   ABORTANDO: Erro 409 persistente após {max_tentativas} tentativas.", "ERROR")
                    raise Exception(f"Erro 409 persistente no comando '{command}'")
                
                if tentativa < max_tentativas:
                    delay = delays[tentativa - 1] if tentativa - 1 < len(delays) else delays[-1]
                    log(f"   Aguardando {delay}s antes de tentar novamente...", "WARNING")
                    time.sleep(delay)
                else:
                    log(f"   Erro final após {max_tentativas} tentativas", "ERROR")
        
        return False
