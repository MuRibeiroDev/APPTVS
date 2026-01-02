"""
Rotas de WhatsApp
Responsável por receber webhooks do Evolution API e processar comandos
"""

from flask import Blueprint, request, jsonify
import threading
from utils import log


def create_whatsapp_routes(tv_service, tv_controller, whatsapp_service):
    """Cria blueprint com rotas de WhatsApp"""
    
    whatsapp = Blueprint('whatsapp', __name__)
    
    @whatsapp.route('/webhook/whatsapp', methods=['POST'])
    def webhook_whatsapp():
        """
        Webhook para receber mensagens do Evolution API
        """
        return processar_webhook()
    
    @whatsapp.route('/webhook/whatsapp/messages-upsert', methods=['POST'])
    def webhook_whatsapp_messages():
        """
        Webhook alternativo com sufixo do Evolution API
        """
        return processar_webhook()
    
    def processar_webhook():
        try:
            data = request.json
            
            # Log do payload recebido para debug
            log(f"[WhatsApp] Webhook recebido: {data}", "INFO")
            
            # Valida estrutura do webhook
            if not data or 'data' not in data:
                return jsonify({"success": True, "message": "Ignorado"}), 200
            
            webhook_data = data.get('data', {})
            
            # Extrai informações da mensagem
            key = webhook_data.get('key', {})
            message = webhook_data.get('message', {})
            
            # Número do remetente
            remote_jid = key.get('remoteJid', '')
            
            # Verifica se é mensagem de texto
            conversation = message.get('conversation', '')
            extended_text = message.get('extendedTextMessage', {}).get('text', '')
            texto_mensagem = conversation or extended_text
            
            if not texto_mensagem:
                return jsonify({"success": True, "message": "Não é mensagem de texto"}), 200
            
            # Verifica se o número está autorizado
            if not whatsapp_service.esta_autorizado(remote_jid):
                log(f"[WhatsApp] Número não autorizado: {remote_jid}", "WARNING")
                return jsonify({"success": True, "message": "Não autorizado"}), 200
            
            # Processa comandos
            processar_comando(texto_mensagem.strip(), remote_jid, tv_service, tv_controller, whatsapp_service)
            
            return jsonify({"success": True, "message": "Processado"}), 200
            
        except Exception as e:
            log(f"[WhatsApp] Erro no webhook: {e}", "ERROR")
            return jsonify({"success": False, "error": str(e)}), 500
    
    def processar_comando(comando: str, numero: str, tv_service, tv_controller, whatsapp_service):
        """Processa comandos recebidos via WhatsApp"""
        
        comando_lower = comando.lower()
        
        # Comando: !ligartvs (COM webhook - primeira vez)
        if comando_lower == '!ligartvs':
            def executar_ligar():
                whatsapp_service.enviar_mensagem_autorizado("🔄 Iniciando processo COMPLETO...\n\n✅ Ligando BIs (máquinas virtuais)\n✅ Ligando TVs\n\nSerão ligadas em blocos de 2 TVs com intervalo de 20 segundos entre cada bloco.")
                
                tvs = tv_service.obter_tvs()
                total = len(tvs)
                
                resultado = tv_controller.toggle_todas(enviar_webhook=True)
                
                if resultado:
                    whatsapp_service.enviar_mensagem_autorizado(f"✅ Comando enviado para {total} TVs + BIs!\n\nO processo está em andamento. Verifique os logs para acompanhar o progresso.")
                else:
                    whatsapp_service.enviar_mensagem_autorizado("❌ Erro ao iniciar o processo.")
            
            thread = threading.Thread(target=executar_ligar)
            thread.daemon = True
            thread.start()
            
            log(f"[WhatsApp] Comando !ligartvs (COM webhook) recebido de {numero}", "INFO")
        
        # Comando: !religartvs (SEM webhook - BIs já ligados)
        elif comando_lower == '!religartvs':
            def executar_religar():
                whatsapp_service.enviar_mensagem_autorizado("🔄 Iniciando processo de RELIGAR TVs...\n\n⚠️ BIs já devem estar ligados\n✅ Ligando apenas TVs\n\nSerão ligadas em blocos de 2 TVs com intervalo de 20 segundos entre cada bloco.")
                
                tvs = tv_service.obter_tvs()
                total = len(tvs)
                
                resultado = tv_controller.toggle_todas(enviar_webhook=False)
                
                if resultado:
                    whatsapp_service.enviar_mensagem_autorizado(f"✅ Comando enviado para {total} TVs!\n\n⚠️ Webhooks de BIs foram ignorados (BIs já ligados).")
                else:
                    whatsapp_service.enviar_mensagem_autorizado("❌ Erro ao iniciar o processo.")
            
            thread = threading.Thread(target=executar_religar)
            thread.daemon = True
            thread.start()
            
            log(f"[WhatsApp] Comando !religartvs (SEM webhook) recebido de {numero}", "INFO")
        
        # Comando: !ligar <nome_da_tv>
        elif comando_lower.startswith('!ligar '):
            tv_nome = comando[7:].strip()  # Remove "!ligar " do início
            
            def executar_ligar_tv():
                tvs = tv_service.obter_tvs()
                
                # Busca a TV (case-insensitive)
                tv_encontrada = None
                for nome in tvs.keys():
                    if nome.lower() == tv_nome.lower():
                        tv_encontrada = nome
                        break
                
                if not tv_encontrada:
                    whatsapp_service.enviar_mensagem_autorizado(f"❌ TV '{tv_nome}' não encontrada.\n\nUse !listartvs para ver todas as TVs disponíveis.")
                    return
                
                whatsapp_service.enviar_mensagem_autorizado(f"🔄 Ligando TV: *{tv_encontrada}*...")
                
                resultado = tv_controller.ligar_tv(tv_encontrada)
                
                if resultado:
                    whatsapp_service.enviar_mensagem_autorizado(f"✅ Comando enviado para *{tv_encontrada}*!\n\nA TV está sendo ligada. Aguarde alguns segundos.")
                else:
                    whatsapp_service.enviar_mensagem_autorizado(f"❌ Erro ao ligar *{tv_encontrada}*.")
            
            thread = threading.Thread(target=executar_ligar_tv)
            thread.daemon = True
            thread.start()
            
            log(f"[WhatsApp] Comando !ligar {tv_nome} recebido de {numero}", "INFO")
        
        # Comando: !status
        elif comando_lower == '!status':
            def executar_status():
                tvs = tv_service.obter_tvs()
                total = len(tvs)
                
                whatsapp_service.enviar_mensagem_autorizado(f"📊 *Status do Sistema*\n\n📺 TVs cadastradas: {total}\n\nUse !listartvs para ver todas as TVs.")
            
            thread = threading.Thread(target=executar_status)
            thread.daemon = True
            thread.start()
        
        # Comando: !listartvs
        elif comando_lower == '!listartvs':
            def executar_listar():
                tvs = tv_service.obter_tvs()
                setores = tv_service.obter_tvs_por_setor()
                
                mensagem = "📺 *TVs Cadastradas*\n\n"
                
                for setor, tvs_setor in setores.items():
                    mensagem += f"*{setor}:*\n"
                    for tv in tvs_setor:
                        mensagem += f"  • {tv}\n"
                    mensagem += "\n"
                
                mensagem += f"Total: {len(tvs)} TVs"
                
                whatsapp_service.enviar_mensagem_autorizado(mensagem)
            
            thread = threading.Thread(target=executar_listar)
            thread.daemon = True
            thread.start()
        
        # Comando: !ajuda ou !comandos
        elif comando_lower in ['!ajuda', '!comandos', '!help']:
            mensagem = """📱 *Comandos Disponíveis*

*Ligar TVs:*
!ligartvs - Liga BIs + TVs (primeira vez)
!religartvs - Liga apenas TVs (BIs já ligados)
!ligar <nome> - Liga uma TV específica

*Informações:*
!status - Status do sistema
!listartvs - Lista todas as TVs
!ajuda - Mostra esta mensagem

💡 Apenas você pode usar estes comandos.

⚠️ *Importante:*
• Use !ligartvs na primeira vez do dia
• Use !religartvs nas próximas vezes

Exemplo: !ligar TI01"""
            
            whatsapp_service.enviar_mensagem_autorizado(mensagem)
        
        else:
            # Comando não reconhecido
            if comando.startswith('!'):
                whatsapp_service.enviar_mensagem_autorizado(f"❓ Comando '{comando}' não reconhecido.\n\nUse !ajuda para ver os comandos disponíveis.")
    
    return whatsapp
