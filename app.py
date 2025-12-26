"""
Servidor Flask para controle das TVs Samsung via interface web
"""

from flask import Flask, jsonify, render_template
import time
import threading
import requests

app = Flask(__name__)

# Token configurado
ACCESS_TOKEN = "4ee52f3e-0e98-4469-a1a0-71ca0c85c0f6"

# IDs das TVs
TVS = {
    "TI01": "98c6e6f8-95b4-cebd-58c3-89b0c8914c98",
    "TI02": "b836e65f-4c6f-0019-ae1b-26dc4f08f634",
    "TI03": "9aec8b23-27bd-cbf5-ed28-36ae181bf20d",
    "TV-ATLAS": "65a53ea8-334d-1510-94c0-915fbbd2ceb1REMOVERDEPOISDAREUNIAO",
    "TV-JURIDICO": "d339553c-5dc4-e28d-e0f2-e188e81b0fca"
}

# ========== CLASSE SMARTTHINGS TV ==========
class SmartThingsTV:
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
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def obter_saude(self, device_id):
        """Obtém a saúde (conexão) do dispositivo"""
        url = f"{self.base_url}/devices/{device_id}/health"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    
    def _executar_comando_com_retry(self, device_id, capability, command, arguments=None, max_tentativas=3, delay_retry=2):
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
                print(f"✓ Comando '{command}' executado com sucesso")
                return True
            else:
                print(f"✗ Tentativa {tentativa}/{max_tentativas} falhou: {response.status_code}")
                
                if tentativa < max_tentativas:
                    delay = delays[tentativa - 1] if tentativa - 1 < len(delays) else delays[-1]
                    print(f"   Aguardando {delay}s antes de tentar novamente...")
                    time.sleep(delay)
                else:
                    print(f"   Erro final após {max_tentativas} tentativas")
        
        return False

# ========== SEQUÊNCIAS DAS TVS ==========

