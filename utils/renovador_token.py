"""
Sistema de Renovação Automática de Token SmartThings
Gerencia o processo completo: login, geração, captura e atualização do token
"""

import time
import json
import os
import requests
import schedule
from pathlib import Path
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# Importa config para buscar credenciais
try:
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from config import GOOGLE_EMAIL, GOOGLE_SENHA
except ImportError:
    GOOGLE_EMAIL = None
    GOOGLE_SENHA = None


class TokenManager:
    """Gerenciador de token com verificação de expiração"""
    
    def __init__(self, token_file='token_data.json'):
        self.token_file = Path(__file__).parent.parent / token_file
        self.status_file = Path(__file__).parent.parent / 'token_status.json'
        self.token_data = self._carregar_token_data()
    
    def _carregar_token_data(self):
        """Carrega dados do token do arquivo JSON"""
        if self.token_file.exists():
            with open(self.token_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'token': None, 'criado_em': None, 'expira_em': None}
    
    def _salvar_token_data(self):
        """Salva dados do token no arquivo JSON"""
        with open(self.token_file, 'w', encoding='utf-8') as f:
            json.dump(self.token_data, indent=4, fp=f)
    
    def _salvar_status(self, sucesso, erro=None):
        """Salva o status da última renovação"""
        status = {
            'ultima_tentativa': datetime.now().isoformat(),
            'sucesso': sucesso,
            'erro': erro
        }
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=4)
    
    def atualizar_token(self, novo_token):
        """Atualiza o token no sistema"""
        agora = datetime.now()
        expira = agora + timedelta(hours=24)
        
        self.token_data = {
            'token': novo_token,
            'criado_em': agora.isoformat(),
            'expira_em': expira.isoformat()
        }
        
        self._salvar_token_data()
        self._atualizar_config_py(novo_token)
        
        print(f"✅ Token atualizado com sucesso!")
        print(f"📅 Criado em: {agora.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"⏰ Expira em: {expira.strftime('%d/%m/%Y %H:%M:%S')}")
        
        return True
    
    def _atualizar_config_py(self, novo_token):
        """Atualiza o token no arquivo config.py"""
        config_path = Path(__file__).parent.parent / 'config.py'
        
        if not config_path.exists():
            print("⚠️  Arquivo config.py não encontrado!")
            return False
        
        with open(config_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        import re
        padrao = r'ACCESS_TOKEN = "[^"]*"'
        novo_conteudo = re.sub(padrao, f'ACCESS_TOKEN = "{novo_token}"', conteudo)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        
        print("✅ Arquivo config.py atualizado")
        return True
    
    def validar_token(self, token):
        """Valida se o token funciona"""
        url = "https://api.smartthings.com/v1/devices"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print("✅ Token validado com sucesso!")
                return True
            elif response.status_code == 401:
                print("❌ Token inválido ou expirado!")
                return False
            else:
                print(f"⚠️  Resposta inesperada: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao validar token: {e}")
            return False


class RenovadorTokenSmartThings:
    """Automatiza a renovação completa do token SmartThings via Google"""
    
    def __init__(self, email=None, senha=None):
        # Usa credenciais passadas ou busca do config.py
        self.email = email or GOOGLE_EMAIL
        self.senha = senha or GOOGLE_SENHA
        self.driver = None
        self.token_manager = TokenManager()
    
    def _iniciar_navegador(self):
        """Inicializa o navegador Edge"""
        print("🌐 Iniciando navegador Edge...")
        
        edge_options = Options()
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        edge_options.add_argument('--window-size=1920,1080')
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        edge_options.use_chromium = True
        
        try:
            # Tenta usar o Edge diretamente (driver já instalado no sistema)
            self.driver = webdriver.Edge(options=edge_options)
            self.driver.implicitly_wait(10)
            print("✅ Navegador Edge iniciado")
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar Edge: {e}")
            print("   Tentando com msedgedriver do PATH...")
            try:
                # Tenta com service explícito
                service = Service("msedgedriver.exe")
                self.driver = webdriver.Edge(service=service, options=edge_options)
                self.driver.implicitly_wait(10)
                print("✅ Navegador Edge iniciado")
                return True
            except Exception as e2:
                print(f"❌ Erro final: {e2}")
                print("   💡 Instale o Edge WebDriver manualmente ou use Chrome")
                return False
    
    def _fazer_login_google(self):
        """Faz login via Google no SmartThings"""
        print("🔐 Fazendo login via Google...")
        
        try:
            self.driver.get("https://account.smartthings.com/login")
            time.sleep(3)
            
            janela_principal = self.driver.current_window_handle
            wait = WebDriverWait(self.driver, 30)
            
            # Clica no botão do Google
            print("   → Clicando em 'Entrar com o Google'...")
            google_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Google')] | //a[contains(., 'Google')]"))
            )
            google_button.click()
            time.sleep(4)
            
            # Troca para popup do Google
            wait.until(lambda d: len(d.window_handles) > 1)
            for janela in self.driver.window_handles:
                if janela != janela_principal:
                    self.driver.switch_to.window(janela)
                    break
            
            time.sleep(2)
            
            # Fluxo normal: preenche email
            print("   → Preenchendo email...")
            email_field = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
            email_field.send_keys(self.email)
            time.sleep(1)
            
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Avançar')]] | //button[@id='identifierNext']"))
            )
            next_button.click()
            time.sleep(3)
            
            # Preenche senha
            print("   → Preenchendo senha...")
            senha_field = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='password' or @name='Passwd']"))
            )
            senha_field.send_keys(self.senha)
            time.sleep(1)
            
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Avançar')]] | //button[@id='passwordNext']"))
            )
            next_button.click()
            time.sleep(8)
            
            # Volta para janela principal
            if len(self.driver.window_handles) == 1:
                self.driver.switch_to.window(self.driver.window_handles[0])
            
            time.sleep(3)
            
            # Volta para janela principal
            if len(self.driver.window_handles) == 1:
                self.driver.switch_to.window(self.driver.window_handles[0])
            
            time.sleep(3)
            current_url = self.driver.current_url
            if ("account.smartthings.com" in current_url or "my.smartthings.com" in current_url) and "login" not in current_url.lower():
                print("✅ Login realizado com sucesso")
                return True
            
            return False
                
        except Exception as e:
            print(f"❌ Erro durante login: {e}")
            return False
    
    def _gerar_e_capturar_token(self):
        """Gera e captura o token na página do SmartThings"""
        print("🔑 Gerando novo token...")
        
        try:
            self.driver.get("https://account.smartthings.com/tokens")
            time.sleep(3)
            
            wait = WebDriverWait(self.driver, 20)
            
            # Elimina tokens existentes
            print("   → Verificando tokens existentes...")
            delete_buttons = self.driver.find_elements(By.XPATH, "//button[@data-testid='delete-btn']")
            for i, btn in enumerate(delete_buttons, 1):
                try:
                    btn.click()
                    time.sleep(1)
                    confirm_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='confirm-delete-btn']"))
                    )
                    confirm_button.click()
                    print(f"   ✓ Token {i} eliminado")
                    time.sleep(2)
                except:
                    pass
            
            # Clica em "Gerar novo token"
            generate_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'token-new-btn')]"))
            )
            generate_button.click()
            print("   ✓ Clicou em 'Gerar novo token'")
            time.sleep(2)
            
            # Preenche nome
            token_name_field = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
            )
            token_name = f"AppTvs_Auto_{int(time.time())}"
            token_name_field.send_keys(token_name)
            print(f"   ✓ Nome: {token_name}")
            time.sleep(1)
            
            # Marca checkbox devices
            devices_checkbox = wait.until(
                EC.element_to_be_clickable((By.ID, "create_token.groups.devices-checkbox"))
            )
            if not devices_checkbox.is_selected():
                devices_checkbox.click()
                print("   ✓ Permissões marcadas")
            time.sleep(1)
            
            # Clica em "Gerar Token"
            submit_button = wait.until(EC.element_to_be_clickable((By.ID, "submit")))
            submit_button.click()
            print("   ✓ Token sendo gerado...")
            time.sleep(3)
            
            # Captura o token
            print("   → Capturando token...")
            token_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'w-75')]"))
            )
            novo_token = token_element.text.replace('Copiar token', '').strip()
            
            if novo_token and len(novo_token) > 20:
                print(f"✅ Token capturado: {novo_token[:10]}...{novo_token[-10:]}")
                return novo_token
            
            return None
                
        except Exception as e:
            print(f"❌ Erro ao gerar token: {e}")
            return None
    
    def renovar(self):
        """Executa o processo completo de renovação"""
        print("\n" + "="*60)
        print("🤖 RENOVAÇÃO AUTOMÁTICA DE TOKEN SMARTTHINGS")
        print("="*60 + "\n")
        
        if not self.email or not self.senha:
            erro = "Credenciais não configuradas"
            print(f"❌ {erro}")
            self.token_manager._salvar_status(False, erro)
            return False
        
        try:
            if not self._iniciar_navegador():
                erro = "Falha ao iniciar navegador Edge"
                self.token_manager._salvar_status(False, erro)
                return False
            
            if not self._fazer_login_google():
                erro = "Falha no login via Google"
                print(f"\n❌ {erro}")
                self.token_manager._salvar_status(False, erro)
                return False
            
            novo_token = self._gerar_e_capturar_token()
            
            if not novo_token:
                erro = "Não foi possível gerar/capturar o token"
                print(f"\n❌ {erro}")
                self.token_manager._salvar_status(False, erro)
                return False
            
            print("\n🔄 Validando token...")
            if self.token_manager.validar_token(novo_token):
                self.token_manager.atualizar_token(novo_token)
                self.token_manager._salvar_status(True)
                print("\n" + "="*60)
                print("✅ TOKEN RENOVADO COM SUCESSO!")
                print("="*60)
                return True
            else:
                erro = "Token gerado mas validação falhou"
                print(f"\n❌ {erro}")
                self.token_manager._salvar_status(False, erro)
                return False
                
        except Exception as e:
            erro = str(e)
            print(f"\n❌ Erro: {erro}")
            self.token_manager._salvar_status(False, erro)
            return False
            
        finally:
            if self.driver:
                print("\n🔒 Fechando navegador...")
                self.driver.quit()


