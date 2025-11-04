"""
Configurações do projeto
"""
import os
from dotenv import load_dotenv

load_dotenv()

# URLs
BLAZE_URL = "https://blaze.bet.br/pt/"
DOUBLE_URL = "https://blaze.bet.br/pt/games/double"

# Credenciais (configure exclusivamente via variáveis de ambiente)
EMAIL = os.getenv("BLAZE_EMAIL", "")
PASSWORD = os.getenv("BLAZE_PASSWORD", "")

# Configurações do navegador
# Detecta automaticamente se está em servidor (sem display)
import os
if not os.getenv('DISPLAY') or os.getenv('DISPLAY') == '':
    HEADLESS = True  # Servidor sem display - força headless
else:
    HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'  # Pode ser sobrescrito via .env
WAIT_TIME = 2  # Tempo de espera padrão em segundos

# Caminho do executável do Google Chrome (Windows)
# Se estiver em outro local, ajuste esta constante.
CHROME_BINARY = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

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

# Recuperação automática (reinicializações). Se houver conflito com asyncio/Playwright, defina como false
AUTO_RECOVERY_ENABLED = os.getenv('AUTO_RECOVERY_ENABLED', 'true').lower() == 'true'
RECOVERY_MAX_ATTEMPTS = int(os.getenv('RECOVERY_MAX_ATTEMPTS', '3'))
RECOVERY_BACKOFF_BASE = float(os.getenv('RECOVERY_BACKOFF_BASE', '3.0'))  # segundos

# Cores do jogo
COLORS = {
    "red": "Vermelho",
    "black": "Preto",
    "white": "Branco"
}

# Database
DATABASE_PATH = "blaze_data.db"

# Telegram Bot (opcional)
# Habilita automaticamente apenas se houver token e chat id válidos
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID", "")
TELEGRAM_ENABLED = (
    os.getenv("TELEGRAM_ENABLED", "auto").lower() == "true"
    or (
        os.getenv("TELEGRAM_ENABLED", "auto").lower() == "auto" and
        bool(TELEGRAM_TOKEN) and bool(TELEGRAM_CHAT_ID)
    )
)

# Configurações de notificações Telegram
TELEGRAM_WARNING_CONFIDENCE = 0.75  # Envia aviso quando confiança está próxima (75%)
TELEGRAM_BET_CONFIDENCE = 0.85  # Envia quando confiança está alta mas ainda não apostou (85%)
TELEGRAM_MIN_CONFIDENCE = 0.60  # Confiança mínima para enviar qualquer mensagem

