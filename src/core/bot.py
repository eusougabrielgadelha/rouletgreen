"""
Módulo core - Classe principal BlazeBot
"""
import sys
import os

# Adiciona o diretório raiz ao path
root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, root_dir)

# Configura encoding UTF-8 para Windows
from src.utils.encoding import setup_encoding
setup_encoding()

import time
import threading
from datetime import datetime
from queue import Queue

# Imports dos módulos
from src.automation import BlazeAutomation
from src.database import Database
from src.analysis import PatternAnalyzer
from src.ui import UI
from src.notifications import TelegramNotifier
from config import config


class BlazeBot:
    def __init__(self):
        self.automation = None
        self.db = Database(config.DATABASE_PATH)
        self.analyzer = PatternAnalyzer(self.db)
        self.ui = UI()
        # IMPORTANTE: NÃO inicializar TelegramNotifier aqui se usar Playwright
        # TelegramNotifier usa asyncio que conflita com Playwright sync API
        # Será inicializado depois do Playwright
        self.telegram = None
        self.running = False
        self.last_game_id = None
        
        # Threading e sincronização
        self.lock = threading.Lock()
        self.game_state_queue = Queue()
        self.results_queue = Queue()
        self.prediction_queue = Queue()
        
        # Cache para evitar processamento duplicado
        self.last_game_state = None
        self.last_history_hash = None
        self.last_results_hash = None
        
        # Controle de coleta de sequências
        self.last_sequence_collection = 0
        self.sequences_collected = set()  # Para evitar duplicação
        
        # Threads
        self.monitor_thread = None
        self.analyzer_thread = None
        
        # Controle de aposta atual
        self.current_bet_game_id = None
    
    def initialize(self, skip_login_on_failure: bool = True):
        """Inicializa o bot
        
        Args:
            skip_login_on_failure: Se True, continua sem login se falhar
        """
        self.ui.print_header()
        self.ui.print_info("Inicializando sistema...")
        
        # Inicializa automação web
        try:
            self.automation = BlazeAutomation(headless=config.HEADLESS)
            self.automation.init_driver()
            self.ui.print_success("Navegador inicializado")
        except Exception as e:
            self.ui.print_error(f"Erro ao inicializar navegador: {e}")
            return False
        
        # Acessa o site
        try:
            self.ui.print_info("Acessando site da Blaze...")
            self.automation.driver.get(config.BLAZE_URL)
            time.sleep(3)
            self.ui.print_success("Site acessado")
        except Exception as e:
            self.ui.print_error(f"Erro ao acessar site: {e}")
            return False
        
        # Aceita cookies
        if self.automation.accept_cookies():
            self.ui.print_success("Cookies aceitos")
        else:
            self.ui.print_warning("Botão de cookies não encontrado (pode já estar aceito)")
        
        # Confirma idade
        if self.automation.confirm_age():
            self.ui.print_success("Idade confirmada")
        else:
            self.ui.print_warning("Botão de idade não encontrado (pode já estar confirmado)")
        
        # Login (com fallback se falhar)
        if config.EMAIL and config.PASSWORD:
            self.ui.print_info("Realizando login...")
            self.automation.login_attempted = True
            if self.automation.login(config.EMAIL, config.PASSWORD):
                self.automation.is_logged_in = True
                self.ui.print_success("Login realizado com sucesso")
                time.sleep(2)
            else:
                self.automation.is_logged_in = False
                if skip_login_on_failure:
                    self.ui.print_warning("Falha no login - continuando sem login")
                else:
                    self.ui.print_error("Falha no login")
                    return False
        else:
            self.ui.print_warning("Credenciais não configuradas - pulando login")
            self.automation.login_attempted = False
        
        # Navega para o jogo Double
        self.ui.print_info("Navegando para o jogo Double...")
        if self.automation.navigate_to_double():
            self.ui.print_success("Jogo Double carregado e pronto")
            # O delay de 10 segundos já está incluído no método navigate_to_double
            
            # Inicializa o Telegram SOMENTE após Playwright estar pronto
            if self.telegram is None:
                try:
                    self.telegram = TelegramNotifier()
                except Exception as e:
                    self.ui.print_warning(f"Falha ao inicializar Telegram: {e}")
                    # Continua mesmo sem Telegram
                    class _DummyTelegram:
                        enabled = False
                        def __getattr__(self, _):
                            def _noop(*args, **kwargs):
                                return None
                            return _noop
                    self.telegram = _DummyTelegram()
            return True
        else:
            self.ui.print_error("Falha ao carregar jogo Double")
            return False
    
    def get_game_id(self) -> str:
        """Gera um ID único para o jogo atual baseado no timestamp"""
        return f"game_{int(time.time())}"
    
    def collect_sequences(self, recent_results: list):
        """Coleta sequências de diferentes tamanhos para análise"""
        try:
            current_time = time.time()
            
            # Coleta sequências em intervalos configurados
            if current_time - self.last_sequence_collection < config.SEQUENCE_COLLECTION_INTERVAL:
                return
            
            self.last_sequence_collection = current_time
            
            # Obtém histórico completo do banco
            with self.lock:
                history = self.db.get_recent_games(limit=max(config.SEQUENCE_SIZES))
            
            if len(history) < 3:
                return
            
            # Coleta sequências de cada tamanho configurado
            for size in config.SEQUENCE_SIZES:
                if len(history) >= size:
                    # Pega os últimos N jogos
                    sequence = history[:size]
                    
                    # Cria hash da sequência para evitar duplicação
                    sequence_hash = hash(str([(s.get('color'), s.get('number')) for s in sequence]))
                    sequence_key = f"{size}_{sequence_hash}"
                    
                    # Se não coletou essa sequência ainda, salva
                    if sequence_key not in self.sequences_collected:
                        self.sequences_collected.add(sequence_key)
                        
                        # Salva no banco
                        with self.lock:
                            self.db.save_sequence(size, sequence)
                        
                        # Limita o tamanho do cache para não consumir muita memória
                        if len(self.sequences_collected) > 1000:
                            # Remove as mais antigas (mantém apenas as últimas 500)
                            sequences_list = list(self.sequences_collected)
                            self.sequences_collected = set(sequences_list[-500:])
        
        except Exception as e:
            # Ignora erros para não interromper o monitoramento
            pass
    
    def analyze_and_predict(self, numbers: list = None):
        """Analisa o histórico e gera uma previsão (cores e números)"""
        # Obtém histórico do banco de dados
        history_colors = self.db.get_game_history_colors(config.HISTORY_SIZE)
        
        if len(history_colors) < 3:
            self.ui.print_warning("Histórico insuficiente para análise")
            return None
        
        # Gera previsão incluindo análise de números
        prediction_data = self.analyzer.get_prediction(
            history_colors, 
            min_confidence=config.MIN_CONFIDENCE,
            numbers=numbers
        )
        
        if not prediction_data:
            return None
        
        prediction, confidence, patterns = prediction_data
        
        # Valida o sinal
        if not self.analyzer.validate_signal(prediction, confidence, config.MIN_CONFIDENCE):
            return None
        
        return {
            'color': prediction,
            'confidence': confidence,
            'patterns': patterns
        }
    
    def monitor_game_loop(self):
        """Thread de monitoramento contínuo do jogo usando observação de DOM"""
        while self.running:
            try:
                # Verifica se Chrome está disponível antes de tentar usar
                if not self.automation or not self.automation.driver:
                    self.ui.print_warning("Chrome não disponível - aguardando...")
                    time.sleep(5)
                    continue
                
                # Usa observação de DOM para detectar mudanças (mais eficiente)
                # Aguarda mudança no DOM ou timeout
                try:
                    dom_changed = self.automation.wait_for_dom_change(timeout=1.0)
                except Exception as e:
                    self.ui.print_warning(f"Erro ao aguardar mudança no DOM: {e}")
                    time.sleep(1)
                    continue
                
                if dom_changed or not self.last_game_state:
                    # Obtém estado do jogo apenas quando há mudança
                    try:
                        game_state = self.automation.get_current_game_state(check_changes=True)
                    except Exception as e:
                        self.ui.print_warning(f"Erro ao obter estado do jogo: {e}")
                        time.sleep(1)
                        continue
                    
                    # Verifica se houve mudança significativa (compatível com Playwright e Selenium)
                    timer_val = game_state.get('timer') if game_state else ''
                    if not timer_val:
                        timer_val = game_state.get('timer_text', '') if game_state else ''
                    can_bet_val = False
                    if game_state:
                        can_bet_val = bool(game_state.get('can_bet', False) or game_state.get('is_betting_period', False))
                    state_hash = hash(str(timer_val) + str(can_bet_val))
                    
                    if state_hash != self.last_game_state:
                        self.last_game_state = state_hash
                        self.game_state_queue.put(game_state)
                
                # Obtém resultados recentes apenas quando há mudança no DOM
                try:
                    recent_results = self.automation.get_recent_results(limit=24, check_changes=True)
                except Exception as e:
                    self.ui.print_warning(f"Erro ao obter resultados: {e}")
                    time.sleep(1)
                    continue
                
                if recent_results:
                    # Calcula hash dos resultados para evitar processamento duplicado
                    results_hash = hash(str([(r.get('color'), r.get('number')) for r in recent_results]))
                    
                    if results_hash != self.last_results_hash:
                        self.last_results_hash = results_hash
                        
                        # Salva resultados no banco (thread-safe, evita duplicação)
                        with self.lock:
                            # Cria IDs únicos baseados em cor+número+timestamp para evitar duplicação
                            for result in recent_results:
                                if result.get('color'):
                                    # Gera ID único baseado no conteúdo
                                    unique_id = f"game_{result.get('color')}_{result.get('number', 0)}_{int(time.time())}"
                                    self.db.save_game(
                                        unique_id,
                                        result.get('color'),
                                        result.get('number')
                                    )
                        
                        self.results_queue.put(recent_results)
                        
                        # Coleta sequências de diferentes tamanhos
                        if config.COLLECT_SEQUENCES:
                            self.collect_sequences(recent_results)
                
                # Sleep menor porque agora estamos reagindo a mudanças no DOM
                time.sleep(0.2)  # Verifica a cada 200ms se há mudanças
                    
            except Exception as e:
                self.ui.print_error(f"Erro no monitoramento: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)
    
    def analyzer_loop(self):
        """Thread de análise paralela"""
        while self.running:
            try:
                # Aguarda por novos resultados ou estado de aposta
                if not self.results_queue.empty():
                    recent_results = self.results_queue.get()
                    
                    # Obtém histórico do banco
                    with self.lock:
                        history = self.db.get_recent_games(limit=config.HISTORY_SIZE)
                    
                    history_colors = [g['color'] for g in history if g.get('color')]
                    history_numbers = [g['number'] for g in history if g.get('number') is not None]
                    
                    # Calcula hash do histórico
                    history_hash = hash(str(history_colors[:10]))
                    
                    # Só analisa se o histórico mudou
                    if history_hash != self.last_history_hash:
                        self.last_history_hash = history_hash
                        
                        if len(history_colors) >= 3:
                            # Analisa e gera previsão em paralelo
                            prediction = self.analyze_and_predict(history_numbers if history_numbers else None)
                            
                            if prediction:
                                self.prediction_queue.put({
                                    'prediction': prediction,
                                    'history': history
                                })
                
                time.sleep(config.ANALYZER_INTERVAL)  # Análise contínua
                
            except Exception as e:
                self.ui.print_error(f"Erro na análise: {e}")
                time.sleep(1)
    
    def run(self):
        """Loop principal do bot com execução paralela e sistema de recuperação"""
        # Configurações de recuperação
        MAX_INACTIVITY_TIME = 30  # Segundos sem resposta antes de reiniciar
        CHROME_CHECK_INTERVAL = 10  # Verifica Chrome a cada 10 segundos
        last_chrome_check = 0
        
        # Loop de inicialização com recuperação
        max_init_retries = 3
        init_retry_count = 0
        
        while init_retry_count < max_init_retries:
            if not self.initialize(skip_login_on_failure=True):
                init_retry_count += 1
                if init_retry_count < max_init_retries:
                    self.ui.print_warning(f"Falha na inicialização. Tentativa {init_retry_count}/{max_init_retries}...")
                    time.sleep(5)
                    continue
                else:
                    self.ui.print_error("Falha na inicialização após todas as tentativas")
                    return
            else:
                break
        
        self.running = True
        self.ui.print_success("Bot iniciado e pronto para análise")
        self.ui.print_info("Modo paralelo ativado - monitoramento contínuo")
        if self.automation.is_logged_in:
            self.ui.print_info("Status: Logado")
        else:
            self.ui.print_warning("Status: Não logado (modo sem login)")
        self.ui.print_separator()
        
        # Envia mensagem de boas-vindas no Telegram
        print("\n[INFO] Verificando Telegram...")
        print(f"[INFO] Telegram habilitado: {getattr(self.telegram, 'enabled', False)}")
        if getattr(self.telegram, 'enabled', False):
            print("[INFO] Enviando mensagem de boas-vindas...")
            self.telegram.send_welcome_message()
        else:
            print("[AVISO] Telegram não está habilitado. Verifique a configuração em config.py")
        
        # Inicia threads de monitoramento e análise
        self.monitor_thread = threading.Thread(target=self.monitor_game_loop, daemon=True)
        self.analyzer_thread = threading.Thread(target=self.analyzer_loop, daemon=True)
        
        self.monitor_thread.start()
        self.analyzer_thread.start()
        
        # Variáveis para controle de UI
        last_update = 0
        current_prediction = None
        current_bet_placed = False
        waiting_for_result = False
        
        # Controle de notificações Telegram
        last_warning_confidence = 0.0  # Última confiança que gerou aviso
        last_opportunity_confidence = 0.0  # Última confiança que gerou oportunidade
        opportunity_lost_sent = False  # Flag para evitar múltiplos avisos de oportunidade perdida
        
        try:
            while self.running:
                try:
                    current_time = time.time()
                    
                    # Sistema de recuperação: verifica se Chrome está respondendo
                    if current_time - last_chrome_check >= CHROME_CHECK_INTERVAL:
                        last_chrome_check = current_time
                        
                        if not self.automation.is_chrome_responsive(timeout=5.0):
                            self.ui.print_warning("Chrome não está respondendo - reiniciando...")
                            
                            # Se estava logado, tenta fazer login novamente
                            if self.automation.is_logged_in or self.automation.login_attempted:
                                self.ui.print_info("Tentando reinicializar com login...")
                                if self.automation.reinitialize_with_login_retry(
                                    email=config.EMAIL if config.EMAIL and config.PASSWORD else None,
                                    password=config.PASSWORD if config.EMAIL and config.PASSWORD else None,
                                    max_retries=2
                                ):
                                    self.ui.print_success("Chrome reinicializado com sucesso")
                                    # Reseta threads e continua
                                    if not self.monitor_thread.is_alive():
                                        self.monitor_thread = threading.Thread(target=self.monitor_game_loop, daemon=True)
                                        self.monitor_thread.start()
                                    if not self.analyzer_thread.is_alive():
                                        self.analyzer_thread = threading.Thread(target=self.analyzer_loop, daemon=True)
                                        self.analyzer_thread.start()
                                else:
                                    self.ui.print_error("Falha ao reinicializar Chrome")
                                    # Tenta reinicializar completamente
                                    time.sleep(5)
                                    if not self.initialize(skip_login_on_failure=True):
                                        self.ui.print_error("Falha crítica - encerrando")
                                        break
                            else:
                                # Não estava logado, apenas reinicia
                                self.ui.print_info("Reiniciando Chrome sem login...")
                                if self.automation.restart_chrome():
                                    self.automation.driver.get(config.BLAZE_URL)
                                    time.sleep(3)
                                    self.automation.accept_cookies()
                                    self.automation.confirm_age()
                                    if self.automation.navigate_to_double():
                                        self.ui.print_success("Chrome reinicializado")
                                    else:
                                        self.ui.print_error("Falha ao navegar para o jogo após reinicialização")
                                        time.sleep(5)
                                        continue
                                else:
                                    self.ui.print_error("Falha ao reiniciar Chrome")
                                    time.sleep(5)
                                    continue
                        
                        # Verifica se ainda está logado (se tinha tentado fazer login)
                        if self.automation.login_attempted:
                            current_login_status = self.automation.check_if_logged_in()
                            if self.automation.is_logged_in and not current_login_status:
                                # Perdeu o login, tenta fazer login novamente
                                self.ui.print_warning("Login perdido - tentando fazer login novamente...")
                                if config.EMAIL and config.PASSWORD:
                                    if self.automation.login(config.EMAIL, config.PASSWORD):
                                        self.automation.is_logged_in = True
                                        self.ui.print_success("Login restaurado")
                                    else:
                                        self.ui.print_warning("Não foi possível restaurar login - continuando sem login")
                                        self.automation.is_logged_in = False
                    
                    # Obtém estado atual do jogo (da queue ou diretamente)
                    game_state = None
                    if not self.game_state_queue.empty():
                        game_state = self.game_state_queue.get()
                    else:
                        # Fallback: obtém diretamente se queue estiver vazia
                        try:
                            game_state = self.automation.get_current_game_state()
                        except Exception as e:
                            self.ui.print_warning(f"Erro ao obter estado do jogo: {e}")
                            time.sleep(1)
                            continue
                    
                    # Obtém histórico do banco
                    with self.lock:
                        history = self.db.get_recent_games(limit=config.HISTORY_SIZE)
                        stats = self.db.get_statistics()
                    
                    # Verifica se há nova previsão
                    if not self.prediction_queue.empty():
                        pred_data = self.prediction_queue.get()
                        current_prediction = pred_data['prediction']
                        history = pred_data['history']
                    
                    # Atualiza UI em intervalo configurável (mais responsivo)
                    if current_time - last_update >= config.UI_UPDATE_INTERVAL:
                        last_update = current_time
                        
                        # Limpa a tela e exibe informações
                        self.ui.clear_screen()
                        self.ui.print_header()
                        
                        # Exibe estatísticas
                        self.ui.display_statistics(stats)
                        self.ui.print_separator()
                        
                        # Exibe histórico de cores
                        if history:
                            self.ui.display_game_history(history[:24])
                            self.ui.print_separator()
                        
                        # Adapta estado para o formato esperado pela UI
                        ui_state = {
                            'timer_text': game_state.get('timer', ''),
                            'is_betting_period': game_state.get('can_bet', False),
                            'recent_colors': [g['color'] for g in history[:10] if g.get('color')]
                        }
                        self.ui.display_game_state(ui_state)
                        self.ui.print_separator()
                        
                        # Se estiver em período de aposta e não esperando resultado
                        if game_state and (game_state.get('can_bet', False) or game_state.get('is_betting_period', False)) and not waiting_for_result:
                            if current_prediction:
                                confidence = current_prediction['confidence']
                                
                                # Exibe previsão
                                self.ui.display_prediction(
                                    current_prediction['color'],
                                    confidence,
                                    current_prediction['patterns']
                                )
                                
                                self.ui.print_info(f"Sinal! Confiança: {confidence*100:.1f}%")
                                self.ui.print_info(f"Previsão: {current_prediction['color']}")
                                
                                # Notificações Telegram
                                # Envia aviso quando confiança está próxima (75%+)
                                if confidence >= config.TELEGRAM_WARNING_CONFIDENCE and confidence != last_warning_confidence:
                                    self.telegram.send_warning_message(
                                        confidence,
                                        current_prediction['color'],
                                        current_prediction.get('patterns', [])
                                    )
                                    last_warning_confidence = confidence
                                
                                # Envia oportunidade quando confiança está alta mas ainda não apostou (85%+)
                                if confidence >= config.TELEGRAM_BET_CONFIDENCE and confidence != last_opportunity_confidence and not current_bet_placed:
                                    self.telegram.send_bet_opportunity(
                                        confidence,
                                        current_prediction['color'],
                                        current_prediction.get('patterns', [])
                                    )
                                    last_opportunity_confidence = confidence
                                    opportunity_lost_sent = False  # Reset flag
                                
                                # Faz aposta automaticamente se confiança for suficiente
                                if confidence >= config.MIN_CONFIDENCE and not current_bet_placed:
                                    self.ui.print_info("Fazendo aposta...")
                                    
                                    # Gera e registra o ID do jogo/aposta atual
                                    self.current_bet_game_id = self.get_game_id()
                                    game_id = self.current_bet_game_id
                                    
                                    if self.automation.place_bet(
                                        current_prediction['color'],
                                        config.DEFAULT_BET_AMOUNT
                                    ):
                                        self.ui.print_success("Aposta realizada!")
                                        current_bet_placed = True
                                        waiting_for_result = True
                                        
                                        # Salva a aposta no banco
                                        with self.lock:
                                            self.db.save_bet(
                                                game_id,
                                                current_prediction['color'],
                                                config.DEFAULT_BET_AMOUNT,
                                                current_prediction['confidence']
                                            )
                                        
                                        # Envia notificação Telegram de aposta realizada
                                        self.telegram.send_bet_placed(
                                            current_prediction['color'],
                                            current_prediction['confidence'],
                                            config.DEFAULT_BET_AMOUNT
                                        )
                                    else:
                                        self.ui.print_error("Falha ao fazer aposta")
                            else:
                                self.ui.print_info("Analisando padrões...")
                                
                                # Verifica se havia uma oportunidade que não se concretizou
                                if last_opportunity_confidence >= config.TELEGRAM_BET_CONFIDENCE and not opportunity_lost_sent:
                                    if current_prediction and current_prediction['confidence'] < config.MIN_CONFIDENCE:
                                        # Confiança caiu abaixo do mínimo
                                        self.telegram.send_opportunity_lost(
                                            last_opportunity_confidence,
                                            current_prediction['color'] if current_prediction else "unknown",
                                            "Confiança caiu abaixo do mínimo"
                                        )
                                        opportunity_lost_sent = True
                                    elif not current_prediction:
                                        # Previsão desapareceu
                                        self.telegram.send_opportunity_lost(
                                            last_opportunity_confidence,
                                            "unknown",
                                            "Padrão não se confirmou"
                                        )
                                        opportunity_lost_sent = True
                        elif waiting_for_result:
                            # Aguarda resultado do jogo
                            self.ui.print_info("Aguardando resultado do jogo...")

                            # Tenta obter o resultado diretamente
                            result = self.automation.get_current_result()
                            if not result or not result.get('color'):
                                # Se não houver resultado direto, verifica indicação textual
                                timer_text = game_state.get('timer_text', '') if game_state else ''
                                timer_lower = timer_text.lower()
                                if game_state and ("girou" in timer_lower or "blaze girou" in timer_lower):
                                    time.sleep(1)
                                    result = self.automation.get_current_result()
                                    if not result:
                                        recent_results = self.automation.get_recent_results(limit=1)
                                        if recent_results:
                                            result = recent_results[0]

                            if result and current_prediction:
                                actual_color = result.get('color')
                                bet_result = "WIN" if actual_color == current_prediction['color'] else "LOSS"

                                # Atualiza aposta e persiste jogo
                                with self.lock:
                                    game_id = self.current_bet_game_id or self.get_game_id()
                                    self.db.update_bet_result(game_id, actual_color, bet_result)
                                    self.db.save_game(game_id, actual_color, result.get('number'))

                                # Exibe resultado
                                self.ui.display_bet_result(
                                    current_prediction['color'], actual_color, bet_result, current_prediction['confidence']
                                )

                                # Salva padrões se houver
                                if current_prediction.get('patterns'):
                                    with self.lock:
                                        for pattern in current_prediction['patterns']:
                                            self.db.save_pattern(
                                                pattern.get('type', 'unknown'), pattern, pattern.get('confidence', 0)
                                            )

                                # Envia notificação Telegram com resultado
                                with self.lock:
                                    stats = self.db.get_statistics()
                                    self.telegram.send_bet_result(
                                        current_prediction['color'],
                                        actual_color,
                                        bet_result,
                                        current_prediction['confidence'],
                                        stats.get('win_rate', 0.0),
                                        stats.get('total_bets', 0),
                                        stats.get('wins', 0)
                                    )

                                # Reseta flags
                                current_bet_placed = False
                                waiting_for_result = False
                                current_prediction = None
                                self.current_bet_game_id = None
                                last_warning_confidence = 0.0
                                last_opportunity_confidence = 0.0
                                opportunity_lost_sent = False
                                last_update = 0
                        else:
                            self.ui.print_info("Aguardando período de apostas...")
                            current_bet_placed = False
                            
                            # Verifica se havia uma oportunidade que não se concretizou (período de apostas expirou)
                            if last_opportunity_confidence >= config.TELEGRAM_BET_CONFIDENCE and not opportunity_lost_sent and not waiting_for_result:
                                if current_prediction:
                                    self.telegram.send_opportunity_lost(
                                        last_opportunity_confidence,
                                        current_prediction['color'],
                                        "Período de apostas expirou"
                                    )
                                else:
                                    self.telegram.send_opportunity_lost(
                                        last_opportunity_confidence,
                                        "unknown",
                                        "Período de apostas expirou"
                                    )
                                opportunity_lost_sent = True
                    
                    # Sleep muito curto para manter responsividade máxima
                    time.sleep(0.05)  # 50ms para máxima responsividade
                    
                except KeyboardInterrupt:
                    self.ui.print_warning("Interrompido pelo usuário")
                    self.running = False
                    break
                except Exception as e:
                    self.ui.print_error(f"Erro no loop principal: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # Se o erro está relacionado ao Chrome, tenta reinicializar
                    if "chrome" in str(e).lower() or "driver" in str(e).lower() or "timeout" in str(e).lower():
                        self.ui.print_warning("Erro relacionado ao Chrome detectado - tentando recuperar...")
                        time.sleep(2)
                        
                        # Tenta reinicializar
                        if self.automation.is_logged_in or self.automation.login_attempted:
                            if not self.automation.reinitialize_with_login_retry(
                                email=config.EMAIL if config.EMAIL and config.PASSWORD else None,
                                password=config.PASSWORD if config.EMAIL and config.PASSWORD else None,
                                max_retries=1
                            ):
                                # Se falhar, tenta reinicializar completamente
                                if not self.initialize(skip_login_on_failure=True):
                                    self.ui.print_error("Falha crítica na recuperação")
                                    time.sleep(5)
                    else:
                        time.sleep(1)
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpa recursos ao encerrar"""
        self.ui.print_info("Encerrando bot...")
        self.running = False
        
        # Aguarda threads finalizarem
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        if self.analyzer_thread:
            self.analyzer_thread.join(timeout=2)
        
        if self.automation:
            self.automation.close()
        self.ui.print_success("Bot encerrado")

