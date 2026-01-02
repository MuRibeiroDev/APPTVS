"""
Serviço de gerenciamento de TVs
Responsável por toda lógica relacionada às TVs
"""

import requests
from typing import Dict, Optional, List
from controllers import SmartThingsTV
from utils import log
import config


class TVService:
    """Gerencia operações relacionadas às TVs"""
    
    def __init__(self):
        self.tvs_cache: Dict[str, Dict] = {}
        self.access_token = config.ACCESS_TOKEN
    
    def carregar_tvs(self) -> bool:
        """Busca todas as TVs da API e monta o dicionário com nome, id e setor"""
        try:
            url = "https://api.smartthings.com/v1/devices"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                devices = response.json().get('items', [])
                self.tvs_cache.clear()
                
                print("\n📋 TODAS AS TVs DISPONÍVEIS NA API:")
                print("="*70)
                
                for device in devices:
                    device_id = device.get('deviceId')
                    device_name = device.get('label') or device.get('name', 'Unknown')
                    
                    if device_id:
                        in_list = "✅" if device_id in config.TV_IDS else "❌"
                        print(f"{in_list} {device_name:<30} → {device_id}")
                    
                    if device_id in config.TV_IDS:
                        setor = next((tv["setor"] for tv in config.TV_CONFIG if tv["id"] == device_id), "Sem Setor")
                        self.tvs_cache[device_name] = {"id": device_id, "setor": setor}
                
                print("="*70)
                print(f"\n✅ {len(self.tvs_cache)} TVs carregadas de {len(config.TV_IDS)} configuradas\n")
                
                log(f"✅ {len(self.tvs_cache)} TVs carregadas da API", "SUCCESS")
                return True
            else:
                log(f"❌ Erro ao buscar TVs: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            log(f"❌ Erro ao carregar TVs: {e}", "ERROR")
            return False
    
    def obter_tvs(self) -> Dict[str, Dict]:
        """Retorna o cache de TVs"""
        return self.tvs_cache
    
    def obter_tvs_por_setor(self) -> Dict[str, Dict]:
        """Agrupa TVs por setor"""
        tvs_por_setor = {}
        for nome, info in self.tvs_cache.items():
            setor = info.get('setor', 'Outros')
            if setor not in tvs_por_setor:
                tvs_por_setor[setor] = {}
            tvs_por_setor[setor][nome] = info
        return dict(sorted(tvs_por_setor.items()))
    
    def obter_tv(self, nome: str) -> Optional[Dict]:
        """Retorna informações de uma TV específica"""
        return self.tvs_cache.get(nome)
    
    def tv_existe(self, nome: str) -> bool:
        """Verifica se uma TV existe no cache"""
        return nome in self.tvs_cache
    
    def obter_status_tv(self, nome: str) -> Optional[Dict]:
        """Obtém o status completo de uma TV"""
        if nome not in self.tvs_cache:
            return None
        
        tv = SmartThingsTV(self.access_token)
        tv_info = self.tvs_cache[nome]
        tv_id = tv_info["id"] if isinstance(tv_info, dict) else tv_info
        status_data = tv.obter_status(tv_id)
        
        is_on = False
        is_online = False
        current_app = None
        input_source = None
        volume = None
        
        if status_data:
            is_online = True
            try:
                switch_value = status_data['components']['main']['switch']['switch']['value']
                is_on = (switch_value == 'on')
            except (KeyError, TypeError):
                pass
            
            try:
                current_app = status_data['components']['main']['tvChannel']['tvChannelName']['value']
            except (KeyError, TypeError):
                pass
            
            try:
                input_source = status_data['components']['main']['samsungvd.mediaInputSource']['inputSource']['value']
            except (KeyError, TypeError):
                pass
            
            try:
                volume = status_data['components']['main']['audioVolume']['volume']['value']
            except (KeyError, TypeError):
                pass
        
        return {
            "is_on": is_on,
            "is_online": is_online,
            "current_app": current_app,
            "input_source": input_source,
            "volume": volume,
            "setor": tv_info.get("setor", "Sem Setor")
        }
    
    def recarregar_token(self):
        """Atualiza o token de acesso"""
        import importlib
        importlib.reload(config)
        self.access_token = config.ACCESS_TOKEN
