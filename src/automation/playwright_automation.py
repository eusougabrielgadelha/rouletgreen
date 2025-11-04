"""
Módulo de automação web usando Playwright
Versão mais estável e recomendada para servidor headless
"""
import time
import re
import random
import sys
import os
import threading

# Importa Playwright de forma segura
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("[AVISO] Playwright não está instalado")

# Adiciona o diretório raiz ao path para importar config
root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, os.path.abspath(root_dir))
from config import config


class BlazeAutomation:
    """Classe de automação usando Playwright - mais estável em servidor headless"""
    
    def __init__(self, headless: bool = False):
        # Força headless em servidor sem display
        import os
        if not headless and (not os.getenv('DISPLAY') or os.getenv('DISPLAY') == ''):
            print("[INFO] Servidor sem display - usando headless=True")
            headless = True
        
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.headless = headless
        self.wait_time = config.WAIT_TIME
        self.last_results_hash = None
        self.last_timer_text = None
        
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
        
        # Compatibilidade: driver aponta para page (para código existente)
        self.driver = None  # Será definido como self.page após init
    
    def init_driver(self):
        """Inicializa o navegador Playwright"""
        try:
            # Verifica se há loop asyncio rodando (incompatível com sync API)
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    print("[AVISO] Loop asyncio detectado - usando headless forçado e aguardando loop")
                    # Força headless em servidor
                    self.headless = True
            except RuntimeError:
                # Não há loop rodando, OK
                pass
            
            # Força headless em servidor (sem DISPLAY)
            if not self.headless:
                import os
                if not os.getenv('DISPLAY') or os.getenv('DISPLAY') == '':
                    print("[INFO] Servidor sem display detectado - forçando headless=True")
                    self.headless = True
            
            print("[INFO] Inicializando Playwright...")
            
            # Inicia Playwright de forma segura
            # IMPORTANTE: Playwright sync API deve ser usado na mesma thread
            # Se houver loop asyncio, não podemos usar thread separada
            try:
                # Tenta iniciar normalmente
                self.playwright = sync_playwright().start()
            except Exception as e:
                error_msg = str(e).lower()
                if "asyncio" in error_msg:
                    print("[AVISO] Conflito com asyncio detectado")
                    print("[INFO] Tentando inicializar Playwright antes do loop asyncio...")
                    # Se houver loop asyncio, tenta esperar ou usar alternativa
                    # Mas não podemos usar thread separada devido a limitação do Playwright
                    # A solução é inicializar o Playwright ANTES de qualquer coisa assíncrona
                    raise Exception(
                        "Playwright não pode ser inicializado dentro de um loop asyncio. "
                        "Certifique-se de que o Playwright é inicializado antes de qualquer código assíncrono."
                    )
                elif "cannot switch" in error_msg or "thread" in error_msg:
                    print("[AVISO] Erro de thread detectado")
                    raise Exception(
                        "Playwright sync API não pode ser usado entre threads diferentes. "
                        "Certifique-se de que toda a inicialização do Playwright acontece na mesma thread."
                    )
                else:
                    raise
            
            # Configurações do navegador
            browser_args = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-blink-features=AutomationControlled',
            ]
            
            print(f"[INFO] Iniciando navegador (headless={self.headless})...")
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=browser_args,
                timeout=60000  # 60 segundos
            )
            
            # Cria contexto com configurações de stealth
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                locale='pt-BR',
                timezone_id='America/Sao_Paulo',
                permissions=['notifications'],
                ignore_https_errors=True,
            )
            
            # Injeta scripts de stealth no contexto
            self.context.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Mock plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Mock languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['pt-BR', 'pt', 'en-US', 'en']
                });
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            self.page = self.context.new_page()
            
            # Compatibilidade: driver aponta para page, mas adiciona método get() para compatibilidade
            self.driver = self.page
            
            # Adiciona método get() para compatibilidade com Selenium (com retry e domcontentloaded)
            def selenium_get(url):
                return self._goto_with_retry(url, attempts=3)
            
            self.driver.get = selenium_get
            
            print("[SUCCESS] Playwright inicializado com sucesso!")
            return self.page
            
        except Exception as e:
            print(f"[ERRO] Falha ao inicializar Playwright: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def accept_cookies(self) -> bool:
        """Aceita cookies"""
        try:
            # Múltiplos seletores para botão de cookies
            selectors = [
                'button:has-text("Aceitar")',
                'button:has-text("Aceitar cookies")',
                'button:has-text("Aceitar todos")',
                '[data-testid*="cookie"]',
                '.cookie-accept',
                '#accept-cookies',
                'button[class*="cookie"]',
            ]
            
            for selector in selectors:
                try:
                    button = self.page.wait_for_selector(selector, timeout=5000)
                    if button:
                        button.click()
                        time.sleep(1)
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            print(f"[AVISO] Erro ao aceitar cookies: {e}")
            return False
    
    def confirm_age(self) -> bool:
        """Confirma idade (18+)"""
        try:
            selectors = [
                'button:has-text("Tenho mais de 18 anos")',
                'button:has-text("18 anos")',
                'button:has-text("Confirmar")',
                '[data-testid*="age"]',
                '.age-confirm',
                '#confirm-age',
            ]
            
            for selector in selectors:
                try:
                    button = self.page.wait_for_selector(selector, timeout=5000)
                    if button:
                        button.click()
                        time.sleep(1)
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            print(f"[AVISO] Erro ao confirmar idade: {e}")
            return False
    
    def login(self, email: str, password: str) -> bool:
        """Realiza login"""
        try:
            # Clica no botão de login
            login_selectors = [
                'button:has-text("Entrar")',
                'a:has-text("Entrar")',
                '[data-testid*="login"]',
                '.login-button',
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = self.page.wait_for_selector(selector, timeout=5000)
                    if login_button:
                        login_button.click()
                        time.sleep(2)
                        break
                except:
                    continue
            
            if not login_button:
                return False
            
            # Aguarda modal de login aparecer
            time.sleep(2)
            
            # Preenche email
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="email"]',
                '#email',
            ]
            
            for selector in email_selectors:
                try:
                    email_input = self.page.wait_for_selector(selector, timeout=3000)
                    if email_input:
                        # Limpa e digita caracter por caracter (simula humano)
                        try:
                            email_input.fill('')
                        except Exception:
                            pass
                        for char in email:
                            email_input.type(char, delay=random.randint(50, 150))
                        break
                except:
                    continue
            
            time.sleep(1)
            
            # Preenche senha
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                '#password',
            ]
            
            for selector in password_selectors:
                try:
                    password_input = self.page.wait_for_selector(selector, timeout=3000)
                    if password_input:
                        try:
                            password_input.fill('')
                        except Exception:
                            pass
                        for char in password:
                            password_input.type(char, delay=random.randint(50, 150))
                        break
                except:
                    continue
            
            # Aguarda Cloudflare Turnstile (se existir)
            time.sleep(3)
            
            # Tenta clicar no Turnstile (se necessário)
            try:
                turnstile_iframe = self.page.wait_for_selector('iframe[title*="cloudflare"], iframe[title*="challenge"]', timeout=3000)
                if turnstile_iframe:
                    # Clica no iframe do Turnstile
                    frame = turnstile_iframe.content_frame()
                    if frame:
                        checkbox = frame.wait_for_selector('input[type="checkbox"], .cb-container', timeout=5000)
                        if checkbox:
                            checkbox.click()
                            time.sleep(2)
            except:
                pass
            
            # Submete formulário
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Entrar")',
                'button:has-text("Login")',
                'form button[type="submit"]',
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = self.page.wait_for_selector(selector, timeout=3000)
                    if submit_button and submit_button.is_enabled():
                        submit_button.click()
                        time.sleep(3)
                        
                        # Verifica se login foi bem-sucedido
                        if self.check_if_logged_in():
                            return True
                        break
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"[AVISO] Erro ao fazer login: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def navigate_to_double(self) -> bool:
        """Navega para o jogo Double"""
        try:
            self._goto_with_retry(config.DOUBLE_URL, attempts=3)
            time.sleep(5)  # Aguarda alguns segundos para estabilizar
            return True
        except Exception as e:
            print(f"[AVISO] Erro ao navegar para Double: {e}")
            return False
    
    def get_recent_results(self, limit: int = 24, check_changes: bool = False) -> list:
        """Obtém resultados recentes"""
        try:
            # Verifica cache
            if check_changes and time.time() - self._results_cache['timestamp'] < self._results_cache['cache_duration']:
                return self._results_cache['results']
            
            results = []
            
            # Extrai resultados usando JavaScript
            results_js = self.page.evaluate("""
                () => {
                    const results = [];
                    const tiles = document.querySelectorAll('.tile, [class*="tile"], [data-color]');
                    
                    tiles.forEach(tile => {
                        const classes = tile.className || '';
                        let color = null;
                        
                        if (classes.includes('red') || classes.includes('lg-box red')) {
                            color = 'red';
                        } else if (classes.includes('black') || classes.includes('lg-box black')) {
                            color = 'black';
                        } else if (classes.includes('white') || classes.includes('lg-box white')) {
                            color = 'white';
                        }
                        
                        if (color) {
                            let number = null;
                            if (color !== 'white') {
                                const numberElem = tile.querySelector('.number');
                                if (numberElem) {
                                    const numText = (numberElem.innerText || numberElem.textContent || '').trim();
                                    if (numText && /^\\d+$/.test(numText)) {
                                        number = parseInt(numText);
                                    }
                                }
                            }
                            
                            results.push({ color, number });
                        }
                    });
                    
                    return results.slice(0, 24);
                }
            """)
            
            # Converte para formato esperado
            for item in results_js[:limit]:
                results.append({
                    'color': item.get('color'),
                    'number': item.get('number'),
                })
            
            # Atualiza cache
            self._results_cache = {
                'timestamp': time.time(),
                'results': results,
                'cache_duration': 0.5
            }
            
            return results
            
        except Exception as e:
            print(f"[AVISO] Erro ao obter resultados: {e}")
            return []
    
    def get_current_game_state(self, check_changes: bool = False) -> dict:
        """Obtém estado atual do jogo"""
        try:
            state_js = self.page.evaluate("""
                () => {
                    const state = {
                        timer: null,
                        status: 'waiting',
                        can_bet: false
                    };
                    
                    // Extrai timer
                    const timerElems = document.querySelectorAll('[class*="timer"], [class*="countdown"], [id*="timer"]');
                    timerElems.forEach(elem => {
                        const text = (elem.innerText || elem.textContent || '').trim();
                        if (text && /\\d+/.test(text)) {
                            state.timer = text;
                        }
                    });
                    
                    // Verifica status
                    const statusText = document.body.innerText || '';
                    if (statusText.includes('Girando')) {
                        state.status = 'spinning';
                    } else if (statusText.includes('Girando em')) {
                        state.status = 'countdown';
                        state.can_bet = true;
                    } else {
                        state.status = 'waiting';
                        state.can_bet = true;
                    }
                    
                    return state;
                }
            """)
            
            return state_js
            
        except Exception as e:
            print(f"[AVISO] Erro ao obter estado do jogo: {e}")
            return {'timer': None, 'status': 'unknown', 'can_bet': False}
    
    def get_current_result(self) -> dict:
        """Obtém resultado atual"""
        try:
            result_js = self.page.evaluate("""
                () => {
                    const selectedTiles = document.querySelectorAll('.tile.selected, [class*="tile"][class*="selected"]');
                    
                    for (const tile of selectedTiles) {
                        const classes = tile.className || '';
                        let color = null;
                        
                        if (classes.includes('red')) {
                            color = 'red';
                        } else if (classes.includes('black')) {
                            color = 'black';
                        } else if (classes.includes('white')) {
                            color = 'white';
                        }
                        
                        if (color) {
                            let number = null;
                            if (color !== 'white') {
                                const numberElem = tile.querySelector('.number');
                                if (numberElem) {
                                    const numText = (numberElem.innerText || numberElem.textContent || '').trim();
                                    if (numText && /^\\d+$/.test(numText)) {
                                        number = parseInt(numText);
                                    }
                                }
                            }
                            
                            return { color, number };
                        }
                    }
                    
                    return null;
                }
            """)
            
            return result_js or {'color': None, 'number': None}
            
        except Exception as e:
            print(f"[AVISO] Erro ao obter resultado atual: {e}")
            return {'color': None, 'number': None}
    
    def place_bet(self, color: str, amount: float = 1.0) -> bool:
        """Realiza aposta"""
        try:
            # Seleciona cor
            color_selectors = {
                'red': ['button[data-color="red"]', '.bet-red', '[class*="red"][class*="bet"]'],
                'black': ['button[data-color="black"]', '.bet-black', '[class*="black"][class*="bet"]'],
                'white': ['button[data-color="white"]', '.bet-white', '[class*="white"][class*="bet"]'],
            }
            
            for selector in color_selectors.get(color, []):
                try:
                    button = self.page.wait_for_selector(selector, timeout=3000)
                    if button:
                        button.click()
                        time.sleep(0.5)
                        break
                except:
                    continue
            
            # Define valor
            amount_selectors = [
                'input[type="number"]',
                'input[name*="amount"]',
                'input[placeholder*="R$"]',
                'input[placeholder*="valor"]',
                'input[placeholder*="aposta"]',
                'input[class*="amount"]',
            ]
            amount_str = str(amount)
            for selector in amount_selectors:
                try:
                    amt = self.page.wait_for_selector(selector, timeout=1500)
                    if amt:
                        try:
                            amt.fill('')
                        except Exception:
                            # fallback: selecionar tudo e digitar
                            amt.click()
                            self.page.keyboard.press('Control+A')
                            self.page.keyboard.press('Backspace')
                        # digita valor lentamente para evitar bloqueios
                        for ch in amount_str:
                            amt.type(ch, delay=random.randint(30, 90))
                        time.sleep(0.2)
                        break
                except:
                    continue
            
            # Confirma aposta
            confirm_selectors = [
                'button:has-text("Apostar")',
                'button:has-text("Confirmar")',
                'button[type="submit"]',
            ]
            
            for selector in confirm_selectors:
                try:
                    confirm_button = self.page.wait_for_selector(selector, timeout=3000)
                    if confirm_button and confirm_button.is_enabled():
                        confirm_button.click()
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"[AVISO] Erro ao realizar aposta: {e}")
            return False
    
    def wait_for_dom_change(self, timeout: float = 5.0) -> bool:
        """Aguarda mudança no DOM"""
        try:
            # Usa MutationObserver via JavaScript
            changed = self.page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        const observer = new MutationObserver(() => {
                            observer.disconnect();
                            resolve(true);
                        });
                        
                        observer.observe(document.body, {
                            childList: true,
                            subtree: true,
                            attributes: true
                        });
                        
                        setTimeout(() => {
                            observer.disconnect();
                            resolve(false);
                        }, """ + str(int(timeout * 1000)) + """);
                    });
                }
            """)
            
            return changed
            
        except:
            return False
    
    def check_if_logged_in(self) -> bool:
        """Verifica se está logado"""
        try:
            # Procura por elementos que indicam login
            login_indicators = [
                '[class*="user"]',
                '[class*="profile"]',
                '[data-testid*="user"]',
            ]
            
            for selector in login_indicators:
                try:
                    element = self.page.query_selector(selector)
                    if element:
                        return True
                except:
                    continue
            
            # Verifica se botão de login ainda existe
            login_button = self.page.query_selector('button:has-text("Entrar"), a:has-text("Entrar")')
            return login_button is None
            
        except:
            return False
    
    def is_chrome_responsive(self, timeout: float = 5.0) -> bool:
        """Verifica se o navegador está respondendo"""
        try:
            self.page.evaluate('() => true', timeout=int(timeout * 1000))
            return True
        except:
            return False
    
    def restart_chrome(self) -> bool:
        """Reinicia o navegador"""
        try:
            self.close()
            time.sleep(2)
            self.init_driver()
            return True
        except:
            return False
    
    def reinitialize_with_login_retry(self, email: str = None, password: str = None, max_retries: int = 2) -> bool:
        """Reinicializa e tenta login novamente"""
        try:
            if self.restart_chrome():
                self._goto_with_retry(config.BLAZE_URL, attempts=3)
                time.sleep(3)
                
                self.accept_cookies()
                self.confirm_age()
                
                if email and password:
                    return self.login(email, password)
                
                return True
            return False
        except:
            return False

    # ===== Utilitários internos =====
    def _goto_with_retry(self, url: str, attempts: int = 3, base_timeout_ms: int = 60000):
        """Abre URL com backoff e espera menos agressiva (domcontentloaded)."""
        last_error = None
        for i in range(1, attempts + 1):
            try:
                wait_until = 'domcontentloaded'
                timeout_ms = base_timeout_ms + (i - 1) * 15000  # aumenta 15s por tentativa
                return self.page.goto(url, wait_until=wait_until, timeout=timeout_ms)
            except Exception as e:
                last_error = e
                print(f"[AVISO] goto falhou (tentativa {i}/{attempts}): {e}")
                time.sleep(min(5 * i, 15))
        if last_error:
            raise last_error
    
    def close(self):
        """Fecha o navegador"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None
            self.driver = None
            self.is_logged_in = False
            self.login_attempted = False
            
        except Exception as e:
            print(f"[AVISO] Erro ao fechar navegador: {e}")

