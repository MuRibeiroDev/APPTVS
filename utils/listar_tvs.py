"""
Script para listar todas as TVs/dispositivos disponíveis na API SmartThings
"""
import json
import requests
import sys
import os

# Adiciona o diretório pai ao path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ACCESS_TOKEN

def listar_dispositivos():
    """Lista todos os dispositivos da conta SmartThings"""
    url = "https://api.smartthings.com/v1/devices"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🔍 Buscando dispositivos na API SmartThings...\n")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            dispositivos = data.get('items', [])
            
            if not dispositivos:
                print("❌ Nenhum dispositivo encontrado.")
                return
            
            print("="*80)
            print(f"📺 DISPOSITIVOS ENCONTRADOS: {len(dispositivos)}")
            print("="*80)
            
            for i, device in enumerate(dispositivos, 1):
                device_id = device.get('deviceId', 'N/A')
                name = device.get('label', device.get('name', 'Sem nome'))
                device_type = device.get('type', 'N/A')
                manufacturer = device.get('manufacturerName', 'N/A')
                model = device.get('deviceTypeName', 'N/A')
                
                print(f"\n{i}. {name}")
                print(f"   └─ ID: {device_id}")
                print(f"   └─ Tipo: {device_type}")
                print(f"   └─ Fabricante: {manufacturer}")
                print(f"   └─ Modelo: {model}")
            
            print("\n" + "="*80)
            print("\n💡 Para usar na API, adicione ao dicionário TVS no app.py:")
            print('   TVS = {')
            for device in dispositivos:
                name = device.get('label', device.get('name', 'Sem nome'))
                device_id = device.get('deviceId', 'N/A')
                # Cria um nome de variável limpo
                var_name = name.upper().replace(' ', '-').replace('_', '-')
                print(f'       "{var_name}": "{device_id}",')
            print('   }')
            print("="*80)
            
        elif response.status_code == 401:
            print("❌ ERRO: Token de acesso inválido ou expirado!")
            print("   Gere um novo token em: https://account.smartthings.com/tokens")
        else:
            print(f"❌ ERRO HTTP {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ ERRO: Timeout ao conectar com a API SmartThings")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRO na requisição: {e}")
    except Exception as e:
        print(f"❌ ERRO inesperado: {e}")

if __name__ == "__main__":
    listar_dispositivos()
