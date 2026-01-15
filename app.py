"""
Sistema de Controle de TVs Samsung
Aplicação Flask refatorada com separação de responsabilidades
"""

import sys
import logging
from flask import Flask
from flask import cli

# Configurações
import config
from config import HOST, PORT, TOKEN_AUTO_RENOVACAO, TOKEN_HORARIO_RENOVACAO, KEEP_ALIVE_ATIVO, KEEP_ALIVE_INTERVALO, AUTO_LIGAR_ATIVO, AUTO_LIGAR_HORARIO

# Services
from services.tv_service import TVService
from services.webhook_service import WebhookService
from services.tv_controller import TVController
from services.scheduler_service import SchedulerService
from services.whatsapp_service import WhatsAppService

# Routes
from routes import create_api_routes, create_web_routes
from routes.whatsapp_routes import create_whatsapp_routes

# Utils
from utils import log
from utils.renovador_token import RenovadorTokenSmartThings


def create_app():
    """Factory function para criar e configurar a aplicação Flask"""
    
    # Desabilita logs do Flask/Werkzeug no terminal
    log_werkzeug = logging.getLogger('werkzeug')
    log_werkzeug.setLevel(logging.ERROR)
    log_werkzeug.disabled = True
    
    # Inicializa Flask
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    
    # Inicializa services
    tv_service = TVService()
    webhook_service = WebhookService()
    whatsapp_service = WhatsAppService()
    tv_controller = TVController(tv_service, webhook_service)
    scheduler_service = SchedulerService(tv_service, tv_controller)
    renovador_token = RenovadorTokenSmartThings()
    
    # Registra rotas
    api_routes = create_api_routes(tv_service, tv_controller, scheduler_service, renovador_token)
    web_routes = create_web_routes(tv_service)
    whatsapp_routes = create_whatsapp_routes(tv_service, tv_controller, whatsapp_service)
    
    app.register_blueprint(api_routes)
    app.register_blueprint(web_routes)
    app.register_blueprint(whatsapp_routes)
    
    # Armazena services no app para acesso posterior se necessário
    app.tv_service = tv_service
    app.tv_controller = tv_controller
    app.scheduler_service = scheduler_service
    
    return app


def inicializar_sistema(app):
    """Inicializa o sistema: carrega TVs e configura schedulers"""
    
    log("=== Sistema de Controle de TVs Samsung ===", "INFO")
    log("Iniciando servidor web na porta 5000...", "INFO")
    log("Acesse: http://localhost:5000", "INFO")
    log("Logs disponíveis em: http://localhost:5000/api/logs", "INFO")
    
    # Carrega TVs da API
    print("\n" + "="*50)
    print("📡 CARREGANDO TVS DA API SMARTTHINGS...")
    print("="*50)
    
    if app.tv_service.carregar_tvs():
        tvs = app.tv_service.obter_tvs()
        print("\n" + "="*50)
        print("📺 TVS DISPONÍVEIS:")
        print("="*50)
        for i, (nome, info) in enumerate(tvs.items(), 1):
            setor = info.get('setor', 'Sem Setor')
            tv_id = info.get('id', 'N/A')
            print(f"  {i}. {nome:<30} [{setor:<15}] → {tv_id}")
        print("="*50 + "\n")
    else:
        print("\n⚠️  Falha ao carregar TVs. Verifique o token.\n")
    
    # Sistema de renovação automática de token
    if TOKEN_AUTO_RENOVACAO:
        try:
            app.scheduler_service.iniciar_renovacao_token(TOKEN_HORARIO_RENOVACAO)
            log(f"[TOKEN] Renovação automática ativada ({TOKEN_HORARIO_RENOVACAO})", "SUCCESS")
        except Exception as e:
            log(f"[TOKEN] Erro ao iniciar renovação automática: {e}", "ERROR")
    else:
        log("[TOKEN] Renovação automática desativada (config.py)", "INFO")
    
    # Sistema de Keep Alive
    if KEEP_ALIVE_ATIVO:
        app.scheduler_service.iniciar_keep_alive(KEEP_ALIVE_INTERVALO)
    
    # Sistema de ligamento automático (dias úteis)
    if AUTO_LIGAR_ATIVO:
        try:
            app.scheduler_service.iniciar_ligamento_automatico(AUTO_LIGAR_HORARIO)
            log(f"[AUTO-LIGAR] Agendamento ativado para {AUTO_LIGAR_HORARIO} (dias úteis)", "SUCCESS")
        except Exception as e:
            log(f"[AUTO-LIGAR] Erro ao iniciar agendamento: {e}", "ERROR")
    else:
        log("[AUTO-LIGAR] Ligamento automático desativado (config.py)", "INFO")
    
    # Inicia a thread do scheduler
    app.scheduler_service.iniciar_scheduler()


if __name__ == '__main__':
    # Configura stdout para line buffering e encoding
    sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')
    
    # Cria aplicação
    app = create_app()
    
    # Inicializa sistema
    inicializar_sistema(app)
    
    # Desabilita banner do Flask
    cli.show_server_banner = lambda *_: None
    
    # Inicia servidor
    app.run(debug=False, host=HOST, port=PORT, use_reloader=False)
