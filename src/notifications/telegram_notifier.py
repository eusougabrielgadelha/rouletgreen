"""
Módulo de notificações via Telegram
"""
import sys
import os

# Configura encoding UTF-8 para Windows
if sys.platform == 'win32':
    try:
        import codecs
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    except:
        pass

import asyncio
from typing import Optional, Dict
from datetime import datetime
try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("[AVISO] python-telegram-bot não instalado. Execute: pip install python-telegram-bot")

import sys
import os

# Adiciona o diretório raiz ao path para importar config
root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, os.path.abspath(root_dir))
from config import config


class TelegramNotifier:
    def __init__(self):
        self.bot = None
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.enabled = config.TELEGRAM_ENABLED and TELEGRAM_AVAILABLE
        self._loop = None
        self._thread = None
        
        # Controle de spam
        self.last_warning_sent = None
        self.last_bet_sent = None
        self.last_result_sent = None
        self.last_opportunity_lost_sent = None
        self.min_interval = 30  # Mínimo de 30 segundos entre mensagens do mesmo tipo
        
        if self.enabled:
            try:
                print(f"[INFO] Inicializando Telegram Bot...")
                print(f"[INFO] Chat ID: {config.TELEGRAM_CHAT_ID}")
                
                self.bot = Bot(token=config.TELEGRAM_TOKEN)
                # Testa conexão sem bloquear o event loop existente
                print(f"[INFO] Testando conexão com Telegram...")
                self._ensure_loop()
                # agenda no loop dedicado
                fut = asyncio.run_coroutine_threadsafe(self._test_connection(), self._loop)
                # aguarda brevemente só para validar
                try:
                    fut.result(timeout=5)
                    print(f"[SUCCESS] Telegram Bot inicializado (teste ok)")
                except Exception:
                    print(f"[AVISO] Teste de conexão agendado")
            except Exception as e:
                print(f"[ERRO] Erro ao inicializar Telegram: {e}")
                import traceback
                traceback.print_exc()
                self.enabled = False
    
    async def _test_connection(self):
        """Testa conexão com Telegram"""
        try:
            if self.bot:
                bot_info = await self.bot.get_me()
                print(f"[INFO] Conectado ao Telegram como: @{bot_info.username}")
                return True
        except Exception as e:
            print(f"[ERRO] Erro ao conectar Telegram: {e}")
            import traceback
            traceback.print_exc()
            self.enabled = False
            return False
        return False
    
    def _can_send_message(self, message_type: str) -> bool:
        """Verifica se pode enviar mensagem (evita spam)"""
        if not self.enabled:
            return False
        
        current_time = datetime.now().timestamp()
        
        if message_type == "warning":
            if self.last_warning_sent and (current_time - self.last_warning_sent) < self.min_interval:
                return False
        elif message_type == "bet":
            if self.last_bet_sent and (current_time - self.last_bet_sent) < self.min_interval:
                return False
        elif message_type == "result":
            if self.last_result_sent and (current_time - self.last_result_sent) < self.min_interval:
                return False
        elif message_type == "opportunity_lost":
            if self.last_opportunity_lost_sent and (current_time - self.last_opportunity_lost_sent) < self.min_interval:
                return False
        
        return True
    
    def _update_last_sent(self, message_type: str):
        """Atualiza timestamp da última mensagem enviada"""
        current_time = datetime.now().timestamp()
        if message_type == "warning":
            self.last_warning_sent = current_time
        elif message_type == "bet":
            self.last_bet_sent = current_time
        elif message_type == "result":
            self.last_result_sent = current_time
        elif message_type == "opportunity_lost":
            self.last_opportunity_lost_sent = current_time
    
    async def _send_message_async(self, message: str, parse_mode: str = "HTML"):
        """Envia mensagem assíncrona"""
        if not self.enabled or not self.bot:
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            print(f"[ERRO] Erro ao enviar mensagem Telegram: {e}")
            return False
        except Exception as e:
            print(f"[ERRO] Erro inesperado Telegram: {e}")
            return False
    
    def send_message(self, message: str, parse_mode: str = "HTML"):
        """Envia mensagem síncrona (wrapper)"""
        if not self.enabled:
            print(f"[AVISO] Telegram desabilitado - mensagem não será enviada")
            return False
        
        if not self.bot:
            print(f"[ERRO] Bot Telegram não inicializado")
            return False
        
        try:
            # Envia sempre via loop dedicado para evitar conflitos com outros loops
            self._ensure_loop()
            fut = asyncio.run_coroutine_threadsafe(self._send_message_async(message, parse_mode), self._loop)
            result = fut.result(timeout=10)
            if result:
                print(f"[SUCCESS] Mensagem enviada ao Telegram")
            else:
                print(f"[ERRO] Falha ao enviar mensagem ao Telegram")
            return result
        except Exception as e:
            print(f"[ERRO] Erro ao enviar mensagem: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ===== Loop dedicado =====
    def _ensure_loop(self):
        if self._loop and self._thread and self._thread.is_alive():
            return
        # Cria loop dedicado em thread separada para evitar conflitos com loops ativos
        self._loop = asyncio.new_event_loop()
        def _run():
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()
        import threading
        self._thread = threading.Thread(target=_run, name="telegram-loop", daemon=True)
        self._thread.start()
    
    def send_welcome_message(self):
        """Envia mensagem de boas-vindas quando o bot inicia"""
        if not self.enabled:
            print("[AVISO] Telegram desabilitado - mensagem de boas-vindas não será enviada")
            return False
        
        message = """
🎰 <b>BLAZE DOUBLE ANALYZER</b> 🎰

✅ <b>Bot Iniciado com Sucesso!</b>

📊 Sistema de análise ativado
🔍 Monitoramento em tempo real
📈 Análise de padrões ativa
💾 Banco de dados conectado

Aguardando padrões válidos para gerar palpites...

<i>O bot enviará notificações quando identificar oportunidades.</i>
"""
        result = self.send_message(message)
        if result:
            print("[SUCCESS] Mensagem de boas-vindas enviada ao Telegram")
        else:
            print("[ERRO] Falha ao enviar mensagem de boas-vindas ao Telegram")
        return result
    
    def send_warning_message(self, confidence: float, predicted_color: str, patterns: list = None):
        """Envia aviso quando confiança está próxima do limite"""
        if not self._can_send_message("warning"):
            return False
        
        if confidence < config.TELEGRAM_WARNING_CONFIDENCE:
            return False
        
        color_emoji = {
            'red': '🔴',
            'black': '⚫',
            'white': '⚪'
        }
        
        color_name = {
            'red': 'VERMELHO',
            'black': 'PRETO',
            'white': 'BRANCO'
        }
        
        emoji = color_emoji.get(predicted_color, '🎯')
        name = color_name.get(predicted_color, predicted_color.upper())
        
        patterns_text = ""
        if patterns:
            patterns_text = "\n\n📋 <b>Padrões Identificados:</b>\n"
            for pattern in patterns[:3]:  # Mostra apenas os 3 primeiros
                patterns_text += f"• {pattern.get('pattern', 'N/A')}\n"
        
        message = f"""
⚠️ <b>ATENÇÃO: Padrão Detectado!</b>

{emoji} <b>Previsão:</b> {name}
📊 <b>Confiança:</b> {confidence*100:.1f}%
🔍 <b>Status:</b> Analisando padrão...

<i>O bot está analisando se este padrão é válido para apostar.</i>
{patterns_text}

<i>Aguardando confirmação...</i>
"""
        
        if self.send_message(message):
            self._update_last_sent("warning")
            return True
        return False
    
    def send_bet_opportunity(self, confidence: float, predicted_color: str, patterns: list = None):
        """Envia quando há oportunidade de aposta (confiança alta mas ainda não apostou)"""
        if not self._can_send_message("bet"):
            return False
        
        if confidence < config.TELEGRAM_BET_CONFIDENCE:
            return False
        
        color_emoji = {
            'red': '🔴',
            'black': '⚫',
            'white': '⚪'
        }
        
        color_name = {
            'red': 'VERMELHO',
            'black': 'PRETO',
            'white': 'BRANCO'
        }
        
        emoji = color_emoji.get(predicted_color, '🎯')
        name = color_name.get(predicted_color, predicted_color.upper())
        
        patterns_text = ""
        if patterns:
            patterns_text = "\n\n📋 <b>Padrões Identificados:</b>\n"
            for pattern in patterns[:3]:
                patterns_text += f"• {pattern.get('pattern', 'N/A')}\n"
        
        message = f"""
💰 <b>OPORTUNIDADE DE APOSTA!</b>

{emoji} <b>Previsão:</b> {name}
📊 <b>Confiança:</b> {confidence*100:.1f}%
🎯 <b>Status:</b> Aguardando período de apostas...

<i>O bot está pronto para apostar quando o período de apostas abrir.</i>
{patterns_text}

<i>Fique atento!</i>
"""
        
        if self.send_message(message):
            self._update_last_sent("bet")
            return True
        return False
    
    def send_opportunity_lost(self, confidence: float, predicted_color: str, reason: str = "Período de apostas expirou"):
        """Envia quando oportunidade não se concretizou"""
        if not self._can_send_message("opportunity_lost"):
            return False
        
        color_emoji = {
            'red': '🔴',
            'black': '⚫',
            'white': '⚪'
        }
        
        color_name = {
            'red': 'VERMELHO',
            'black': 'PRETO',
            'white': 'BRANCO'
        }
        
        emoji = color_emoji.get(predicted_color, '🎯')
        name = color_name.get(predicted_color, predicted_color.upper())
        
        message = f"""
❌ <b>Oportunidade Não Concretizada</b>

{emoji} <b>Previsão:</b> {name}
📊 <b>Confiança:</b> {confidence*100:.1f}%
⚠️ <b>Motivo:</b> {reason}

<i>A oportunidade passou. Aguardando próximos padrões...</i>
"""
        
        if self.send_message(message):
            self._update_last_sent("opportunity_lost")
            return True
        return False
    
    def send_bet_placed(self, predicted_color: str, confidence: float, bet_amount: float):
        """Envia quando aposta foi realizada"""
        if not self._can_send_message("bet"):
            return False
        
        color_emoji = {
            'red': '🔴',
            'black': '⚫',
            'white': '⚪'
        }
        
        color_name = {
            'red': 'VERMELHO',
            'black': 'PRETO',
            'white': 'BRANCO'
        }
        
        emoji = color_emoji.get(predicted_color, '🎯')
        name = color_name.get(predicted_color, predicted_color.upper())
        
        message = f"""
✅ <b>APOSTA REALIZADA!</b>

{emoji} <b>Cor Apostada:</b> {name}
📊 <b>Confiança:</b> {confidence*100:.1f}%
💰 <b>Valor:</b> R$ {bet_amount:.2f}
⏳ <b>Status:</b> Aguardando resultado...

<i>O resultado será enviado assim que disponível.</i>
"""
        
        if self.send_message(message):
            self._update_last_sent("bet")
            return True
        return False
    
    def send_bet_result(self, predicted_color: str, actual_color: str, result: str, 
                       confidence: float, win_rate: float, total_bets: int, wins: int):
        """Envia resultado da aposta com estatísticas"""
        if not self._can_send_message("result"):
            return False
        
        color_emoji = {
            'red': '🔴',
            'black': '⚫',
            'white': '⚪'
        }
        
        color_name = {
            'red': 'VERMELHO',
            'black': 'PRETO',
            'white': 'BRANCO'
        }
        
        predicted_emoji = color_emoji.get(predicted_color, '🎯')
        predicted_name = color_name.get(predicted_color, predicted_color.upper())
        actual_emoji = color_emoji.get(actual_color, '🎯')
        actual_name = color_name.get(actual_color, actual_color.upper())
        
        if result == "WIN":
            result_emoji = "✅"
            result_text = "GREEN"
            result_color = "green"
        else:
            result_emoji = "❌"
            result_text = "LOSS"
            result_color = "red"
        
        message = f"""
{result_emoji} <b>RESULTADO DA APOSTA</b>

🎯 <b>Previsão:</b> {predicted_emoji} {predicted_name}
🎲 <b>Resultado:</b> {actual_emoji} {actual_name}
📊 <b>Confiança:</b> {confidence*100:.1f}%

<b>{result_text}</b>

📈 <b>Estatísticas:</b>
• Taxa de Acerto: <b>{win_rate:.1f}%</b>
• Total de Apostas: {total_bets}
• Vitórias: {wins}
• Derrotas: {total_bets - wins}
"""
        
        if self.send_message(message):
            self._update_last_sent("result")
            return True
        return False

