"""
Rotas da API - Endpoints HTTP
"""

import threading
import json
from pathlib import Path
from flask import Blueprint, jsonify, request
from utils import log, LOGS, LOGS_LOCK
import config


def create_routes(tv_service, tv_controller, scheduler_service, renovador_token):
    """Cria e retorna o blueprint com todas as rotas"""
    
    api = Blueprint('api', __name__, url_prefix='/api')
    TOKEN_CONFIG_FILE = Path(__file__).parent.parent / 'token_config.json'
    
    # ========== TVs ==========
    
    @api.route('/tvs')
    def listar_tvs():
        """Lista todas as TVs disponíveis"""
        return jsonify({
            "success": True,
            "tvs": list(tv_service.obter_tvs().keys())
        })
    
    @api.route('/executar/<tv_nome>', methods=['GET', 'POST'])
    def executar_sequencia(tv_nome):
        """Executa a sequência de uma TV específica (toggle power)"""
        if not tv_service.tv_existe(tv_nome):
            return jsonify({
                "success": False,
                "message": f"TV {tv_nome} não encontrada"
            }), 404
        
        # Executa em thread separada
        thread = threading.Thread(target=tv_controller.toggle_tv, args=(tv_nome,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "message": f"Comando enviado para {tv_nome}"
        })
    
    @api.route('/ligar-sem-bi/<tv_nome>', methods=['GET', 'POST'])
    def ligar_sem_bi(tv_nome):
        """Toggle de uma TV SEM webhook (não liga BI, assume que já está ligado)"""
        if not tv_service.tv_existe(tv_nome):
            return jsonify({
                "success": False,
                "message": f"TV {tv_nome} não encontrada"
            }), 404
        
        # Executa em thread separada
        thread = threading.Thread(target=tv_controller._toggle_tv_interno, args=(tv_nome, False))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "message": f"Toggle {tv_nome} (sem BI)"
        })
    
    @api.route('/ligar-com-bi/<tv_nome>', methods=['GET', 'POST'])
    def ligar_com_bi(tv_nome):
        """Liga uma TV específica COM webhook (liga BI também)"""
        if not tv_service.tv_existe(tv_nome):
            return jsonify({
                "success": False,
                "message": f"TV {tv_nome} não encontrada"
            }), 404
        
        # Executa em thread separada
        thread = threading.Thread(target=tv_controller.ligar_tv, args=(tv_nome, True))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "message": f"Ligando {tv_nome} (com BI)"
        })
    
    @api.route('/executar/todas', methods=['GET', 'POST'])
    def executar_todas():
        """Executa a sequência de todas as TVs simultaneamente (COM webhook)"""
        tv_controller.toggle_todas(enviar_webhook=True)
        return jsonify({
            "success": True,
            "message": "Sequências de todas as TVs iniciadas (COM webhook para BIs)"
        })
    
    @api.route('/religar/todas', methods=['GET', 'POST'])
    def religar_todas():
        """Executa a sequência de todas as TVs simultaneamente (SEM webhook - BIs já ligados)"""
        tv_controller.toggle_todas(enviar_webhook=False)
        return jsonify({
            "success": True,
            "message": "Sequências de todas as TVs iniciadas (SEM webhook - BIs já ligados)"
        })
    
    @api.route('/desligar/exceto-reuniao', methods=['GET', 'POST'])
    def desligar_exceto_reuniao():
        """Desliga todas as TVs exceto as de reunião, 2 por vez com intervalo de 10 segundos"""
        thread = threading.Thread(target=tv_controller.desligar_tvs_exceto_reuniao)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "message": "Desligamento em lote iniciado (exceto TVs de reunião)"
        })
    
    @api.route('/status/<tv_nome>')
    def obter_status_tv(tv_nome):
        """Obtém o status (ligada/desligada) de uma TV específica"""
        if not tv_service.tv_existe(tv_nome):
            return jsonify({
                "success": False,
                "message": f"TV {tv_nome} não encontrada"
            }), 404
        
        status = tv_service.obter_status_tv(tv_nome)
        if status is None:
            return jsonify({
                "success": False,
                "message": "Erro ao obter status"
            }), 500
        
        return jsonify({
            "success": True,
            "tv": tv_nome,
            **status
        })
    
    @api.route('/status/todas')
    def obter_status_todas():
        """Obtém o status de todas as TVs"""
        resultados = {}
        
        def check_status(nome):
            status = tv_service.obter_status_tv(nome)
            if status:
                resultados[nome] = status
        
        threads = []
        for nome in tv_service.obter_tvs().keys():
            t = threading.Thread(target=check_status, args=(nome,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        return jsonify({
            "success": True,
            "status": resultados
        })
    
    @api.route('/reconnect/<tv_nome>', methods=['POST'])
    def reconnect_tv(tv_nome):
        """Executa a sequência de reconexão: Enter -> Wait 10s -> Enter"""
        if not tv_service.tv_existe(tv_nome):
            return jsonify({
                "success": False,
                "message": f"TV {tv_nome} não encontrada"
            }), 404
        
        thread = threading.Thread(target=tv_controller.reconectar_tv, args=(tv_nome,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "message": f"Sequência de reconexão iniciada para {tv_nome}"
        })
    
    @api.route('/wallpaper/<tv_nome>', methods=['POST'])
    def alterar_wallpaper(tv_nome):
        """Altera o wallpaper de uma TV específica via webhook"""
        if not tv_service.tv_existe(tv_nome):
            return jsonify({
                "success": False,
                "message": f"TV {tv_nome} não encontrada"
            }), 404
        
        data = request.get_json()
        if not data or 'base64' not in data:
            return jsonify({
                "success": False,
                "message": "Imagem base64 não fornecida"
            }), 400
        
        base64_image = data['base64']
        
        # Usa o webhook_service do tv_controller
        resultado = tv_controller.webhook_service.enviar_comando_wallpaper(tv_nome, base64_image)
        
        return jsonify({
            "success": resultado,
            "message": f"Wallpaper alterado para {tv_nome}" if resultado else f"Erro ao alterar wallpaper de {tv_nome}"
        })
    
    @api.route('/bis/<tv_nome>', methods=['GET'])
    def listar_bis(tv_nome):
        """Lista os BIs (URLs) atuais de uma TV"""
        if not tv_service.tv_existe(tv_nome):
            return jsonify({
                "success": False,
                "message": f"TV {tv_nome} não encontrada"
            }), 404
        
        resultado = tv_controller.webhook_service.listar_bis(tv_nome)
        return jsonify(resultado)
    
    @api.route('/bis/<tv_nome>', methods=['POST'])
    def editar_bis(tv_nome):
        """Edita os BIs (URLs) de uma TV"""
        if not tv_service.tv_existe(tv_nome):
            return jsonify({
                "success": False,
                "message": f"TV {tv_nome} não encontrada"
            }), 404
        
        data = request.get_json()
        if not data or 'urls' not in data:
            return jsonify({
                "success": False,
                "message": "URLs não fornecidas. Envie {urls: ['url1', 'url2']}"
            }), 400
        
        urls = data['urls']
        if not isinstance(urls, list):
            return jsonify({
                "success": False,
                "message": "URLs deve ser uma lista"
            }), 400
        
        resultado = tv_controller.webhook_service.editar_bis(tv_nome, urls)
        
        return jsonify({
            "success": resultado,
            "message": f"BIs atualizados para {tv_nome}" if resultado else f"Erro ao atualizar BIs de {tv_nome}"
        })
    
    @api.route('/bis/<tv_nome>/abrir', methods=['POST'])
    def abrir_bi(tv_nome):
        """Abre o BI na TV"""
        if not tv_service.tv_existe(tv_nome):
            return jsonify({
                "success": False,
                "message": f"TV {tv_nome} não encontrada"
            }), 404
        
        resultado = tv_controller.webhook_service.abrir_bi(tv_nome)
        return jsonify(resultado)
    
    @api.route('/bis/<tv_nome>/fechar', methods=['POST'])
    def fechar_bi(tv_nome):
        """Fecha o BI na TV"""
        if not tv_service.tv_existe(tv_nome):
            return jsonify({
                "success": False,
                "message": f"TV {tv_nome} não encontrada"
            }), 404
        
        resultado = tv_controller.webhook_service.fechar_bi(tv_nome)
        return jsonify(resultado)
    
    # ========== Token ==========
    
    @api.route('/token/config', methods=['GET', 'POST'])
    def config_token():
        """Configura horário de renovação do token"""
        from datetime import datetime
        
        if request.method == 'POST':
            data = request.get_json()
            horario = data.get('horario', '02:00')
            
            try:
                datetime.strptime(horario, "%H:%M")
                
                config_data = {'horario': horario, 'ativo': True}
                with open(TOKEN_CONFIG_FILE, 'w') as f:
                    json.dump(config_data, f, indent=4)
                
                scheduler_service.parar_scheduler()
                scheduler_service.iniciar_renovacao_token(horario)
                scheduler_service.iniciar_scheduler()
                
                log(f"[TOKEN] Renovação agendada para {horario}", "SUCCESS")
                return jsonify({
                    "success": True,
                    "message": f"Renovação agendada para {horario}"
                })
            except ValueError:
                return jsonify({
                    "success": False,
                    "message": "Horário inválido! Use formato HH:MM"
                }), 400
        
        # GET
        try:
            if TOKEN_CONFIG_FILE.exists():
                with open(TOKEN_CONFIG_FILE, 'r') as f:
                    config_data = json.load(f)
            else:
                config_data = {'horario': '02:00', 'ativo': False}
            return jsonify({"success": True, "config": config_data})
        except:
            return jsonify({"success": True, "config": {'horario': '02:00', 'ativo': False}})
    
    @api.route('/token/renovar', methods=['POST'])
    def renovar_token_manual():
        """Executa renovação manual do token"""
        def executar():
            try:
                log("[TOKEN] Iniciando renovação manual...", "INFO")
                resultado = renovador_token.renovar()
                if resultado:
                    import importlib
                    importlib.reload(config)
                    tv_service.recarregar_token()
                    log("[TOKEN] Renovação concluída!", "SUCCESS")
                else:
                    log("[TOKEN] Erro na renovação", "ERROR")
            except Exception as e:
                log(f"[TOKEN] Erro: {e}", "ERROR")
        
        thread = threading.Thread(target=executar)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "message": "Renovação iniciada em segundo plano"
        })
    
    @api.route('/token/status')
    def token_status():
        """Retorna o status da última renovação de token"""
        status_file = Path(__file__).parent.parent / 'token_status.json'
        
        try:
            if status_file.exists():
                with open(status_file, 'r') as f:
                    status = json.load(f)
                return jsonify({
                    "success": True,
                    "status": status
                })
            else:
                return jsonify({
                    "success": True,
                    "status": {
                        "ultima_tentativa": None,
                        "sucesso": None,
                        "erro": None
                    }
                })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            })
    
    # ========== Logs ==========
    
    @api.route('/logs')
    def obter_logs():
        """Retorna os logs do sistema"""
        with LOGS_LOCK:
            logs_list = list(LOGS)
        
        return jsonify({
            "success": True,
            "logs": logs_list,
            "total": len(logs_list)
        })
    
    @api.route('/logs/limpar', methods=['POST'])
    def limpar_logs():
        """Limpa todos os logs"""
        with LOGS_LOCK:
            LOGS.clear()
        log("Logs limpos pelo usuário", "INFO")
        
        return jsonify({
            "success": True,
            "message": "Logs limpos com sucesso"
        })
    
    return api
