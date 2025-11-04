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
from src.utils.roulette import normalize_result


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
        # Diagnóstico
        self.last_heartbeat_elapsed = 0.0
        self.last_heartbeat_error = None
        self.last_page_crash_time = None
        self.last_page_close_time = None
        self.last_request_fail = None
        self.last_console_error = None
        self.last_response_status_error = None
        self.last_antibot_detected = False
        # Humanização
        self.last_human_action_time = 0.0
        
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
            
            # Handlers para diagnosticar travamentos e fechamentos de página/contexto
            try:
                self.page.on('crash', lambda _: (setattr(self, 'last_page_crash_time', time.time()), print('[ERRO] Página crashou (event: crash)')))
                self.page.on('close', lambda _: (setattr(self, 'last_page_close_time', time.time()), print('[AVISO] Página fechada (event: close)')))
                self.page.on('requestfailed', lambda req: setattr(self, 'last_request_fail', {
                    'url': req.url,
                    'failure': req.failure,
                    'method': req.method
                }))
                self.page.on('response', lambda resp: (resp.status >= 400) and setattr(self, 'last_response_status_error', {
                    'url': resp.url,
                    'status': resp.status
                }))
                self.page.on('console', lambda msg: (msg.type == 'error') and setattr(self, 'last_console_error', msg.text))
            except Exception:
                pass

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
            # Abre diretamente o modal de login (mais confiável)
            try:
                self._goto_with_retry(config.DOUBLE_URL + '?modal=auth&tab=login', attempts=2)
            except Exception:
                try:
                    self._goto_with_retry(config.BLAZE_URL + '?modal=auth&tab=login', attempts=2)
                except Exception:
                    pass

            # Aguarda o modal de login
            try:
                self.page.wait_for_selector('#auth-modal, [data-modal-type="auth"]', timeout=8000)
            except Exception:
                pass

            # Seletores específicos do modal informado
            username_selector = '#auth-modal input[name="username"], [data-modal-type="auth"] input[name="username"]'
            password_selector = '#auth-modal input[name="password"], [data-modal-type="auth"] input[name="password"]'
            submit_selector = '#auth-modal button.red.submit, [data-modal-type="auth"] button.red.submit'

            # Preenche usuário/email
            try:
                email_input = self.page.wait_for_selector(username_selector, timeout=5000)
                if not email_input:
                    return False
                try:
                    email_input.fill('')
                except Exception:
                    pass
                for ch in email:
                    email_input.type(ch, delay=random.randint(40, 100))
            except Exception:
                return False

            # Preenche senha
            try:
                password_input = self.page.wait_for_selector(password_selector, timeout=5000)
                if not password_input:
                    return False
                try:
                    password_input.fill('')
                except Exception:
                    pass
                for ch in password:
                    password_input.type(ch, delay=random.randint(40, 100))
            except Exception:
                return False

            # Pequena espera para Turnstile preencher token (se já liberado)
            time.sleep(2)

            # Clica no botão "Entrar" do modal (type=button)
            try:
                submit_button = self.page.wait_for_selector(submit_selector, timeout=5000)
                if submit_button and submit_button.is_enabled():
                    submit_button.click()
            except Exception:
                pass

            # Aguarda navegação/estado logado
            time.sleep(3)
            if self.check_if_logged_in():
                return True

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
    
    def get_recent_results(self, limit: int = 24, check_changes: bool = False, newest_first: bool = True) -> list:
        """Obtém resultados recentes.
        newest_first=True retorna o mais recente no índice 0.
        """
        try:
            # Verifica cache
            if check_changes and time.time() - self._results_cache['timestamp'] < self._results_cache['cache_duration']:
                return self._results_cache['results']
            
            results = []
            
            # Extrai resultados da seção "Giros Anteriores"
            results_js = self.page.evaluate("""
                () => {
                    const results = [];
                    const entries = document.querySelectorAll('#roulette-recent .roulette-previous .entry .sm-box');
                    entries.forEach(entry => {
                        const classes = entry.className || '';
                        let color = null;
                        if (classes.includes('red')) color = 'red';
                        else if (classes.includes('black')) color = 'black';
                        else if (classes.includes('white')) color = 'white';
                        if (!color) return;
                        let number = null;
                        const numEl = entry.querySelector('.number');
                        if (numEl) {
                            const t = (numEl.innerText || numEl.textContent || '').trim();
                            if (/^\\d+$/.test(t)) number = parseInt(t);
                        }
                        results.push({ color, number });
                    });
                    return results.slice(0, 24);
                }
            """)
            
            # Ajusta ordem conforme parâmetro
            sliced = results_js[:limit]
            if not newest_first:
                sliced = list(reversed(sliced))

            # Converte e normaliza (white => number=0; corrige inconsistências)
            for item in sliced:
                results.append(normalize_result({'color': item.get('color'), 'number': item.get('number')}))
            
            # Atualiza cache
            self._results_cache = {
                'timestamp': time.time(),
                'results': results,
                'cache_duration': 0.5
            }
            
            # Atualiza indicador de atividade
            self.last_activity_time = time.time()
            return results
            
        except Exception as e:
            print(f"[AVISO] Erro ao obter resultados: {e}")
            return []
    
    def get_current_game_state(self, check_changes: bool = False) -> dict:
        """Obtém estado atual do jogo"""
        try:
            state_js = self.page.evaluate("""
                () => {
                    const state = { timer: null, status: 'waiting', can_bet: false };
                    const tl = document.querySelector('#roulette-timer .time-left');
                    const text = tl ? (tl.innerText || tl.textContent || '').trim() : '';
                    state.timer = text;
                    if (text.toLowerCase().includes('girando...')) {
                        state.status = 'spinning';
                        state.can_bet = false;
                    } else if (text.toLowerCase().includes('girando em')) {
                        state.status = 'countdown';
                        // quando mostra "Girando em <span>mm:ss</span>" normalmente apostas estão abertas
                        state.can_bet = true;
                    } else {
                        state.status = 'waiting';
                        state.can_bet = true;
                    }
                    return state;
                }
            """)
            
            # Atualiza indicador de atividade
            self.last_activity_time = time.time()
            return state_js
            
        except Exception as e:
            print(f"[AVISO] Erro ao obter estado do jogo: {e}")
            return {'timer': None, 'status': 'unknown', 'can_bet': False}
    
    def get_current_result(self) -> dict:
        """Obtém resultado atual"""
        try:
            result_js = self.page.evaluate("""
                () => {
                    // Resultado atual pode estar no slider com destaque (borda/branco) logo após girar
                    const entries = document.querySelectorAll('#roulette-slider-entries .lg-box');
                    for (const el of entries) {
                        const style = el.getAttribute('style') || '';
                        const hasBorder = style.includes('border');
                        const classes = el.className || '';
                        if (!hasBorder) continue;
                        let color = null;
                        if (classes.includes('red')) color = 'red';
                        else if (classes.includes('black')) color = 'black';
                        else if (classes.includes('white')) color = 'white';
                        let number = null;
                        if (color !== 'white') {
                            const numEl = el.querySelector('.number');
                            if (numEl) {
                                const t = (numEl.innerText || numEl.textContent || '').trim();
                                if (/^\\d+$/.test(t)) number = parseInt(t);
                            }
                        }
                        if (color) return { color, number };
                    }
                    return null;
                }
            """)
            
            if result_js:
                self.last_activity_time = time.time()
            return normalize_result(result_js) if result_js else {'color': None, 'number': None}
            
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

    def wait_for_recent_results_change(self, timeout: float = 30.0) -> bool:
        """Aguarda uma mudança na lista de resultados recentes (entrada adicionada/movida).
        Retorna True se detectar mudança antes do timeout, senão False.
        """
        try:
            changed = self.page.evaluate(
                """
                (ms) => {
                    return new Promise((resolve) => {
                        const container = document.querySelector('#roulette-recent .roulette-previous .entries');
                        if (!container) {
                            setTimeout(() => resolve(false), ms);
                            return;
                        }
                        const baseline = container.innerText || container.textContent || '';
                        const observer = new MutationObserver(() => {
                            const current = container.innerText || container.textContent || '';
                            if (current !== baseline) {
                                observer.disconnect();
                                resolve(true);
                            }
                        });
                        observer.observe(container, { childList: true, subtree: true, attributes: false, characterData: false });
                        setTimeout(() => { observer.disconnect(); resolve(false); }, ms);
                    });
                }
                """,
                int(timeout * 1000)
            )
            return bool(changed)
        except Exception:
            return False

    def detect_antibot(self) -> bool:
        """Tenta detectar sinais de anti-bot/Cloudflare/Turnstile na página."""
        try:
            detected = self.page.evaluate("""
                () => {
                    const title = (document.title||'').toLowerCase();
                    if (title.includes('attention required') || title.includes('checking your browser')) return true;
                    if (document.querySelector('iframe[src*="challenges.cloudflare.com"], script[src*="turnstile"]')) return true;
                    if (document.querySelector('[data-cf]') || document.querySelector('[data-challenge]')) return true;
                    if (location.pathname.includes('challenge')) return true;
                    return false;
                }
            """)
            self.last_antibot_detected = bool(detected)
            return self.last_antibot_detected
        except Exception:
            return False

    def get_diagnostic_summary(self) -> dict:
        """Resumo estruturado da possível causa de não-responsividade/fechamento."""
        summary = {
            'antibot_detected': False,
            'last_heartbeat_elapsed': self.last_heartbeat_elapsed,
            'last_heartbeat_error': self.last_heartbeat_error,
            'page_crash_at': self.last_page_crash_time,
            'page_close_at': self.last_page_close_time,
            'last_request_fail': self.last_request_fail,
            'last_response_status_error': self.last_response_status_error,
            'last_console_error': self.last_console_error,
            'inferred_reason': 'unknown'
        }
        try:
            if self.detect_antibot():
                summary['antibot_detected'] = True
                summary['inferred_reason'] = 'anti-bot/Cloudflare'
            elif self.last_page_crash_time:
                summary['inferred_reason'] = 'page_crash'
            elif self.last_page_close_time and (not self.page or self.page.is_closed()):
                summary['inferred_reason'] = 'page_closed'
            elif self.last_heartbeat_error:
                summary['inferred_reason'] = 'heartbeat_error'
            elif self.last_request_fail or (summary['last_response_status_error'] and summary['last_response_status_error'].get('status', 200) >= 500):
                summary['inferred_reason'] = 'network_error'
            elif summary['last_response_status_error'] and 400 <= summary['last_response_status_error'].get('status', 0) < 500:
                summary['inferred_reason'] = 'http_client_error'
        except Exception:
            pass
        return summary

    # ===== Humanização de interação =====
    def perform_human_tick(self) -> None:
        """Executa uma pequena sequência pseudo-aleatória de ações humanas para reduzir detecção de bot.
        Mantém frequência moderada e usa áreas seguras para clique/hover/scroll.
        """
        try:
            now = time.time()
            # Limita frequência: entre 4 e 10s
            if now - self.last_human_action_time < random.uniform(4.0, 10.0):
                return

            self.last_human_action_time = now

            # Viewport
            vp = self.page.viewport_size or { 'width': 1280, 'height': 720 }
            width = vp.get('width', 1280)
            height = vp.get('height', 720)

            # 1) Movimento do mouse com passos suaves
            def _rand_coord():
                margin_x = int(width * 0.08)
                margin_y = int(height * 0.08)
                return (
                    random.randint(margin_x, max(margin_x + 1, width - margin_x)),
                    random.randint(margin_y, max(margin_y + 1, height - margin_y)),
                )

            x1, y1 = _rand_coord()
            x2, y2 = _rand_coord()
            steps = random.randint(12, 28)
            try:
                self.page.mouse.move(x1, y1, steps=int(steps/2))
                self.page.mouse.move(x2, y2, steps=steps)
            except Exception:
                pass

            # 2) Hover em elementos comuns
            hover_candidates = [
                '#roulette-recent', '#roulette-controller', 'header', '.logo',
                '.entries.main', '.balance-input-field', '#roulette-timer',
            ]
            random.shuffle(hover_candidates)
            for sel in hover_candidates[:random.randint(1, 2)]:
                try:
                    el = self.page.query_selector(sel)
                    if el:
                        box = el.bounding_box()
                        if box:
                            hx = int(box['x'] + box['width'] * random.uniform(0.2, 0.8))
                            hy = int(box['y'] + box['height'] * random.uniform(0.2, 0.8))
                            self.page.mouse.move(hx, hy, steps=random.randint(6, 18))
                            time.sleep(random.uniform(0.05, 0.15))
                except Exception:
                    continue

            # 3) Scroll suave (para cima/baixo pequeno)
            try:
                dy = random.choice([1, -1]) * random.randint(80, 240)
                self.page.mouse.wheel(0, dy)
                time.sleep(random.uniform(0.05, 0.2))
                if random.random() < 0.35:
                    dy2 = (-dy) + random.randint(-60, 60)
                    self.page.mouse.wheel(0, dy2)
            except Exception:
                pass

            # 4) Clique esporádico em área segura (sem enviar form)
            try:
                if random.random() < 0.45:
                    cx, cy = _rand_coord()
                    self.page.mouse.click(cx, cy, delay=random.randint(20, 80))
            except Exception:
                pass

            # 5) Pequeno think time
            time.sleep(random.uniform(0.05, 0.2))

        except Exception:
            # Não deixa exceções daqui quebrarem o fluxo
            pass
    
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
            if not self.page or self.page.is_closed():
                return False
            start_t = time.time()
            self.page.evaluate('() => true', timeout=int(timeout * 1000))
            elapsed = time.time() - start_t
            # Atualiza último heartbeat/atividade
            self.last_activity_time = time.time()
            self.last_heartbeat_elapsed = elapsed
            self.last_heartbeat_error = None
            # Se a resposta do heartbeat foi muito lenta, sinaliza degradação
            if elapsed > max(1.5, timeout * 0.8):
                print(f"[AVISO] Heartbeat lento: {elapsed:.2f}s")
            return True
        except Exception as e:
            self.last_heartbeat_error = str(e)
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

    def soft_recover(self, navigate: bool = True) -> bool:
        """Tenta recuperar sem recriar Playwright (mesmo processo/contexto).
        - Fecha e reabre apenas a página dentro do mesmo context
        - Se necessário, recria o contexto dentro do mesmo browser
        - Reatribui self.driver
        - Opcionalmente navega até a URL principal e/ou Double
        """
        try:
            if not self.browser:
                return False
            # sempre recria o contexto para limpar estado corrompido
            try:
                if self.context:
                    self.context.close()
            except Exception:
                pass
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                locale='pt-BR',
                timezone_id='America/Sao_Paulo',
                permissions=['notifications'],
                ignore_https_errors=True,
            )
            # fecha página antiga
            try:
                if self.page:
                    self.page.close()
            except:
                pass
            # abre nova página
            self.page = self.context.new_page()
            self.driver = self.page

            if navigate:
                try:
                    self._goto_with_retry(config.BLAZE_URL, attempts=2)
                    time.sleep(2)
                    self.accept_cookies()
                    self.confirm_age()
                    # tenta ir ao Double
                    self._goto_with_retry(config.DOUBLE_URL, attempts=2)
                    time.sleep(2)
                except Exception:
                    pass

            return True
        except Exception:
            return False
    
    def reinitialize_with_login_retry(self, email: str = None, password: str = None, max_retries: int = 2) -> bool:
        """Reinicializa e tenta login novamente"""
        try:
            # Evita recriar Playwright; tenta recuperação suave primeiro
            if self.soft_recover(navigate=True):
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
    # ===== Modal de Analytics (Padrões / Histórico) =====
    def open_analytics_modal(self, tab: str = 'patterns') -> bool:
        """Abre o modal de analytics e seleciona a aba desejada: 'patterns' ou 'history'."""
        try:
            # Abre diretamente o modal via parâmetro se possível
            try:
                self._goto_with_retry(config.DOUBLE_URL + '?modal=double_history-v2_index&roomId=1', attempts=1)
                time.sleep(1.5)
            except Exception:
                pass

            # Garante existência do modal
            self.page.wait_for_selector('#double-analytics', timeout=5000)

            # Seleciona a aba
            if tab == 'patterns':
                btn = self.page.query_selector('.tabs-crash-analytics .tab:has-text("Padrões")')
                if btn:
                    btn.click()
            else:
                btn = self.page.query_selector('.tabs-crash-analytics .tab:has-text("Histórico")')
                if btn:
                    btn.click()
            time.sleep(0.5)
            return True
        except Exception:
            return False

    def set_analytics_rounds(self, rounds: int = 100) -> bool:
        """Seleciona a quantidade de rodadas no select do modal (25,50,100,500,3000)."""
        try:
            sel = self.page.wait_for_selector('#double-analytics .select-menu select', timeout=3000)
            if not sel:
                return False
            value = str(rounds) if str(rounds) in {'25','50','100','500','3000'} else '100'
            sel.select_option(value=value)
            time.sleep(0.3)
            return True
        except Exception:
            return False

    def get_patterns_numbers_percentages(self) -> dict:
        """Extrai o bloco "Número percentual" -> {numero:int -> percent:float}."""
        try:
            data = self.page.evaluate("""
                () => {
                    const result = {};
                    const container = Array.from(document.querySelectorAll('#double-analytics .roll-title'))
                      .find(el => (el.innerText||'').toLowerCase().includes('número percentual'));
                    if (!container) return result;
                    const roll = container.nextElementSibling;
                    if (!roll) return result;
                    const items = roll.querySelectorAll('.roll__container');
                    items.forEach(it => {
                        const numEl = it.querySelector('.roll__square span');
                        const pctEl = it.querySelector('p');
                        if (!numEl || !pctEl) return;
                        const numTxt = (numEl.innerText||'').trim();
                        const pctTxt = (pctEl.innerText||'').replace('%','').replace(',','.');
                        const n = /^\d+$/.test(numTxt) ? parseInt(numTxt) : (numTxt==='0' ? 0 : null);
                        const v = parseFloat(pctTxt.replace(/[^0-9\.]/g,''));
                        if (n !== null && !Number.isNaN(v)) result[n] = v;
                    });
                    return result;
                }
            """)
            return data or {}
        except Exception:
            return {}

    def get_patterns_parity(self) -> dict:
        """Extrai Par/Ímpar -> {'even':%, 'odd':%}."""
        try:
            data = self.page.evaluate("""
                () => {
                    const out = { even: null, odd: null };
                    const charts = Array.from(document.querySelectorAll('#double-analytics .chart'));
                    const block = charts.find(c => (c.querySelector('.chart__title')?.innerText||'').toLowerCase().includes('chance / par'));
                    if (!block) return out;
                    const rows = block.querySelectorAll('.chart__bar_container');
                    rows.forEach(r => {
                        const title = (r.querySelector('.chart__bar__title')?.innerText||'').toLowerCase();
                        const valTxt = (r.querySelector('.chart__bar__value')?.innerText||'').replace('%','').replace(',','.');
                        const v = parseFloat(valTxt);
                        if (title.includes('par')) out.even = v;
                        if (title.includes('ímpar') || title.includes('impar')) out.odd = v;
                    });
                    return out;
                }
            """)
            return data or { 'even': None, 'odd': None }
        except Exception:
            return { 'even': None, 'odd': None }

    def get_patterns_high_low(self) -> dict:
        """Extrai Alto/Baixo -> {'high':%, 'low':%}."""
        try:
            data = self.page.evaluate("""
                () => {
                    const out = { high: null, low: null };
                    const charts = Array.from(document.querySelectorAll('#double-analytics .chart'));
                    const block = charts.find(c => (c.querySelector('.chart__title')?.innerText||'').toLowerCase().includes('alto / baixo'));
                    if (!block) return out;
                    const rows = block.querySelectorAll('.chart__bar_container');
                    rows.forEach(r => {
                        const title = (r.querySelector('.chart__bar__title')?.innerText||'').toLowerCase();
                        const valTxt = (r.querySelector('.chart__bar__value')?.innerText||'').replace('%','').replace(',','.');
                        const v = parseFloat(valTxt);
                        if (title.includes('alto')) out.high = v;
                        if (title.includes('baixo')) out.low = v;
                    });
                    return out;
                }
            """)
            return data or { 'high': None, 'low': None }
        except Exception:
            return { 'high': None, 'low': None }

    def get_history_latest(self, limit: int = 25) -> list:
        """Extrai a lista do Histórico no modal (necessita aba 'Histórico' ativa)."""
        try:
            items = self.page.evaluate("""
                (limit) => {
                    const out = [];
                    const rows = document.querySelectorAll('#double-analytics #history__double .history__double__container');
                    for (let i = 0; i < rows.length && out.length < limit; i++) {
                        const row = rows[i];
                        const itemEl = row.querySelector('.history__double__item');
                        if (!itemEl) continue;
                        let color = null;
                        const cls = itemEl.className || '';
                        if (cls.includes('--red')) color = 'red';
                        else if (cls.includes('--black')) color = 'black';
                        else if (cls.includes('--white')) color = 'white';
                        let number = null;
                        const center = itemEl.querySelector('.history__double__center');
                        if (center) {
                            const numTxt = (center.innerText||'').trim();
                            if (/^\d+$/.test(numTxt)) number = parseInt(numTxt);
                        } else if (color === 'white') {
                            number = 0;
                        }
                        const dateEl = row.querySelector('.history__double__date');
                        let date = null, time = null;
                        if (dateEl) {
                            const ps = dateEl.querySelectorAll('p');
                            if (ps && ps.length >= 2) {
                                date = (ps[0].innerText||'').trim();
                                time = (ps[1].innerText||'').trim();
                            }
                        }
                        out.push({ color, number, date, time });
                    }
                    return out;
                }
            """, int(max(1, min(300, limit))))
            # Normaliza números/cores
            return [normalize_result(it) for it in (items or [])]
        except Exception:
            return []

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

