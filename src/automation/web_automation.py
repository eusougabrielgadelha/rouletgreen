"""
Módulo de automação web usando Selenium
"""
import time
import re
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import sys
import os

# Tenta importar undetected-chromedriver (melhor para bypass do Cloudflare)
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False
    print("[AVISO] undetected-chromedriver não instalado. Execute: pip install undetected-chromedriver")

# Adiciona o diretório raiz ao path para importar config
root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, os.path.abspath(root_dir))
from config import config


class BlazeAutomation:
    def __init__(self, headless: bool = False):
        self.driver = None
        self.headless = headless
        self.wait_time = config.WAIT_TIME
        self.last_results_hash = None
        self.last_timer_text = None
        self.wait = None  # WebDriverWait instance
        
        # Estado do login
        self.is_logged_in = False
        self.login_attempted = False
        self.last_activity_time = time.time()
        
        # Cache de resultados para performance
        self._results_cache = {
            'timestamp': 0,
            'results': [],
            'cache_duration': 0.5  # Cache por 0.5 segundos
        }
    
    def init_driver(self):
        """Inicializa o driver do Chrome com técnicas avançadas de bypass do Cloudflare"""
        try:
            # Detecta qual navegador está disponível e verifica se é executável
            chrome_binary = None
            chrome_paths = [
                '/usr/bin/google-chrome-stable',
                '/usr/bin/google-chrome',
                '/usr/bin/chromium-browser',
                '/usr/bin/chromium',
                '/snap/bin/chromium',
            ]
            
            # Primeiro verifica se os caminhos diretos existem e são executáveis
            for path in chrome_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    # Tenta executar para verificar se realmente funciona
                    try:
                        import subprocess
                        # Testa se consegue executar o Chrome
                        test_result = subprocess.run(
                            [path, '--headless', '--disable-gpu', '--no-sandbox', '--version'],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        if test_result.returncode == 0:
                            chrome_binary = path
                            print(f"[INFO] Navegador encontrado e testado: {chrome_binary}")
                            print(f"[INFO] Versão: {test_result.stdout.strip()}")
                            break
                        else:
                            print(f"[AVISO] Chrome encontrado em {path} mas não conseguiu executar")
                    except Exception as e:
                        print(f"[AVISO] Erro ao testar Chrome em {path}: {e}")
                        # Ainda assim, tenta usar se o arquivo existe
                        chrome_binary = path
                        print(f"[INFO] Navegador encontrado (não testado): {chrome_binary}")
                        break
            
            # Se não encontrou, tenta detectar via which
            if not chrome_binary:
                try:
                    import subprocess
                    for cmd in ['google-chrome-stable', 'google-chrome', 'chromium-browser', 'chromium']:
                        result = subprocess.run(['which', cmd], 
                                              capture_output=True, text=True, timeout=2)
                        if result.returncode == 0:
                            found_path = result.stdout.strip()
                            # Verifica se o arquivo existe e é executável
                            if os.path.exists(found_path) and os.access(found_path, os.X_OK):
                                # Testa se funciona
                                try:
                                    test_result = subprocess.run(
                                        [found_path, '--headless', '--disable-gpu', '--no-sandbox', '--version'],
                                        capture_output=True,
                                        text=True,
                                        timeout=10
                                    )
                                    if test_result.returncode == 0:
                                        chrome_binary = found_path
                                        print(f"[INFO] Navegador encontrado via which e testado: {chrome_binary}")
                                        break
                                    else:
                                        print(f"[AVISO] Chrome encontrado via which mas não executou: {found_path}")
                                except:
                                    # Se não conseguiu testar, usa mesmo assim
                                    chrome_binary = found_path
                                    print(f"[INFO] Navegador encontrado via which (não testado): {chrome_binary}")
                                    break
                except:
                    pass
            
            # Se ainda não encontrou, avisa
            if not chrome_binary:
                print("[AVISO] Chrome/Chromium não encontrado nos caminhos padrão")
                print("[INFO] Tente instalar: sudo apt install chromium-browser -y")
                print("[INFO] Ou instalar dependências: sudo apt install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libxshmfence1 libxss1 libgconf-2-4 libpangocairo-1.0-0 libatk1.0-0 libcairo-gobject2 libgtk-3-0 libgdk-pixbuf2.0-0")
            
            # Prioriza usar undetected-chromedriver se disponível (melhor para bypass)
            # Verifica novamente se está disponível (pode ter sido instalado após import inicial)
            try:
                import undetected_chromedriver as uc
                UC_AVAILABLE_NOW = True
            except ImportError:
                UC_AVAILABLE_NOW = False
            
            if UC_AVAILABLE or UC_AVAILABLE_NOW:
                print("[INFO] Usando undetected-chromedriver para melhor bypass do Cloudflare...")
                try:
                    options = uc.ChromeOptions()
                    
                    if self.headless:
                        options.add_argument("--headless=new")
                    
                    # Especifica o binário do Chrome se encontrado
                    if chrome_binary:
                        options.binary_location = chrome_binary
                        print(f"[INFO] Usando Chrome em: {chrome_binary}")
                    
                    # User agent realista e atualizado
                    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
                    
                    # Configurações para parecer mais humano
                    options.add_argument("--window-size=1920,1080")
                    options.add_argument("--start-maximized")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--disable-software-rasterizer")
                    options.add_argument("--disable-extensions")
                    options.add_argument("--disable-setuid-sandbox")
                    options.add_argument("--disable-web-security")
                    options.add_argument("--disable-features=VizDisplayCompositor")
                    # Para servidor headless
                    options.add_argument("--remote-debugging-port=9222")
                    options.add_argument("--disable-background-timer-throttling")
                    options.add_argument("--disable-backgrounding-occluded-windows")
                    options.add_argument("--disable-renderer-backgrounding")
                    
                    # Desabilita notificações
                    prefs = {
                        "profile.default_content_setting_values.notifications": 2,
                        "profile.default_content_setting_values.geolocation": 2,
                        "credentials_enable_service": False,
                        "profile.password_manager_enabled": False
                    }
                    options.add_experimental_option("prefs", prefs)
                    
                    # Inicializa undetected-chromedriver com timeout maior
                    self.driver = uc.Chrome(
                        options=options,
                        version_main=None,  # Auto-detecta versão do Chrome
                        use_subprocess=True,
                        driver_executable_path=None,
                        timeout=60  # Timeout maior para servidor headless
                    )
                    
                    print("[SUCCESS] undetected-chromedriver inicializado com sucesso!")
                    
                    # Injeta scripts adicionais de stealth
                    self._inject_stealth_scripts()
                    
                    self.wait = WebDriverWait(self.driver, self.wait_time)
                    
                    # Injeta MutationObserver para detectar mudanças no DOM
                    self._inject_dom_observer()
                    
                    return self.driver
                    
                except Exception as e:
                    print(f"[AVISO] Erro ao usar undetected-chromedriver: {e}")
                    print("[INFO] Tentando método padrão do Selenium...")
            
            # Método padrão (fallback)
            print("[INFO] Usando método padrão do Selenium com técnicas de stealth...")
            chrome_options = Options()
            
            # Especifica o binário do Chrome se encontrado e válido
            # IMPORTANTE: Verifica se o arquivo realmente existe e é executável
            if chrome_binary:
                if not os.path.exists(chrome_binary):
                    print(f"[AVISO] Chrome não encontrado no caminho: {chrome_binary}")
                    chrome_binary = None
                elif not os.access(chrome_binary, os.X_OK):
                    print(f"[AVISO] Chrome encontrado mas não é executável: {chrome_binary}")
                    print("[INFO] Tentando corrigir permissões...")
                    try:
                        os.chmod(chrome_binary, 0o755)
                        if os.access(chrome_binary, os.X_OK):
                            chrome_options.binary_location = chrome_binary
                            print(f"[SUCCESS] Permissões corrigidas, usando: {chrome_binary}")
                        else:
                            print("[AVISO] Não foi possível corrigir permissões")
                            chrome_binary = None
                    except Exception as e:
                        print(f"[AVISO] Erro ao corrigir permissões: {e}")
                        chrome_binary = None
                else:
                    chrome_options.binary_location = chrome_binary
                    print(f"[INFO] Usando Chrome em: {chrome_binary}")
                    # Verifica se o Chrome realmente funciona
                    try:
                        import subprocess
                        result = subprocess.run([chrome_binary, '--version'], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            print(f"[INFO] Chrome versão: {result.stdout.strip()}")
                        else:
                            print(f"[AVISO] Chrome não respondeu corretamente")
                    except Exception as e:
                        print(f"[AVISO] Erro ao verificar Chrome: {e}")
            
            if not chrome_binary:
                print("[AVISO] Chrome não encontrado ou não executável")
                print("[INFO] Tentando continuar sem especificar binário...")
                print("[INFO] O Selenium tentará encontrar o Chrome automaticamente")
            
            if self.headless:
                chrome_options.add_argument("--headless=new")
            
            # Opções de segurança e compatibilidade (essenciais para servidor headless)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-setuid-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            # Para servidor headless sem display
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Opções para suprimir erros de GPU/Virtualização
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-gpu-sandbox")
            chrome_options.add_argument("--disable-accelerated-2d-canvas")
            chrome_options.add_argument("--disable-accelerated-video-decode")
            
            # Suprime erros do DevTools e logging
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--silent")
            
            # Desabilita serviços do Google
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-breakpad")
            chrome_options.add_argument("--disable-client-side-phishing-detection")
            chrome_options.add_argument("--disable-component-extensions-with-background-pages")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-hang-monitor")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-prompt-on-repost")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--disable-translate")
            chrome_options.add_argument("--disable-web-resources")
            chrome_options.add_argument("--metrics-recording-only")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--safebrowsing-disable-auto-update")
            chrome_options.add_argument("--password-store=basic")
            chrome_options.add_argument("--use-mock-keychain")
            
            # User agent atualizado e realista
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
            
            # IMPORTANTE: Remove flags de automação
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Desabilita notificações e permissões
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                },
                "profile.managed_default_content_settings": {
                    "images": 1
                },
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Tenta instalar o ChromeDriver usando webdriver-manager
            try:
                driver_path = ChromeDriverManager().install()
                
                # Verifica se o caminho aponta para o executável correto
                # O ChromeDriverManager às vezes retorna arquivos errados (como THIRD_PARTY_NOTICES)
                from pathlib import Path
                driver_path_obj = Path(driver_path)
                
                # Se o caminho retornado não é um executável válido, procura pelo executável
                valid_driver = None
                
                # Primeiro verifica se o arquivo retornado é válido
                if driver_path_obj.is_file() and os.access(driver_path, os.X_OK):
                    # Verifica se não é um arquivo de texto (THIRD_PARTY_NOTICES, LICENSE, etc)
                    if not driver_path.endswith(('.txt', '.md', '.json', '.LICENSE', '.NOTICES')):
                        # Tenta executar para verificar se é binário válido
                        try:
                            import subprocess
                            result = subprocess.run(['file', driver_path], 
                                                  capture_output=True, text=True, timeout=2)
                            if 'executable' in result.stdout.lower() or 'binary' in result.stdout.lower():
                                valid_driver = driver_path
                        except:
                            # Se file não estiver disponível, assume que é válido se tiver permissão de execução
                            valid_driver = driver_path
                
                # Se não encontrou um executável válido, procura no diretório
                if not valid_driver:
                    driver_dir = driver_path_obj.parent
                    
                    # Procura pelo executável chromedriver (Linux)
                    # Primeiro procura no diretório retornado
                    for name in ['chromedriver', 'chromedriver.exe']:
                        exe_path = driver_dir / name
                        if exe_path.exists():
                            # Ignora arquivos de texto/documentação
                            if not exe_path.name.upper().endswith(('.TXT', '.MD', '.LICENSE', '.NOTICES')):
                                try:
                                    os.chmod(str(exe_path), 0o755)  # Torna executável
                                    if os.access(str(exe_path), os.X_OK):
                                        # Verifica se é realmente um binário
                                        try:
                                            import subprocess
                                            result = subprocess.run(['file', str(exe_path)], 
                                                                  capture_output=True, text=True, timeout=2)
                                            if 'executable' in result.stdout.lower() or 'binary' in result.stdout.lower():
                                                valid_driver = str(exe_path)
                                                break
                                        except:
                                            # Se file não funcionar, tenta usar mesmo assim
                                            valid_driver = str(exe_path)
                                            break
                                except:
                                    continue
                    
                    # Se ainda não encontrou, procura recursivamente no diretório pai
                    if not valid_driver:
                        parent_dir = driver_dir.parent if driver_dir.parent != driver_dir else driver_dir
                        for root, dirs, files in os.walk(parent_dir):
                            for file in files:
                                # Ignora arquivos de documentação
                                if file.upper().endswith(('.TXT', '.MD', '.LICENSE', '.NOTICES', '.JSON')):
                                    continue
                                
                                if file == 'chromedriver' or (file.startswith('chromedriver') and file.endswith('.exe')):
                                    full_path = os.path.join(root, file)
                                    try:
                                        os.chmod(full_path, 0o755)
                                        if os.access(full_path, os.X_OK):
                                            # Verifica se é binário
                                            try:
                                                import subprocess
                                                result = subprocess.run(['file', full_path], 
                                                                      capture_output=True, text=True, timeout=2)
                                                if 'executable' in result.stdout.lower() or 'binary' in result.stdout.lower():
                                                    valid_driver = full_path
                                                    break
                                            except:
                                                valid_driver = full_path
                                                break
                                    except:
                                        continue
                            if valid_driver:
                                break
                
                # Se ainda não encontrou, tenta usar chromedriver do sistema
                if not valid_driver:
                    try:
                        import subprocess
                        result = subprocess.run(['which', 'chromedriver'], 
                                              capture_output=True, text=True, timeout=2)
                        if result.returncode == 0:
                            system_driver = result.stdout.strip()
                            if os.path.exists(system_driver) and os.access(system_driver, os.X_OK):
                                valid_driver = system_driver
                                print(f"[INFO] Usando ChromeDriver do sistema: {valid_driver}")
                    except:
                        pass
                
                if valid_driver and os.path.exists(valid_driver) and os.access(valid_driver, os.X_OK):
                    service = Service(valid_driver)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    print(f"[SUCCESS] ChromeDriver encontrado: {valid_driver}")
                else:
                    raise Exception(f"ChromeDriver executável não encontrado. Caminho retornado: {driver_path}")
            except Exception as e:
                print(f"Aviso: Erro ao usar ChromeDriverManager: {e}")
                print("Tentando usar ChromeDriver do sistema...")
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                except Exception as e2:
                    # Diagnóstico adicional detalhado
                    error_msg = str(e2)
                    diagnostics = []
                    
                    # Verifica se o Chrome realmente existe e funciona
                    if chrome_binary:
                        try:
                            import subprocess
                            # Testa execução básica
                            test_result = subprocess.run(
                                [chrome_binary, '--headless', '--disable-gpu', '--no-sandbox', '--version'],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            if test_result.returncode != 0:
                                diagnostics.append(f"- Chrome não consegue executar (código {test_result.returncode})")
                                diagnostics.append(f"  Erro: {test_result.stderr[:200]}")
                            else:
                                diagnostics.append(f"- Chrome executou com sucesso: {test_result.stdout.strip()}")
                        except Exception as test_error:
                            diagnostics.append(f"- Erro ao testar Chrome: {test_error}")
                    
                    # Verifica dependências faltando (verifica múltiplos nomes possíveis)
                    try:
                        import subprocess
                        missing_deps = []
                        # Verifica com nomes antigos e novos (Ubuntu 24.04+ usa t64)
                        deps_to_check = {
                            'libnss3': ['libnss3'],
                            'libatk-bridge2.0-0': ['libatk-bridge2.0-0', 'libatk-bridge2.0-0t64'],
                            'libgbm1': ['libgbm1'],
                            'libxss1': ['libxss1'],
                            'libgtk-3-0': ['libgtk-3-0', 'libgtk-3-0t64']
                        }
                        for key, pkg_names in deps_to_check.items():
                            found = False
                            for pkg in pkg_names:
                                result = subprocess.run(
                                    ['dpkg', '-l', pkg],
                                    capture_output=True,
                                    text=True,
                                    timeout=2
                                )
                                if 'ii' in result.stdout:  # 'ii' = instalado corretamente
                                    found = True
                                    break
                            if not found:
                                missing_deps.append(pkg_names[0])  # Adiciona o nome padrão
                        if missing_deps:
                            diagnostics.append(f"- Dependências faltando: {', '.join(missing_deps)}")
                            diagnostics.append(f"  Instale com: sudo apt install -y {' '.join(missing_deps)}")
                    except:
                        pass
                    
                    # Verifica se undetected-chromedriver está instalado
                    try:
                        import undetected_chromedriver as uc
                        diagnostics.append("- undetected-chromedriver está instalado")
                    except ImportError:
                        diagnostics.append("- undetected-chromedriver não está instalado")
                        diagnostics.append("  Instale com: pip install undetected-chromedriver")
                    
                    raise Exception(
                        f"Erro ao inicializar ChromeDriver.\n\n"
                        f"Detalhes:\n"
                        f"1. Erro com ChromeDriverManager: {str(e)[:200]}\n"
                        f"2. Erro sem service: {str(e2)[:200]}\n"
                        + ("\n".join(diagnostics) if diagnostics else "\n- Nenhum diagnóstico adicional disponível") + "\n\n"
                        f"Soluções:\n"
                        f"1. Instalar dependências:\n"
                        f"   sudo apt install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libxshmfence1 libxss1 libgconf-2-4 libpangocairo-1.0-0 libatk1.0-0 libcairo-gobject2 libgtk-3-0 libgdk-pixbuf2.0-0 xvfb\n"
                        f"2. Testar Chrome manualmente:\n"
                        f"   /usr/bin/google-chrome-stable --headless --disable-gpu --no-sandbox --version\n"
                        f"3. Instalar undetected-chromedriver:\n"
                        f"   pip install undetected-chromedriver\n"
                        f"4. Limpar cache:\n"
                        f"   rm -rf ~/.wdm ~/.cache/selenium"
                    )
            
            # Injeta scripts avançados de stealth
            self._inject_stealth_scripts()
            
            try:
                self.driver.maximize_window()
            except:
                pass
            
            # Inicializa WebDriverWait
            self.wait = WebDriverWait(self.driver, timeout=30)
            
            # Injeta MutationObserver para detectar mudanças no DOM
            self._inject_dom_observer()
            
            return self.driver
            
        except Exception as e:
            error_msg = str(e)
            if "WinError 193" in error_msg or "não é um aplicativo Win32 válido" in error_msg:
                raise Exception(
                    "Erro ao inicializar ChromeDriver. Possíveis causas:\n"
                    "1. ChromeDriver incompatível ou corrompido\n"
                    "2. Arquitetura incompatível (32-bit vs 64-bit)\n"
                    "3. Chrome não está instalado\n\n"
                    "Soluções:\n"
                    "- Verifique se o Google Chrome está instalado\n"
                    "- Tente reinstalar o ChromeDriver: pip install --upgrade webdriver-manager\n"
                    "- Ou baixe manualmente o ChromeDriver compatível com sua versão do Chrome"
                )
            else:
                raise Exception(f"Erro ao inicializar navegador: {error_msg}")
    
    def _inject_stealth_scripts(self):
        """Injeta scripts JavaScript avançados para evitar detecção de automação"""
        try:
            # Script principal de stealth (executa antes de qualquer página carregar)
            stealth_script = """
            // Remove propriedades que indicam automação
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Sobrescreve plugins para parecer mais real
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Sobrescreve languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
            
            // Remove propriedade automation do Chrome
            window.navigator.chrome = {
                runtime: {}
            };
            
            // Permissões
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // WebGL Vendor e Renderer (evita fingerprinting)
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.call(this, parameter);
            };
            
            // Canvas fingerprinting protection (retorna dados consistentes)
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function() {
                const context = this.getContext('2d');
                if (context) {
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i] = imageData.data[i] ^ 0x01;
                    }
                    context.putImageData(imageData, 0, 0);
                }
                return originalToDataURL.apply(this, arguments);
            };
            
            // AudioContext fingerprinting protection
            const originalCreateOscillator = AudioContext.prototype.createOscillator;
            AudioContext.prototype.createOscillator = function() {
                const oscillator = originalCreateOscillator.apply(this, arguments);
                const originalFrequency = oscillator.frequency.value;
                Object.defineProperty(oscillator.frequency, 'value', {
                    get: () => originalFrequency + Math.random() * 0.0001
                });
                return oscillator;
            };
            
            // Remove propriedades de automação do window
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            
            // Override console.debug para evitar detecção
            const originalDebug = console.debug;
            console.debug = function() {
                // Não faz nada (evita logs de automação)
            };
            """
            
            # Injeta o script usando CDP (Chrome DevTools Protocol)
            try:
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': stealth_script
                })
            except:
                # Fallback: injeta via JavaScript normal
                try:
                    self.driver.execute_script(stealth_script)
                except:
                    pass
            
            # Script adicional para esconder automação após página carregar
            additional_stealth = """
            // Remove propriedade webdriver novamente (alguns sites verificam após carregar)
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
            
            // Adiciona propriedades que navegadores reais têm
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
            
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
            
            // Override getBattery (alguns sites verificam)
            if (navigator.getBattery) {
                navigator.getBattery = () => Promise.resolve({
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: Infinity,
                    level: 1
                });
            }
            """
            
            try:
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': additional_stealth
                })
            except:
                pass
            
            print("[SUCCESS] Scripts de stealth injetados com sucesso!")
            
        except Exception as e:
            print(f"[AVISO] Erro ao injetar scripts de stealth: {e}")
            # Continua mesmo se falhar
    
    def wait_for_element(self, by, value, timeout=None):
        """Aguarda um elemento aparecer na página"""
        if timeout is None:
            timeout = self.wait_time
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_clickable(self, by, value, timeout=None):
        """Aguarda um elemento ficar clicável"""
        if timeout is None:
            timeout = self.wait_time
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    
    def accept_cookies(self):
        """Aceita os cookies do site usando seletores específicos do Blaze"""
        try:
            time.sleep(2)
            
            # Estratégia 1: Procura pelo modal específico de cookies/políticas
            try:
                # Seletores específicos baseados no HTML fornecido
                modal_selectors = [
                    "#policy-regulation-popup",
                    "div#policy-regulation-popup.modal-sm",
                    "div.policy-regulation-container",
                    "div.modal-sm"
                ]
                
                modal_found = False
                for selector in modal_selectors:
                    try:
                        modal = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if modal and any(m.is_displayed() for m in modal):
                            modal_found = True
                            break
                    except:
                        continue
                
                if not modal_found:
                    # Verifica via JavaScript se o modal existe
                    modal_exists = self.driver.execute_script("""
                        var modal = document.getElementById('policy-regulation-popup');
                        if (modal) {
                            var style = window.getComputedStyle(modal);
                            return style.display !== 'none' && style.visibility !== 'hidden';
                        }
                        return false;
                    """)
                    if not modal_exists:
                        print("[INFO] Modal de cookies não encontrado (pode já estar aceito)")
                        return False
            except Exception as e:
                print(f"[AVISO] Erro ao verificar modal de cookies: {e}")
            
            # Estratégia 2: Procura pelo botão "ACEITAR TODOS OS COOKIES" (seletor específico)
            try:
                # Seletores específicos baseados no HTML
                button_selectors = [
                    "#policy-regulation-popup button[data-testid]",
                    "#policy-regulation-popup button.shared-button-custom",
                    "div.policy-regulation-button-container button",
                    "button:contains('ACEITAR TODOS OS COOKIES')"
                ]
                
                cookies_button = None
                
                # Tenta encontrar via CSS Selector
                for selector in button_selectors:
                    try:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for btn in buttons:
                            if btn.is_displayed() and btn.is_enabled():
                                text = btn.text.upper()
                                if "ACEITAR" in text or "COOKIES" in text or "ACCEPT" in text:
                                    cookies_button = btn
                                    break
                        if cookies_button:
                            break
                    except:
                        continue
                
                # Estratégia 3: Procura via XPath pelo texto exato
                if not cookies_button:
                    try:
                        buttons = self.driver.find_elements(By.XPATH,
                            "//button[contains(text(), 'ACEITAR TODOS OS COOKIES')] | "
                            "//button[contains(text(), 'Aceitar')] | "
                            "//button[contains(text(), 'Accept')] | "
                            "//button[contains(., 'COOKIES')]")
                        for btn in buttons:
                            if btn.is_displayed() and btn.is_enabled():
                                cookies_button = btn
                                break
                    except:
                        pass
                
                # Estratégia 4: Procura via JavaScript
                if not cookies_button:
                    try:
                        cookies_button = self.driver.execute_script("""
                            // Procura pelo botão dentro do modal de políticas
                            var modal = document.getElementById('policy-regulation-popup');
                            if (modal) {
                                var buttons = modal.querySelectorAll('button');
                                for (var i = 0; i < buttons.length; i++) {
                                    var btn = buttons[i];
                                    var text = (btn.textContent || btn.innerText || '').toUpperCase();
                                    var style = window.getComputedStyle(btn);
                                    if ((text.includes('ACEITAR') || text.includes('ACCEPT') || text.includes('COOKIES')) &&
                                        style.display !== 'none' && style.visibility !== 'hidden' && !btn.disabled) {
                                        return btn;
                                    }
                                }
                            }
                            // Procura em qualquer lugar
                            var allButtons = document.querySelectorAll('button');
                            for (var i = 0; i < allButtons.length; i++) {
                                var btn = allButtons[i];
                                var text = (btn.textContent || btn.innerText || '').toUpperCase();
                                var style = window.getComputedStyle(btn);
                                if ((text.includes('ACEITAR') || text.includes('ACCEPT')) &&
                                    text.includes('COOKIES') &&
                                    style.display !== 'none' && style.visibility !== 'hidden' && !btn.disabled) {
                                    return btn;
                                }
                            }
                            return null;
                        """)
                        if cookies_button and not hasattr(cookies_button, 'click'):
                            cookies_button = None
                    except Exception as e:
                        print(f"[AVISO] Erro ao buscar botão via JS: {e}")
                
                if cookies_button:
                    try:
                        # Scroll até o elemento
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", cookies_button)
                        time.sleep(0.5)
                        
                        # Aguarda ficar clicável
                        try:
                            WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable(cookies_button)
                            )
                        except:
                            pass
                        
                        # Clica no botão
                        cookies_button.click()
                        time.sleep(1)
                        print("[SUCCESS] Cookies aceitos com sucesso")
                        return True
                    except Exception as e:
                        print(f"[ERRO] Erro ao clicar no botão de cookies: {e}")
                else:
                    print("[AVISO] Botão de aceitar cookies não encontrado")
                    return False
                    
            except Exception as e:
                print(f"[ERRO] Erro ao procurar botão de cookies: {e}")
                return False
            
            return False
        except Exception as e:
            print(f"[ERRO] Erro ao aceitar cookies: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def confirm_age(self):
        """Confirma que tem mais de 18 anos"""
        try:
            time.sleep(2)
            
            # Procura por botões relacionados a idade
            age_buttons = self.driver.find_elements(By.XPATH,
                "//button[contains(text(), '18') or contains(text(), 'Tenho') or contains(text(), 'Sim') or contains(text(), 'Confirmar')]")
            
            if age_buttons:
                age_buttons[0].click()
                time.sleep(1)
                return True
            
            # Procura por elementos com texto relacionado
            age_elements = self.driver.find_elements(By.CSS_SELECTOR,
                "button[class*='age'], button[class*='confirm'], button[class*='18']")
            
            for elem in age_elements:
                if elem.is_displayed():
                    elem.click()
                    time.sleep(1)
                    return True
            
            return False
        except Exception as e:
            print(f"Erro ao confirmar idade: {e}")
            return False
    
    def login(self, email: str, password: str):
        """Realiza o login no site com múltiplas estratégias para o modal"""
        try:
            time.sleep(2)
            
            # Estratégia 1: Procura pelo botão de entrar/login na página principal (seletor específico do header)
            try:
                # Seletores específicos baseados no HTML fornecido
                login_link_selectors = [
                    "div.unauthed-buttons a.link",
                    "a.link:contains('Entrar')",
                    "div.routes a.link"
                ]
                
                login_button_found = False
                
                # Tenta encontrar o link "Entrar" no header
                for selector in login_link_selectors:
                    try:
                        links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for link in links:
                            if link.is_displayed() and "Entrar" in link.text:
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                                time.sleep(0.5)
                                link.click()
                                time.sleep(2)
                                login_button_found = True
                                break
                        if login_button_found:
                            break
                    except:
                        continue
                
                # Fallback: procura via XPath
                if not login_button_found:
                    login_buttons = self.driver.find_elements(By.XPATH,
                        "//a[contains(text(), 'Entrar')] | //button[contains(text(), 'Entrar')] | //a[@class='link']")
                    
                    for btn in login_buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                            time.sleep(0.5)
                            btn.click()
                            time.sleep(2)
                            login_button_found = True
                            break
            except Exception as e:
                print(f"[AVISO] Erro ao clicar no botão de login: {e}")
            
            # Estratégia 2: Aguarda o modal de login aparecer usando seletores específicos
            try:
                # Seletores específicos baseados no HTML fornecido
                modal_selectors = [
                    "div.modal-portal[data-modal-type='auth']",
                    "div.modal-portal",
                    "#auth-modal",
                    "div.modal-sm.modal-container",
                    "div.modal",
                    "form[data-testid='login-form-email']"
                ]
                
                modal_found = False
                for selector in modal_selectors:
                    try:
                        modal = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if modal.is_displayed():
                            modal_found = True
                            print(f"[INFO] Modal de login encontrado usando: {selector}")
                            break
                    except:
                        continue
                
                if not modal_found:
                    # Tenta usar JavaScript para encontrar o modal específico
                    modal_js = self.driver.execute_script("""
                        // Procura pelo modal de auth específico
                        var modal = document.querySelector('div.modal-portal[data-modal-type="auth"]');
                        if (modal) {
                            var style = window.getComputedStyle(modal);
                            if (style.display !== 'none' && style.visibility !== 'hidden') {
                                return modal;
                            }
                        }
                        // Fallback: procura por qualquer modal visível
                        var modals = document.querySelectorAll('div.modal, div.modal-portal, #auth-modal');
                        for (var i = 0; i < modals.length; i++) {
                            var style = window.getComputedStyle(modals[i]);
                            if (style.display !== 'none' && style.visibility !== 'hidden') {
                                return modals[i];
                            }
                        }
                        return null;
                    """)
                    if not modal_js:
                        print("[AVISO] Modal de login não encontrado, tentando continuar...")
                    else:
                        modal_found = True
            except Exception as e:
                print(f"[AVISO] Erro ao aguardar modal: {e}")
            
            # Aguarda um pouco para o modal carregar completamente
            time.sleep(2)
            
            # Estratégia 3: Interage com o Cloudflare Turnstile ANTES de preencher os campos
            try:
                print("[INFO] Verificando autenticação Cloudflare Turnstile...")
                
                # Verifica se existe o Turnstile
                turnstile_widget = self.driver.execute_script("""
                    // Verifica se existe o widget do Turnstile
                    var turnstileWidget = document.getElementById('turnstile-widget');
                    var turnstileContainer = document.querySelector('.turnstile-container');
                    return turnstileWidget || turnstileContainer;
                """)
                
                if turnstile_widget:
                    print("[INFO] Cloudflare Turnstile detectado, clicando primeiro...")
                    
                    # Tenta encontrar e clicar no widget do Turnstile (simula clique real)
                    try:
                        # Procura pelo widget do Turnstile
                        turnstile_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                            "#turnstile-widget, .turnstile-container, div[id*='turnstile']")
                        
                        if turnstile_elements:
                            turnstile_element = turnstile_elements[0]
                            
                            # Scroll até o elemento
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", turnstile_element)
                            time.sleep(0.5)
                            
                            # Simula clique real usando ActionChains (importante para passar pelo Cloudflare)
                            print("[INFO] Clicando no widget do Turnstile...")
                            actions = ActionChains(self.driver)
                            # Move o mouse até o elemento, pausa, e clica (simula comportamento humano)
                            actions.move_to_element(turnstile_element).pause(0.3).click().perform()
                            time.sleep(1)
                            
                            # Alternativamente, tenta clicar via JavaScript para garantir
                            try:
                                self.driver.execute_script("""
                                    var widget = document.getElementById('turnstile-widget');
                                    if (widget) {
                                        // Dispara evento de clique no widget
                                        var clickEvent = new MouseEvent('click', {
                                            view: window,
                                            bubbles: true,
                                            cancelable: true,
                                            clientX: widget.offsetLeft + widget.offsetWidth / 2,
                                            clientY: widget.offsetTop + widget.offsetHeight / 2
                                        });
                                        widget.dispatchEvent(clickEvent);
                                        
                                        // Também tenta clicar diretamente
                                        if (widget.click) {
                                            widget.click();
                                        }
                                    }
                                """)
                                time.sleep(1)
                            except:
                                pass
                            
                            print("[SUCCESS] Clique no Turnstile realizado")
                    except Exception as e:
                        print(f"[AVISO] Erro ao clicar no Turnstile: {e}")
                    
                    # Aguarda um pouco para o Turnstile processar o clique
                    time.sleep(1)
                else:
                    print("[INFO] Cloudflare Turnstile não detectado, continuando...")
            except Exception as e:
                print(f"[AVISO] Erro ao verificar Cloudflare Turnstile: {e}")
                # Continua mesmo se houver erro
            
            # Estratégia 4: Procura pelo campo de email com múltiplas estratégias
            email_input = None
            
            # Lista de seletores para email (específicos do Blaze)
            email_selectors = [
                "form[data-testid='login-form-email'] input[name='username']",  # Específico do Blaze
                "input[name='username']",  # Campo username no Blaze
                "input[type='email']",
                "input[name='email']",
                "input[id*='email' i]",
                "input[placeholder*='email' i]",
                "input[placeholder*='Email' i]",
                "input[placeholder*='E-mail' i]",
                "input[placeholder*='CPF' i]",  # Blaze aceita CPF ou email
                "input[autocomplete='email']",
                "input[data-testid*='email' i]"
            ]
            
            # Tenta encontrar usando seletores CSS
            for selector in email_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            email_input = elem
                            break
                    if email_input:
                        break
                except:
                    continue
            
            # Estratégia 5: Usa JavaScript para encontrar o campo de email
            if not email_input:
                try:
                    email_input = self.driver.execute_script("""
                        // Procura primeiro pelo input específico do Blaze (username)
                        var form = document.querySelector('form[data-testid="login-form-email"]');
                        if (form) {
                            var usernameInput = form.querySelector('input[name="username"]');
                            if (usernameInput) {
                                var style = window.getComputedStyle(usernameInput);
                                if (style.display !== 'none' && style.visibility !== 'hidden' && !usernameInput.disabled) {
                                    return usernameInput;
                                }
                            }
                        }
                        // Procura por input de email
                        var inputs = document.querySelectorAll('input[type="email"], input[name="username"], input[name*="email" i], input[id*="email" i], input[placeholder*="email" i], input[placeholder*="CPF" i]');
                        for (var i = 0; i < inputs.length; i++) {
                            var style = window.getComputedStyle(inputs[i]);
                            if (style.display !== 'none' && style.visibility !== 'hidden' && !inputs[i].disabled) {
                                return inputs[i];
                            }
                        }
                        // Tenta encontrar por texto de label (Blaze usa span.label)
                        var labels = document.querySelectorAll('span.label');
                        for (var i = 0; i < labels.length; i++) {
                            var labelText = (labels[i].textContent || '').toLowerCase();
                            if (labelText.includes('email') || labelText.includes('cpf')) {
                                var inputWrapper = labels[i].closest('.input-wrapper');
                                if (inputWrapper) {
                                    var input = inputWrapper.querySelector('input');
                                    if (input) {
                                        var style = window.getComputedStyle(input);
                                        if (style.display !== 'none' && style.visibility !== 'hidden' && !input.disabled) {
                                            return input;
                                        }
                                    }
                                }
                            }
                        }
                        return null;
                    """)
                    if email_input:
                        # Converte para WebElement se necessário
                        if not hasattr(email_input, 'send_keys'):
                            # Se retornou um elemento DOM, precisa encontrar via Selenium
                            email_input = None
                except Exception as e:
                    print(f"[AVISO] Erro ao buscar email via JS: {e}")
            
            # Estratégia 6: Tenta encontrar via XPath
            if not email_input:
                try:
                    email_elements = self.driver.find_elements(By.XPATH,
                        "//input[@type='email'] | //input[contains(@name, 'email')] | //input[contains(@id, 'email')] | //input[contains(@placeholder, 'email')]")
                    for elem in email_elements:
                        if elem.is_displayed() and elem.is_enabled():
                            email_input = elem
                            break
                except:
                    pass
            
            if not email_input:
                print("[ERRO] Campo de email não encontrado")
                return False
            
            # Aguarda o campo ficar interagível
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(email_input)
                )
            except:
                pass
            
            # Preenche o email com digitação letra por letra (simula digitação humana)
            try:
                print("[INFO] Preenchendo email letra por letra...")
                
                # Scroll até o elemento
                self.driver.execute_script("arguments[0].scrollIntoView(true);", email_input)
                time.sleep(0.5)
                
                # Clica no campo primeiro (simula interação humana)
                try:
                    # Usa ActionChains para clique real
                    actions = ActionChains(self.driver)
                    actions.move_to_element(email_input).click().perform()
                    time.sleep(0.3)
                except:
                    # Fallback: clique simples
                    email_input.click()
                    time.sleep(0.3)
                
                # Limpa o campo
                email_input.clear()
                time.sleep(0.2)
                
                # Digita letra por letra para simular digitação humana
                for char in email:
                    email_input.send_keys(char)
                    # Delay aleatório entre 0.05 e 0.15 segundos por letra
                    import random
                    time.sleep(random.uniform(0.05, 0.15))
                
                time.sleep(0.5)
                print("[SUCCESS] Email preenchido")
            except Exception as e:
                print(f"[ERRO] Erro ao preencher email: {e}")
                return False
            
            # Estratégia 7: Procura pelo campo de senha com múltiplas estratégias
            password_input = None
            
            # Lista de seletores para senha
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[id*='password' i]",
                "input[placeholder*='password' i]",
                "input[placeholder*='Password' i]",
                "input[placeholder*='Senha' i]",
                "input[autocomplete='current-password']",
                "input[data-testid*='password' i]"
            ]
            
            # Tenta encontrar usando seletores CSS
            for selector in password_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            password_input = elem
                            break
                    if password_input:
                        break
                except:
                    continue
            
            # Estratégia 8: Usa JavaScript para encontrar o campo de senha
            if not password_input:
                try:
                    password_input = self.driver.execute_script("""
                        // Procura por input de senha
                        var inputs = document.querySelectorAll('input[type="password"], input[name*="password" i], input[id*="password" i], input[placeholder*="password" i], input[placeholder*="senha" i]');
                        for (var i = 0; i < inputs.length; i++) {
                            var style = window.getComputedStyle(inputs[i]);
                            if (style.display !== 'none' && style.visibility !== 'hidden' && !inputs[i].disabled) {
                                return inputs[i];
                            }
                        }
                        return null;
                    """)
                    if password_input and not hasattr(password_input, 'send_keys'):
                        password_input = None
                except Exception as e:
                    print(f"[AVISO] Erro ao buscar senha via JS: {e}")
            
            # Estratégia 9: Tenta encontrar via XPath
            if not password_input:
                try:
                    password_elements = self.driver.find_elements(By.XPATH,
                        "//input[@type='password'] | //input[contains(@name, 'password')] | //input[contains(@id, 'password')] | //input[contains(@placeholder, 'password')] | //input[contains(@placeholder, 'senha')]")
                    for elem in password_elements:
                        if elem.is_displayed() and elem.is_enabled():
                            password_input = elem
                            break
                except:
                    pass
            
            if not password_input:
                print("[ERRO] Campo de senha não encontrado")
                return False
            
            # Aguarda o campo ficar interagível
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(password_input)
                )
            except:
                pass
            
            # Preenche a senha com digitação letra por letra (simula digitação humana)
            try:
                print("[INFO] Preenchendo senha letra por letra...")
                
                # Scroll até o elemento
                self.driver.execute_script("arguments[0].scrollIntoView(true);", password_input)
                time.sleep(0.5)
                
                # Clica no campo primeiro (simula interação humana)
                try:
                    # Usa ActionChains para clique real
                    actions = ActionChains(self.driver)
                    actions.move_to_element(password_input).click().perform()
                    time.sleep(0.3)
                except:
                    # Fallback: clique simples
                    password_input.click()
                    time.sleep(0.3)
                
                # Limpa o campo
                password_input.clear()
                time.sleep(0.2)
                
                # Digita letra por letra para simular digitação humana
                import random
                for char in password:
                    password_input.send_keys(char)
                    # Delay aleatório entre 0.05 e 0.15 segundos por letra
                    time.sleep(random.uniform(0.05, 0.15))
                
                time.sleep(0.5)
                print("[SUCCESS] Senha preenchida")
            except Exception as e:
                print(f"[ERRO] Erro ao preencher senha: {e}")
                return False
            
            # Aguarda um pouco para o Turnstile processar os campos preenchidos
            time.sleep(1)
            
            # Estratégia 10: Procura pelo botão de submit/login com múltiplas estratégias
            submit_button = None
            
            # Lista de seletores para botão de submit (específicos do Blaze)
            submit_selectors = [
                "form[data-testid='login-form-email'] button.red.submit",  # Específico do Blaze
                "form[data-testid='login-form-email'] button.submit",  # Específico do Blaze
                "button.red.submit.shared-button-custom",  # Específico do Blaze
                "button.submit.shared-button-custom",
                "button[type='submit']",
                "button[type='button'][contains(text(), 'Entrar')]",
                "button[type='button'][contains(text(), 'Login')]",
                "button[contains(@class, 'submit')]",
                "button[contains(@class, 'login')]",
                "button[contains(@class, 'signin')]",
                "button[data-testid*='submit' i]",
                "button[data-testid*='login' i]"
            ]
            
            # Tenta encontrar usando seletores CSS
            for selector in submit_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            submit_button = elem
                            break
                    if submit_button:
                        break
                except:
                    continue
            
            # Estratégia 11: Usa XPath para encontrar botão de submit
            if not submit_button:
                try:
                    submit_elements = self.driver.find_elements(By.XPATH,
                        "//button[@type='submit'] | //button[contains(text(), 'Entrar')] | //button[contains(text(), 'Login')] | //button[contains(text(), 'Sign in')] | //button[contains(., 'Entrar')]")
                    for elem in submit_elements:
                        if elem.is_displayed() and elem.is_enabled():
                            submit_button = elem
                            break
                except:
                    pass
            
            # Estratégia 12: Usa JavaScript para encontrar o botão de submit
            if not submit_button:
                try:
                    submit_button = self.driver.execute_script("""
                        // Procura primeiro pelo botão específico do Blaze dentro do form
                        var form = document.querySelector('form[data-testid="login-form-email"]');
                        if (form) {
                            var submitBtn = form.querySelector('button.red.submit, button.submit');
                            if (submitBtn) {
                                var style = window.getComputedStyle(submitBtn);
                                if (style.display !== 'none' && style.visibility !== 'hidden' && !submitBtn.disabled) {
                                    return submitBtn;
                                }
                            }
                        }
                        // Procura por botão de submit
                        var buttons = document.querySelectorAll('button[type="submit"], button.submit, button.red.submit');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = (buttons[i].textContent || buttons[i].innerText || '').toLowerCase();
                            var style = window.getComputedStyle(buttons[i]);
                            if ((text.includes('entrar') || text.includes('login') || text.includes('sign in') || buttons[i].classList.contains('submit')) &&
                                style.display !== 'none' && style.visibility !== 'hidden' && !buttons[i].disabled) {
                                return buttons[i];
                            }
                        }
                        return null;
                    """)
                    if submit_button and not hasattr(submit_button, 'click'):
                        submit_button = None
                except Exception as e:
                    print(f"[AVISO] Erro ao buscar botão via JS: {e}")
            
            # Estratégia 13: Aguarda o Cloudflare Turnstile ser resolvido após preencher os campos
            try:
                print("[INFO] Verificando se Cloudflare Turnstile foi resolvido...")
                
                # Verifica se existe o Turnstile
                turnstile_present = self.driver.execute_script("""
                    // Verifica se existe o widget do Turnstile
                    var turnstileWidget = document.getElementById('turnstile-widget');
                    var turnstileContainer = document.querySelector('.turnstile-container');
                    return !!(turnstileWidget || turnstileContainer);
                """)
                
                if turnstile_present:
                    print("[INFO] Aguardando resolução do Turnstile após preenchimento...")
                    
                    # Aguarda o Turnstile ser resolvido (até 30 segundos)
                    max_wait_time = 30
                    check_interval = 0.5
                    elapsed_time = 0
                    
                    while elapsed_time < max_wait_time:
                        # Verifica se o Turnstile foi resolvido
                        turnstile_resolved = self.driver.execute_script("""
                            // Verifica se o Turnstile foi resolvido
                            // O Turnstile preenche um input hidden com o token quando resolvido
                            var turnstileInput = document.querySelector('input[name="cf-turnstile-response"]');
                            if (turnstileInput) {
                                var token = turnstileInput.value;
                                // Token válido geralmente tem mais de 50 caracteres e não é o valor inicial
                                if (token && token.length > 50 && !token.startsWith('0.')) {
                                    return true;
                                }
                            }
                            
                            return false;
                        """)
                        
                        if turnstile_resolved:
                            print("[SUCCESS] Cloudflare Turnstile resolvido!")
                            time.sleep(1)  # Aguarda um pouco para garantir
                            break
                        
                        # Verifica se o botão ficou habilitado (indica que Turnstile foi resolvido)
                        button_enabled = self.driver.execute_script("""
                            var form = document.querySelector('form[data-testid="login-form-email"]');
                            if (form) {
                                var submitBtn = form.querySelector('button.red.submit, button.submit');
                                if (submitBtn) {
                                    return !submitBtn.disabled;
                                }
                            }
                            return false;
                        """)
                        
                        if button_enabled:
                            print("[SUCCESS] Botão de login habilitado (Turnstile resolvido)")
                            time.sleep(0.5)
                            break
                        
                        time.sleep(check_interval)
                        elapsed_time += check_interval
                        
                        # Mostra progresso a cada 5 segundos
                        if int(elapsed_time) % 5 == 0 and int(elapsed_time) > 0:
                            print(f"[INFO] Aguardando Turnstile... ({int(elapsed_time)}/{max_wait_time}s)")
                    
                    if elapsed_time >= max_wait_time:
                        print("[AVISO] Timeout aguardando Cloudflare Turnstile, tentando continuar...")
                        # Continua mesmo se não detectou resolução (pode ter sido resolvido silenciosamente)
                else:
                    print("[INFO] Cloudflare Turnstile não detectado, continuando...")
            except Exception as e:
                print(f"[AVISO] Erro ao verificar Cloudflare Turnstile: {e}")
                # Continua mesmo se houver erro
            
            # Estratégia 14: Tenta encontrar o botão novamente após aguardar Turnstile (pode ter sido habilitado)
            if not submit_button:
                print("[INFO] Tentando encontrar botão de submit novamente após aguardar Turnstile...")
                # Tenta encontrar novamente
                try:
                    submit_elements = self.driver.find_elements(By.CSS_SELECTOR,
                        "form[data-testid='login-form-email'] button.red.submit, "
                        "form[data-testid='login-form-email'] button.submit, "
                        "button.red.submit.shared-button-custom, "
                        "button.submit.shared-button-custom, "
                        "button[type='submit']")
                    
                    for elem in submit_elements:
                        if elem.is_displayed():
                            # Verifica se está habilitado
                            is_disabled = elem.get_attribute('disabled')
                            if not is_disabled or is_disabled == 'false':
                                submit_button = elem
                                print("[SUCCESS] Botão de submit encontrado após aguardar Turnstile!")
                                break
                except Exception as e:
                    print(f"[AVISO] Erro ao buscar botão novamente: {e}")
            
            if not submit_button:
                print("[ERRO] Botão de submit não encontrado após todas as tentativas")
                # Tenta uma última vez via JavaScript
                try:
                    submit_button = self.driver.execute_script("""
                        var form = document.querySelector('form[data-testid="login-form-email"]');
                        if (form) {
                            var buttons = form.querySelectorAll('button');
                            for (var i = 0; i < buttons.length; i++) {
                                var btn = buttons[i];
                                var style = window.getComputedStyle(btn);
                                if (style.display !== 'none' && style.visibility !== 'hidden' && !btn.disabled) {
                                    return btn;
                                }
                            }
                        }
                        return null;
                    """)
                    if submit_button and not hasattr(submit_button, 'click'):
                        submit_button = None
                    if submit_button:
                        print("[SUCCESS] Botão encontrado via JavaScript!")
                except Exception as e:
                    print(f"[AVISO] Erro ao buscar botão via JS: {e}")
            
            if not submit_button:
                print("[ERRO] Botão de submit não encontrado")
                return False
            
            # Aguarda o botão ficar clicável (pode ter sido habilitado pelo Turnstile)
            try:
                print("[INFO] Aguardando botão de login ficar clicável...")
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(submit_button)
                )
                print("[SUCCESS] Botão de login está clicável!")
            except TimeoutException:
                print("[AVISO] Botão ainda não está clicável, tentando continuar...")
                # Verifica se está desabilitado
                try:
                    is_disabled = submit_button.get_attribute('disabled')
                    if is_disabled:
                        print("[ERRO] Botão de login está desabilitado. Verifique se o Cloudflare Turnstile foi resolvido.")
                        return False
                except:
                    pass
            
            # Clica no botão de submit usando clique real (ActionChains)
            try:
                print("[INFO] Clicando no botão de login...")
                
                # Scroll até o elemento
                self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(0.5)
                
                # Simula clique real usando ActionChains
                try:
                    actions = ActionChains(self.driver)
                    actions.move_to_element(submit_button).pause(0.2).click().perform()
                    print("[SUCCESS] Clique no botão realizado")
                except:
                    # Fallback: clique simples
                    submit_button.click()
                    print("[INFO] Clique simples realizado")
                
                time.sleep(3)
                
                # Verifica se o login foi bem-sucedido (modal fechou ou há elementos de usuário logado)
                time.sleep(2)
                
                # Verifica se ainda está no modal (login falhou)
                modal_visible = self.driver.execute_script("""
                    var modals = document.querySelectorAll('[class*="modal"], [class*="dialog"], [role="dialog"]');
                    for (var i = 0; i < modals.length; i++) {
                        var style = window.getComputedStyle(modals[i]);
                        if (style.display !== 'none' && style.visibility !== 'hidden') {
                            return true;
                        }
                    }
                    return false;
                """)
                
                if modal_visible:
                    print("[AVISO] Modal ainda visível após login, pode ter falhado")
                    # Pode ter falhado, mas continua
                
                return True
            except Exception as e:
                print(f"[ERRO] Erro ao clicar no botão de submit: {e}")
                return False
            
        except Exception as e:
            print(f"[ERRO] Erro no login: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _inject_dom_observer(self):
        """Injeta MutationObserver para detectar mudanças no DOM"""
        try:
            observer_script = """
            // Cria um observer para detectar mudanças no DOM
            if (!window.blazeObserver) {
                window.blazeObserver = {
                    lastResultHash: null,
                    lastTimerText: null,
                    callbacks: [],
                    
                    init: function() {
                        // Observa mudanças no container de resultados (estrutura exata)
                        const resultContainer = document.querySelector('#roulette-recent .roulette-previous.casino-recent .entries.main') ||
                                                document.querySelector('#roulette-recent') ||
                                                document.querySelector('[class*="roulette-previous"]');
                        
                        const timerContainer = document.querySelector('#roulette-timer, [id*="timer"], [class*="timer"]');
                        
                        if (resultContainer) {
                            const observer = new MutationObserver((mutations) => {
                                // Verifica se foi adicionado um novo .entry (novo resultado)
                                for (let mutation of mutations) {
                                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                                        // Verifica se algum dos nós adicionados é um .entry
                                        for (let node of mutation.addedNodes) {
                                            if (node.nodeType === 1) { // Element node
                                                if (node.classList && node.classList.contains('entry')) {
                                                    window.blazeObserver.onDomChange();
                                                    break;
                                                }
                                                // Verifica dentro do nó
                                                if (node.querySelector && node.querySelector('.entry')) {
                                                    window.blazeObserver.onDomChange();
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                    // Também detecta mudanças em atributos (classes, styles)
                                    if (mutation.type === 'attributes') {
                                        window.blazeObserver.onDomChange();
                                    }
                                }
                            });
                            
                            observer.observe(resultContainer, {
                                childList: true,
                                subtree: true,
                                attributes: true,
                                attributeFilter: ['class', 'style']
                            });
                        }
                        
                        if (timerContainer) {
                            const timerObserver = new MutationObserver((mutations) => {
                                window.blazeObserver.onTimerChange();
                            });
                            
                            timerObserver.observe(timerContainer, {
                                childList: true,
                                subtree: true,
                                characterData: true
                            });
                        }
                    },
                    
                    onDomChange: function() {
                        // Notifica que houve mudança no DOM
                        window.blazeObserver.hasChanged = true;
                    },
                    
                    onTimerChange: function() {
                        const timerEl = document.querySelector('#roulette-timer, [id*="timer"], [class*="timer"]');
                        if (timerEl) {
                            const newText = timerEl.textContent || timerEl.innerText;
                            if (newText !== window.blazeObserver.lastTimerText) {
                                window.blazeObserver.lastTimerText = newText;
                                window.blazeObserver.hasChanged = true;
                            }
                        }
                    },
                    
                    hasChanged: false,
                    
                    checkForChanges: function() {
                        const changed = window.blazeObserver.hasChanged;
                        window.blazeObserver.hasChanged = false;
                        return changed;
                    }
                };
                
                window.blazeObserver.init();
            }
            """
            self.driver.execute_script(observer_script)
        except Exception as e:
            # Se falhar, continua sem observer (fallback para polling)
            pass
    
    def navigate_to_double(self):
        """Navega para a página do jogo Double/Roleta"""
        try:
            print("[INFO] Navegando para a página do Double...")
            self.driver.get(config.DOUBLE_URL)
            
            # Aguarda 10 segundos para a página carregar completamente antes de procurar elementos
            print("[INFO] Aguardando 10 segundos para página carregar completamente...")
            time.sleep(10)
            
            # Reinjeta o observer após navegação
            print("[INFO] Injetando observer de DOM...")
            self._inject_dom_observer()
            
            print("[SUCCESS] Página do Double carregada e pronta")
            return True
        except Exception as e:
            print(f"Erro ao navegar para Double: {e}")
            return False
    
    def wait_for_dom_change(self, timeout: int = 10):
        """Aguarda mudança no DOM usando MutationObserver"""
        try:
            if not self.wait:
                return False
            
            # Verifica se há mudança detectada pelo observer
            changed = self.driver.execute_script("""
                return window.blazeObserver ? window.blazeObserver.checkForChanges() : false;
            """)
            
            return changed
        except:
            return False
    
    def wait_for_new_result(self, timeout: int = 30):
        """Aguarda até que um novo resultado apareça no histórico"""
        try:
            if not self.wait:
                return False
            
            # Aguarda mudança no histórico de resultados
            initial_count = len(self.get_recent_results())
            
            # Usa WebDriverWait para esperar mudança
            try:
                self.wait.until(lambda driver: len(self.get_recent_results()) > initial_count)
                return True
            except TimeoutException:
                return False
        except Exception as e:
            return False
    
    def wait_for_timer_change(self, timeout: int = 10):
        """Aguarda mudança no timer usando observação de DOM"""
        try:
            if not self.wait:
                return False
            
            initial_timer = self.last_timer_text
            
            # Aguarda até que o timer mude
            try:
                self.wait.until(lambda driver: self._timer_has_changed())
                return True
            except TimeoutException:
                return False
        except:
            return False
    
    def _timer_has_changed(self):
        """Verifica se o timer mudou"""
        try:
            timer_element = self.driver.find_elements(By.CSS_SELECTOR, 
                "#roulette-timer, [id*='timer'], [class*='timer']")
            
            if timer_element:
                current_timer = timer_element[0].text
                if current_timer != self.last_timer_text:
                    self.last_timer_text = current_timer
                    return True
            return False
        except:
            return False
    
    def get_current_game_state(self, check_changes: bool = True):
        """Obtém o estado atual do jogo (usa observação de DOM se disponível)"""
        try:
            # Se check_changes é True, verifica se há mudanças antes de processar
            if check_changes and self.wait:
                has_changed = self.wait_for_dom_change(timeout=0.1)
                if not has_changed:
                    # Não houve mudança, retorna estado anterior se disponível
                    pass
            
            # Procura pelo timer
            timer_element = self.driver.find_elements(By.CSS_SELECTOR, 
                "#roulette-timer, [id*='timer'], [class*='timer']")
            
            timer_text = ""
            if timer_element:
                timer_text = timer_element[0].text
                self.last_timer_text = timer_text
            
            # Detecta período de apostas corretamente:
            # - "Girando em X segundos" = período de apostas (pode apostar)
            # - "Girando..." ou apenas "Girando" = já está girando (não pode apostar)
            # - "Girou" ou "Blaze Girou" = terminou de girar (não pode apostar)
            # - "Aguardando" = aguardando próximo jogo (não pode apostar)
            
            is_betting = False
            timer_lower = timer_text.lower()
            
            # Período de apostas: quando mostra "Girando em X segundos" (antes de começar a girar)
            if "girando em" in timer_lower:
                # Tem tempo restante para apostar
                is_betting = True
            elif "girando" in timer_lower and "em" not in timer_lower:
                # Já está girando (não pode apostar)
                is_betting = False
            elif "girou" in timer_lower or "blaze girou" in timer_lower:
                # Terminou de girar (não pode apostar)
                is_betting = False
            elif "aguardando" in timer_lower:
                # Aguardando próximo jogo (não pode apostar)
                is_betting = False
            
            # Obtém as últimas cores jogadas para exibir no estado
            recent_colors = []
            recent_results = self.get_recent_results(limit=10)
            for result in recent_results[:10]:
                if result.get('color'):
                    recent_colors.append(result['color'])
            
            return {
                'timer_text': timer_text,
                'is_betting_period': is_betting,
                'recent_colors': recent_colors
            }
        except Exception as e:
            print(f"Erro ao obter estado do jogo: {e}")
            return {'timer_text': '', 'is_betting_period': False, 'recent_colors': []}
    
    def get_recent_results(self, limit: int = 24, check_changes: bool = False) -> list:
        """Obtém os resultados recentes do jogo (cores e números)
        
        Args:
            limit: Número máximo de resultados a retornar
            check_changes: Se True, só processa se houver mudança no DOM
        """
        try:
            # Verifica cache primeiro (se ainda válido)
            current_time = time.time()
            if (not check_changes and 
                self._results_cache['results'] and 
                current_time - self._results_cache['timestamp'] < self._results_cache['cache_duration']):
                return self._results_cache['results'][:limit]
            
            # Verifica mudança no DOM antes de processar
            if check_changes and self.wait:
                has_changed = self.wait_for_dom_change(timeout=0.1)
                if not has_changed and self.last_results_hash:
                    # Não houve mudança, retorna cache se disponível
                    if self._results_cache['results']:
                        return self._results_cache['results'][:limit]
                    return []
            
            results = []
            
            # Estrutura exata: #roulette-recent > .roulette-previous.casino-recent > .entries.main > .entry
            # Procura pelos elementos .entry dentro da estrutura correta
            history_selectors = [
                "#roulette-recent .roulette-previous.casino-recent .entries.main .entry",
                "#roulette-recent .entries.main .entry",
                "#roulette-recent .entry",
                ".roulette-previous.casino-recent .entries.main .entry",
                ".casino-recent .entries.main .entry"
            ]
            
            history_elements = []
            for selector in history_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    history_elements = elements
                    break
            
            # Se não encontrou com a estrutura específica, tenta genérico
            if not history_elements:
                history_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    "#roulette-recent .entry, [class*='roulette-previous'] .entry")
            
            # Processa cada entry (o primeiro é o mais recente)
            for i, entry_elem in enumerate(history_elements[:limit]):
                try:
                    color = None
                    number = None
                    
                    # Procura pelo sm-box dentro do roulette-tile - múltiplas estratégias
                    sm_box = entry_elem.find_elements(By.CSS_SELECTOR, ".roulette-tile .sm-box")
                    
                    if not sm_box:
                        # Tenta encontrar diretamente
                        sm_box = entry_elem.find_elements(By.CSS_SELECTOR, ".sm-box")
                    
                    # Estratégia adicional: XPath como fallback
                    if not sm_box:
                        try:
                            sm_box = entry_elem.find_elements(By.XPATH, 
                                ".//div[contains(@class, 'sm-box')]")
                        except:
                            pass
                    
                    # Estratégia adicional: busca por qualquer div com classes relacionadas
                    if not sm_box:
                        try:
                            sm_box = entry_elem.find_elements(By.XPATH,
                                ".//div[contains(@class, 'box') and (contains(@class, 'red') or contains(@class, 'black') or contains(@class, 'white'))]")
                        except:
                            pass
                    
                    if sm_box:
                        sm_box_elem = sm_box[0]
                        classes = sm_box_elem.get_attribute('class') or ''
                        style = sm_box_elem.get_attribute('style') or ''
                        html = sm_box_elem.get_attribute('innerHTML') or ''
                        
                        # Detecta cor pela classe sm-box (prioridade alta)
                        if 'sm-box white' in classes or 'white' in classes:
                            color = 'white'
                        elif 'sm-box red' in classes or 'red' in classes:
                            color = 'red'
                        elif 'sm-box black' in classes or 'black' in classes:
                            color = 'black'
                        
                        # Estratégia adicional: Verifica computed styles via JavaScript
                        if color is None:
                            try:
                                computed_color = self.driver.execute_script("""
                                    var elem = arguments[0];
                                    var style = window.getComputedStyle(elem);
                                    var bgColor = style.backgroundColor;
                                    var classes = elem.className || '';
                                    
                                    // Verifica cor pelo background color
                                    if (bgColor.includes('241') && bgColor.includes('44') && bgColor.includes('76')) {
                                        return 'red';
                                    } else if (bgColor.includes('0, 0, 0') || bgColor === 'rgb(0, 0, 0)') {
                                        return 'black';
                                    } else if (bgColor.includes('255, 255, 255') || bgColor === 'rgb(255, 255, 255)') {
                                        return 'white';
                                    }
                                    
                                    // Verifica por classe
                                    if (classes.includes('white')) return 'white';
                                    if (classes.includes('red')) return 'red';
                                    if (classes.includes('black')) return 'black';
                                    
                                    return null;
                                """, sm_box_elem)
                                if computed_color:
                                    color = computed_color
                            except:
                                pass
                        
                        # Verifica por background-color no estilo (vermelho tem rgb(241, 44, 76))
                        if color is None:
                            if 'rgb(241, 44, 76)' in style or '#F12C4C' in style.upper() or '#f12c4c' in style.lower():
                                color = 'red'
                            elif 'background-color: black' in style.lower() or 'background-color:#000' in style.lower() or 'background-color:rgb(0,0,0)' in style.lower():
                                color = 'black'
                            elif 'background-color: white' in style.lower() or 'background-color:#fff' in style.lower() or 'background-color:rgb(255,255,255)' in style.lower():
                                color = 'white'
                        
                        # Verifica atributos data-* se disponíveis (React pode usar isso)
                        if color is None:
                            try:
                                data_color = sm_box_elem.get_attribute('data-color')
                                if data_color in ['red', 'black', 'white']:
                                    color = data_color
                            except:
                                pass
                        
                        # Verifica se tem SVG (branco não tem número, só SVG)
                        if 'svg' in html.lower() and color is None:
                            color = 'white'
                        
                        # Extrai o número (se houver) - múltiplas estratégias
                        if color != 'white':  # Branco não tem número
                            # Estratégia 1: Procura pelo elemento .number diretamente
                            number_elem = sm_box_elem.find_elements(By.CSS_SELECTOR, ".number")
                            if number_elem:
                                try:
                                    # Tenta obter texto de várias formas
                                    number_text = number_elem[0].text.strip()
                                    if not number_text:
                                        # Se text não funcionou, tenta innerText via JavaScript
                                        number_text = self.driver.execute_script(
                                            "return arguments[0].innerText || arguments[0].textContent || '';", 
                                            number_elem[0]
                                        ).strip()
                                    if not number_text:
                                        # Tenta textContent
                                        number_text = number_elem[0].get_attribute('textContent') or ''
                                        number_text = number_text.strip()
                                    
                                    if number_text and number_text.isdigit():
                                        number = int(number_text)
                                except Exception as e:
                                    pass
                            
                            # Estratégia 2: Se ainda não encontrou, tenta extrair do HTML
                            if number is None:
                                try:
                                    # Procura por números no HTML do elemento
                                    html_content = sm_box_elem.get_attribute('innerHTML') or ''
                                    # Procura por padrão: <div class="number">X</div> ou similar
                                    number_matches = re.findall(r'<div[^>]*class="number"[^>]*>(\d+)</div>', html_content)
                                    if number_matches:
                                        number = int(number_matches[0])
                                except:
                                    pass
                            
                            # Estratégia 3: Extrai do texto completo do elemento
                            if number is None:
                                try:
                                    # Tenta obter todo o texto do elemento
                                    full_text = sm_box_elem.text.strip()
                                    if not full_text:
                                        # Se não funcionou, tenta via JavaScript
                                        full_text = self.driver.execute_script(
                                            "return arguments[0].innerText || arguments[0].textContent || '';", 
                                            sm_box_elem
                                        ).strip()
                                    
                                    # Procura por números no texto
                                    numbers = re.findall(r'\d+', full_text)
                                    if numbers:
                                        # Pega o primeiro número encontrado (deve ser o número do jogo)
                                        number = int(numbers[0])
                                        # Valida se o número está na faixa válida (1-14)
                                        if number < 1 or number > 14:
                                            number = None
                                except:
                                    pass
                            
                            # Estratégia 4: Usa JavaScript para buscar diretamente no DOM (melhorado)
                            if number is None:
                                try:
                                    # Executa JavaScript para encontrar o número diretamente
                                    number_js = self.driver.execute_script("""
                                        var elem = arguments[0];
                                        
                                        // Tenta múltiplas formas de encontrar o número
                                        var numberDiv = elem.querySelector('.number');
                                        if (numberDiv) {
                                            var num = numberDiv.innerText || numberDiv.textContent || numberDiv.innerHTML || '';
                                            num = num.trim();
                                            if (num && /^\\d+$/.test(num)) {
                                                var numVal = parseInt(num);
                                                if (numVal >= 1 && numVal <= 14) {
                                                    return numVal;
                                                }
                                            }
                                        }
                                        
                                        // Tenta buscar por qualquer div com número
                                        var allDivs = elem.querySelectorAll('div');
                                        for (var i = 0; i < allDivs.length; i++) {
                                            var text = allDivs[i].innerText || allDivs[i].textContent || '';
                                            text = text.trim();
                                            if (/^\\d+$/.test(text)) {
                                                var numVal = parseInt(text);
                                                if (numVal >= 1 && numVal <= 14) {
                                                    return numVal;
                                                }
                                            }
                                        }
                                        
                                        // Tenta buscar no texto completo do elemento
                                        var fullText = elem.innerText || elem.textContent || '';
                                        var numbers = fullText.match(/\\d+/g);
                                        if (numbers) {
                                            for (var i = 0; i < numbers.length; i++) {
                                                var numVal = parseInt(numbers[i]);
                                                if (numVal >= 1 && numVal <= 14) {
                                                    return numVal;
                                                }
                                            }
                                        }
                                        
                                        return null;
                                    """, sm_box_elem)
                                    
                                    if number_js and isinstance(number_js, (int, str)):
                                        if isinstance(number_js, str) and number_js.isdigit():
                                            num_val = int(number_js)
                                        else:
                                            num_val = int(number_js)
                                        if 1 <= num_val <= 14:
                                            number = num_val
                                except:
                                    pass
                            
                            # Estratégia 5: Busca por atributos data-* (React pode usar)
                            if number is None:
                                try:
                                    data_number = sm_box_elem.get_attribute('data-number')
                                    if data_number and data_number.isdigit():
                                        num_val = int(data_number)
                                        if 1 <= num_val <= 14:
                                            number = num_val
                                except:
                                    pass
                    
                    # Se encontrou a cor, adiciona ao resultado
                    if color:
                        results.append({
                            'color': color,
                            'number': number  # Será None para branco
                        })
                except Exception as e:
                    continue
            
            # Calcula hash dos resultados para detectar mudanças
            results_hash = hash(str([(r.get('color'), r.get('number')) for r in results]))
            
            # Se os resultados mudaram, atualiza o hash
            if results_hash != self.last_results_hash:
                self.last_results_hash = results_hash
                # Atualiza cache
                self._results_cache = {
                    'timestamp': time.time(),
                    'results': results,
                    'cache_duration': 0.5
                }
            elif check_changes and results_hash == self.last_results_hash:
                # Não houve mudança real, atualiza cache se necessário
                if not self._results_cache['results']:
                    self._results_cache = {
                        'timestamp': time.time(),
                        'results': results,
                        'cache_duration': 0.5
                    }
                return []
            else:
                # Atualiza cache mesmo se não mudou (para evitar re-extração)
                if not self._results_cache['results'] or results_hash == hash(str([(r.get('color'), r.get('number')) for r in self._results_cache['results']])):
                    self._results_cache = {
                        'timestamp': time.time(),
                        'results': results,
                        'cache_duration': 0.5
                    }
            
            return results
        except Exception as e:
            print(f"Erro ao obter resultados recentes: {e}")
            return []
    
    def get_current_result(self):
        """Obtém o resultado atual do jogo (se houver)"""
        try:
            # Procura pelo resultado mais recente na roleta
            current_tile = self.driver.find_elements(By.CSS_SELECTOR,
                "#roulette-slider .selector, [class*='selector']")
            
            if current_tile:
                # Procura pelo tile selecionado
                selected_tile = self.driver.find_elements(By.CSS_SELECTOR,
                    "#roulette-slider-entries .tile-wrapper")
                
                # Tenta encontrar o tile central/selecionado
                for tile in selected_tile:
                    classes = tile.get_attribute('class')
                    color = None
                    
                    if 'red' in classes or 'lg-box red' in tile.get_attribute('innerHTML'):
                        color = 'red'
                    elif 'black' in classes or 'lg-box black' in tile.get_attribute('innerHTML'):
                        color = 'black'
                    elif 'white' in classes or 'lg-box white' in tile.get_attribute('innerHTML'):
                        color = 'white'
                    
                    if color:
                        # Tenta extrair número - múltiplas estratégias
                        number = None
                        if color != 'white':  # Branco não tem número
                            # Estratégia 1: Procura pelo elemento .number
                            number_elem = tile.find_elements(By.CSS_SELECTOR, ".number")
                            if number_elem:
                                try:
                                    number_text = number_elem[0].text.strip()
                                    if not number_text:
                                        number_text = self.driver.execute_script(
                                            "return arguments[0].innerText || arguments[0].textContent || '';", 
                                            number_elem[0]
                                        ).strip()
                                    if number_text and number_text.isdigit():
                                        number = int(number_text)
                                except:
                                    pass
                            
                            # Estratégia 2: Extrai do HTML se necessário
                            if number is None:
                                try:
                                    html_content = tile.get_attribute('innerHTML') or ''
                                    number_matches = re.findall(r'<div[^>]*class="number"[^>]*>(\d+)</div>', html_content)
                                    if number_matches:
                                        number = int(number_matches[0])
                                except:
                                    pass
                            
                            # Estratégia 3: JavaScript direto
                            if number is None:
                                try:
                                    number_js = self.driver.execute_script("""
                                        var elem = arguments[0];
                                        var numberDiv = elem.querySelector('.number');
                                        if (numberDiv) {
                                            var num = numberDiv.innerText || numberDiv.textContent || '';
                                            return num.trim();
                                        }
                                        return null;
                                    """, tile)
                                    
                                    if number_js and number_js.isdigit():
                                        num_val = int(number_js)
                                        if 1 <= num_val <= 14:
                                            number = num_val
                                except:
                                    pass
                        
                        return {'color': color, 'number': number}
            
            return None
        except Exception as e:
            print(f"Erro ao obter resultado atual: {e}")
            return None
    
    def place_bet(self, color: str, amount: float):
        """Faz uma aposta no jogo"""
        try:
            # Seleciona a cor
            color_selectors = {
                'red': ".red, [class*='red']",
                'black': ".black, [class*='black']",
                'white': ".white, [class*='white']"
            }
            
            if color not in color_selectors:
                return False
            
            # Clica na cor
            color_elements = self.driver.find_elements(By.CSS_SELECTOR,
                color_selectors[color])
            
            for elem in color_elements:
                if 'selected' not in elem.get_attribute('class') and elem.is_displayed():
                    try:
                        elem.click()
                        time.sleep(0.5)
                        break
                    except:
                        continue
            
            # Insere o valor da aposta
            bet_input = self.driver.find_elements(By.CSS_SELECTOR,
                "input[type='number'].input-field, input.input-field")
            
            if bet_input:
                bet_input[0].clear()
                bet_input[0].send_keys(str(amount))
                time.sleep(0.5)
            
            # Clica no botão de apostar
            bet_button = self.driver.find_elements(By.XPATH,
                "//button[contains(text(), 'Começar') or contains(text(), 'Apostar') or contains(text(), 'Bet')]")
            
            if bet_button:
                if not bet_button[0].get_attribute('disabled'):
                    bet_button[0].click()
                    time.sleep(1)
                    return True
            
            return False
        except Exception as e:
            print(f"Erro ao fazer aposta: {e}")
            return False
    
    def close(self):
        """Fecha o navegador"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.wait = None
            self.is_logged_in = False
            self.login_attempted = False

