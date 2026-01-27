"""
Configurações do sistema de controle de TVs Samsung
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Token de acesso SmartThings (atualizado automaticamente pelo renovador)
ACCESS_TOKEN = "302fc938-d6fb-41ae-93c7-4102cf6e857a"

# AVISO: Se você está recebendo erros 401, o token pode ter expirado.
# O sistema renova automaticamente, mas para gerar manualmente:
# 1. Acesse: https://account.smartthings.com/tokens
# 2. Crie um novo Personal Access Token
# 3. Marque as permissões: devices (read, write, execute)
# 4. Substitua o ACCESS_TOKEN acima pelo novo token gerado

# IDs das TVs com seus setores (o sistema busca os nomes automaticamente via API)
# Formato: {"id": "device_id", "setor": "nome_do_setor"}
TV_CONFIG = [
    {"id": "a856316a-8b57-f399-e72b-fd595c67edd3", "setor": "Operação"},      # OPERAÇÃO-2---TV2
    {"id": "eb80c602-ae51-a7b6-eaa2-d305b45dd23c", "setor": "Reunião"},       # TV-REUNIÃO-01
    {"id": "65a53ea8-334d-1510-94c0-915fbbd2ceb1", "setor": "Reunião"},       # TV-ATLAS
    {"id": "541381f7-f709-60f1-312e-4157dd324528", "setor": "Operação"},      # TV-1-PAINEL---TV3
    {"id": "a72afd67-bc90-db11-e16b-55ad1adf253f", "setor": "Operação"},      # TV-4-PAINEL---TV6
    {"id": "66d85860-b9b3-0b1d-0ad4-6577159d60c6", "setor": "Operação"}, # CONTROLADORIA
    {"id": "a94e2b55-c2db-2945-9407-7b4514d829c1", "setor": "Operação"},      # TV-3-PAINEL---TV5
    {"id": "d339553c-5dc4-e28d-e0f2-e188e81b0fca", "setor": "Jurídico"},      # TV-JURIDICO
    {"id": "6282866e-47cb-2dde-cbc4-15c381ff6540", "setor": "Reunião"},       # TV-REUNIÃO-02
    {"id": "741ef7e0-f033-809b-1e09-7313e1e37ef0", "setor": "Operação"},      # TVCADASTRO
    {"id": "abb860b1-4190-c03a-4ac7-19459adc6bcc", "setor": "Reunião"},       # TV-MOSSAD
    {"id": "4321bd17-6f06-cdfc-08ac-8edef0b768ae", "setor": "Operação"},      # OPERAÇÃO-1---TV1
    {"id": "b836e65f-4c6f-0019-ae1b-26dc4f08f634", "setor": "TI"},            # TI02
    {"id": "9aec8b23-27bd-cbf5-ed28-36ae181bf20d", "setor": "TI"},            # TI03
    {"id": "391051ba-fa19-0afc-81cb-9a8114ff6726", "setor": "Operação"},    # ANTIFRAUDE
    {"id": "4a26a59f-1f9e-858f-bf7f-f448389b7c22", "setor": "Reunião"},       # TV-DIA-D
    {"id": "98c6e6f8-95b4-cebd-58c3-89b0c8914c98", "setor": "TI"},            # TI01
    {"id": "04523f83-6676-e648-87e4-c72543aaee45", "setor": "Operação"},        # GESTÃO-INDUSTRIA
    {"id": "033209fe-3ae3-2d71-be86-75b2f1d4268b", "setor": "Reunião"},       # TV-GEO-FOREST
    {"id": "cd98ec70-e345-2960-c042-ec2bcd783f24", "setor": "Operação"},      # TV-2-PAINEL---TV4
    {"id": "22b8779b-16f5-9c79-687b-70c275d6e550", "setor": "Operação"},      # COBRANÇA
    {"id": "50f875f3-b76b-b808-396e-b343a899a517", "setor": "Financeiro"},    # FINANCEIRO
    {"id": "e83bb859-9240-2b35-c6e1-b4b217b6821b", "setor": "Cozinha"},       # Cozinha Entrada
    {"id": "61fcb532-3d44-f253-c838-16e031135519", "setor": "Recepção"}       # Recepção
]

# Lista de IDs para compatibilidade
TV_IDS = [tv["id"] for tv in TV_CONFIG]

# URL do webhook para ligar máquinas virtuais (do .env)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# URL do endpoint de gerenciamento de BIs (do .env)
BI_WEBHOOK_URL = os.getenv("BI_WEBHOOK_URL", "http://172.16.30.10:5679/webhook/f70578b6-fad3-421e-b19b-552cb6c8e981")
BI_WEBHOOK_AUTH = os.getenv("BI_WEBHOOK_AUTH", "UmlrZWxtZVNhbnRvczoxMjM0NTY=")

# Configurações do servidor
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

# Configurações de renovação automática de token
TOKEN_AUTO_RENOVACAO = True  # True para ativar, False para desativar
TOKEN_HORARIO_RENOVACAO = "08:26"  # Horário diário para renovar (formato HH:MM)

# Configuração de ligamento automático de TVs
AUTO_LIGAR_ATIVO = True  # True para ativar, False para desativar
AUTO_LIGAR_HORARIO = "06:20"  # Horário diário para ligar todas as TVs (formato HH:MM)

# Configuração de Keep Alive (Reconexão automática)
KEEP_ALIVE_ATIVO = True
KEEP_ALIVE_INTERVALO = 5  # Minutos
KEEP_ALIVE_IGNORE_SETORES = ["Reunião", "Reuniao", "Recepção", "Recepcao", "Cozinha", "Jurídico", "Juridico"]

# Credenciais Google para renovação de token (do .env)
GOOGLE_EMAIL = os.getenv("GOOGLE_EMAIL")
GOOGLE_SENHA = os.getenv("GOOGLE_SENHA")

# Configurações Evolution API / WhatsApp (do .env)
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE")
WHATSAPP_AUTORIZADO = os.getenv("WHATSAPP_AUTORIZADO")