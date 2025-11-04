"""
Configurações do projeto
"""
import os
from dotenv import load_dotenv

load_dotenv()

# URLs
BLAZE_URL = "https://blaze.bet.br/pt/"
DOUBLE_URL = "https://blaze.bet.br/pt/games/double"

# Credenciais (deve ser configurado via variáveis de ambiente)
EMAIL = os.getenv("BLAZE_EMAIL", "gabrielgadelham@gmail.com")
PASSWORD = os.getenv("BLAZE_PASSWORD", "inDubai2023*")

# Configurações do navegador
HEADLESS = False  # True para rodar sem interface gráfica
WAIT_TIME = 2  # Tempo de espera padrão em segundos

# Configurações de aposta
MIN_BET_AMOUNT = 1.0  # Valor mínimo de aposta
DEFAULT_BET_AMOUNT = 1.0  # Valor padrão de aposta

# Configurações de análise
MIN_CONFIDENCE = 0.6  # Confiança mínima para enviar aposta (0-1)
HISTORY_SIZE = 50  # Quantidade de jogos anteriores a analisar

# Configurações de coleta de sequências (amostragens)
SEQUENCE_SIZES = [3, 5, 7, 10, 15, 20, 24]  # Tamanhos de sequências para coletar
COLLECT_SEQUENCES = True  # Se True, coleta sequências automaticamente
SEQUENCE_COLLECTION_INTERVAL = 5  # Intervalo em segundos para coletar sequências

# Configurações de performance
MONITOR_INTERVAL = 0.5  # Intervalo de monitoramento em segundos (durante apostas)
ANALYZER_INTERVAL = 0.3  # Intervalo de análise em segundos
UI_UPDATE_INTERVAL = 0.5  # Intervalo de atualização da UI em segundos

# Cores do jogo
COLORS = {
    "red": "Vermelho",
    "black": "Preto",
    "white": "Branco"
}

# Database
DATABASE_PATH = "blaze_data.db"

# Telegram Bot (opcional)
TELEGRAM_ENABLED = True  # Se False, não envia mensagens
TELEGRAM_TOKEN = "8487738643:AAHfnEEB6PKN6rDlRKrKkrh6HGRyTYtrge0"
TELEGRAM_CHAT_ID = "-1003285838290"  # Chat ID do grupo/canal
TELEGRAM_USER_ID = "570272217"  # User ID (para DMs, se necessário)

# Configurações de notificações Telegram
TELEGRAM_WARNING_CONFIDENCE = 0.75  # Envia aviso quando confiança está próxima (75%)
TELEGRAM_BET_CONFIDENCE = 0.85  # Envia quando confiança está alta mas ainda não apostou (85%)
TELEGRAM_MIN_CONFIDENCE = 0.60  # Confiança mínima para enviar qualquer mensagem