def sequencia_ti(tv, tv_id, nome_tv):
    """Sequência para TVs TI01, TI02 e TI03"""
    try:
        print(f"\n[{nome_tv}] Iniciando sequência...")
        
        tv._executar_comando_com_retry(tv_id, "switch", "on", max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print(f"[{nome_tv}] SETA ESQUERDA")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["LEFT", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print(f"[{nome_tv}] SETA CIMA (1/2)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["UP", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print(f"[{nome_tv}] SETA CIMA (2/2)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["UP", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print(f"[{nome_tv}] ENTER")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["OK", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print(f"[{nome_tv}] SETA BAIXO")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["DOWN", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print(f"[{nome_tv}] ENTER")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["OK", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print(f"[{nome_tv}] ENTER")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["OK", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        
        print(f"[{nome_tv}] Sequência finalizada!")
        return True
    except Exception as e:
        print(f"[{nome_tv}] ERRO: {e}")
        return False

def sequencia_atlas(tv, tv_id):
    """Sequência para TV-ATLAS"""
    try:
        print("\n[TV-ATLAS] Iniciando sequência...")
        
        tv._executar_comando_com_retry(tv_id, "switch", "on", max_tentativas=3, delay_retry=[10, 15])
        time.sleep(5)
        
        print("[TV-ATLAS] BOTÃO HOME")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["HOME", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-ATLAS] SETA ESQUERDA")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["LEFT", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-ATLAS] SETA BAIXO")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["DOWN", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-ATLAS] SETA DIREITA (1/3)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["RIGHT", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-ATLAS] SETA DIREITA (2/3)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["RIGHT", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-ATLAS] SETA DIREITA (3/3)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["RIGHT", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-ATLAS] ENTER")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["OK", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-ATLAS] SETA DIREITA")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["RIGHT", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-ATLAS] ENTER")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["OK", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        
        print("[TV-ATLAS] Sequência finalizada!")
        return True
    except Exception as e:
        print(f"[TV-ATLAS] ERRO: {e}")
        return False

def sequencia_juridico(tv, tv_id):
    """Sequência para TV-JURIDICO"""
    try:
        print("\n[TV-JURIDICO] Iniciando sequência...")
        
        print("[TV-JURIDICO] Ligando TV...")
        tv._executar_comando_com_retry(tv_id, "switch", "on", max_tentativas=3, delay_retry=[10, 15])
        time.sleep(5)
        
        print("[TV-JURIDICO] ENTER (1)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["OK", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] SETA DIREITA (1/2)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["RIGHT", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] SETA DIREITA (2/2)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["RIGHT", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] ENTER (2)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["OK", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] SETA BAIXO (1/3)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["DOWN", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] SETA BAIXO (2/3)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["DOWN", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] SETA BAIXO (3/3)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["DOWN", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] ENTER (3)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["OK", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] SETA BAIXO (1/2)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["DOWN", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] SETA BAIXO (2/2)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["DOWN", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] ENTER (4)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["OK", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] SETA DIREITA")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["RIGHT", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] ENTER (5)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["OK", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        time.sleep(3)
        
        print("[TV-JURIDICO] ENTER (6)")
        tv._executar_comando_com_retry(tv_id, "samsungvd.remoteControl", "send", ["OK", "PRESS_AND_RELEASED"], max_tentativas=3, delay_retry=[10, 15])
        
        print("[TV-JURIDICO] Sequência finalizada!")
        return True
    except Exception as e:
        print(f"[TV-JURIDICO] ERRO: {e}")
        return False

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/tvs')
def listar_tvs():
    """Lista todas as TVs disponíveis"""
    return jsonify({
        "success": True,
        "tvs": list(TVS.keys())
    })

@app.route('/api/executar/<tv_nome>', methods=['GET', 'POST'])
def executar_sequencia(tv_nome):
    """Executa a sequência de uma TV específica (toggle power)"""
    if tv_nome not in TVS:
        return jsonify({
            "success": False,
            "sucesso": False,
            "message": f"TV {tv_nome} não encontrada",
            "mensagem": f"TV {tv_nome} não encontrada"
        }), 404
    
    def executar():
        tv = SmartThingsTV(ACCESS_TOKEN)
        tv_id = TVS[tv_nome]
        
        # Verifica o status atual da TV
        status_data = tv.obter_status(tv_id)
        is_on = False
        
        if status_data:
            try:
                switch_value = status_data['components']['main']['switch']['switch']['value']
                is_on = (switch_value == 'on')
            except (KeyError, TypeError):
                pass
        
        # Toggle: se está ligada, desliga; se está desligada, executa sequência
        if is_on:
            print(f"[{tv_nome}] Desligando TV...")
            tv._executar_comando_com_retry(tv_id, "switch", "off", max_tentativas=3, delay_retry=[10, 15])
        else:
            # Envia webhook para ligar a máquina virtual
            print(f"[{tv_nome}] Enviando webhook para ligar máquina virtual...")
            try:
                webhook_url = "http://172.16.30.10:5679/webhook-test/ligatvsmurilo"
                webhook_data = {"tv": tv_nome}
                response = requests.post(webhook_url, json=webhook_data, timeout=5)
                print(f"[{tv_nome}] Webhook enviado: {response.status_code}")
            except Exception as e:
                print(f"[{tv_nome}] Erro ao enviar webhook: {e}")
            
            # Executa a sequência específica para ligar e configurar
            if tv_nome in ["TI01", "TI02", "TI03"]:
                sequencia_ti(tv, tv_id, tv_nome)
            elif tv_nome == "TV-ATLAS":
                sequencia_atlas(tv, tv_id)
            elif tv_nome == "TV-JURIDICO":
                sequencia_juridico(tv, tv_id)
    
    # Executa em thread separada para não bloquear a resposta
    thread = threading.Thread(target=executar)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "success": True,
        "sucesso": True,
        "message": f"Comando enviado para {tv_nome}",
        "mensagem": f"Comando enviado para {tv_nome}"
    })

@app.route('/api/executar/todas')
def executar_todas():
    """Executa a sequência de todas as TVs simultaneamente"""
    def executar_todas_threads():
        tv = SmartThingsTV(ACCESS_TOKEN)
        threads = []
        
        # TI01
        t1 = threading.Thread(target=sequencia_ti, args=(tv, TVS["TI01"], "TI01"))
        threads.append(t1)
        
        # TI02
        t2 = threading.Thread(target=sequencia_ti, args=(tv, TVS["TI02"], "TI02"))
        threads.append(t2)
        
        # TI03
        t3 = threading.Thread(target=sequencia_ti, args=(tv, TVS["TI03"], "TI03"))
        threads.append(t3)
        
        # TV-ATLAS
        t4 = threading.Thread(target=sequencia_atlas, args=(tv, TVS["TV-ATLAS"]))
        threads.append(t4)
        
        # TV-JURIDICO
        t5 = threading.Thread(target=sequencia_juridico, args=(tv, TVS["TV-JURIDICO"]))
        threads.append(t5)
        
        # Inicia todas as threads
        for t in threads:
            t.start()
        
        # Aguarda todas finalizarem
        for t in threads:
            t.join()
        
        print("\nTodas as sequências finalizadas!")
    
    # Executa em thread separada
    thread = threading.Thread(target=executar_todas_threads)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "success": True,
        "message": "Sequências de todas as TVs iniciadas"
    })

@app.route('/api/status/<tv_nome>')
def obter_status_tv(tv_nome):
    """Obtém o status (ligada/desligada) de uma TV específica"""
    if tv_nome not in TVS:
        return jsonify({
            "success": False,
            "message": f"TV {tv_nome} não encontrada"
        }), 404
    
    tv = SmartThingsTV(ACCESS_TOKEN)
    tv_id = TVS[tv_nome]
    status_data = tv.obter_status(tv_id)
    
    is_on = False
    if status_data:
        try:
            switch_value = status_data['components']['main']['switch']['switch']['value']
            is_on = (switch_value == 'on')
        except (KeyError, TypeError):
            pass
            
    return jsonify({
        "success": True,
        "tv": tv_nome,
        "is_on": is_on
    })

@app.route('/api/status/todas')
def obter_status_todas():
    """Obtém o status de todas as TVs"""
    tv = SmartThingsTV(ACCESS_TOKEN)
    resultados = {}
    
    def check_status(nome, id):
        # Verifica status (ligada/desligada)
        status_data = tv.obter_status(id)
        is_on = False
        current_app = None
        input_source = None
        volume = None
        
        if status_data:
            try:
                switch_value = status_data['components']['main']['switch']['switch']['value']
                is_on = (switch_value == 'on')
            except (KeyError, TypeError):
                pass
            
            # App/Canal atual
            try:
                current_app = status_data['components']['main']['tvChannel']['tvChannelName']['value']
            except (KeyError, TypeError):
                pass
            
            # Entrada atual
            try:
                input_source = status_data['components']['main']['samsungvd.mediaInputSource']['inputSource']['value']
            except (KeyError, TypeError):
                pass
            
            # Volume
            try:
                volume = status_data['components']['main']['audioVolume']['volume']['value']
            except (KeyError, TypeError):
                pass
        
        # Verifica saúde (online/offline)
        health_data = tv.obter_saude(id)
        is_online = False
        if health_data:
            is_online = (health_data.get('state') == 'ONLINE')

        resultados[nome] = {
            "is_on": is_on,
            "is_online": is_online,
            "current_app": current_app,
            "input_source": input_source,
            "volume": volume
        }

    threads = []
    for nome, id in TVS.items():
        t = threading.Thread(target=check_status, args=(nome, id))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
        
    return jsonify({
        "success": True,
        "status": resultados
    })

if __name__ == '__main__':
    print("Iniciando servidor web na porta 5000...")
    print("Acesse: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