def agendar_renovacao():
    """Agenda renovação automática diária"""
    print("\n" + "="*60)
    print("⏰ CONFIGURAÇÃO DE AGENDAMENTO")
    print("="*60 + "\n")
    
    horario = input("Digite o horário para renovação diária (HH:MM, ex: 02:00): ").strip()
    
    try:
        # Valida formato
        datetime.strptime(horario, "%H:%M")
        
        renovador = RenovadorTokenSmartThings()
        
        # Agenda a tarefa
        schedule.every().day.at(horario).do(renovador.renovar)
        
        print(f"\n✅ Renovação agendada para todo dia às {horario}")
        print("🔄 O script ficará executando em segundo plano...")
        print("   Pressione Ctrl+C para parar\n")
        
        # Executa uma vez imediatamente
        print("🚀 Executando primeira renovação agora...\n")
        renovador.renovar()
        
        # Loop de agendamento
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto
            
    except ValueError:
        print("❌ Horário inválido! Use o formato HH:MM (ex: 02:00)")
    except KeyboardInterrupt:
        print("\n\n⏹️  Agendamento interrompido pelo usuário")


if __name__ == "__main__":
    import sys
    
    renovador = RenovadorTokenSmartThings()
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--agendar', '-a']:
        agendar_renovacao()
    else:
        renovador.renovar()
