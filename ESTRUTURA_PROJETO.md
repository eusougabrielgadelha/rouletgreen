# 📁 Estrutura do Projeto Blaze Double Analyzer

## 🎯 Estrutura Modular

```
roleta/
├── src/                          # 📦 Código fonte principal
│   ├── __init__.py
│   ├── core/                     # 🎯 Lógica principal
│   │   ├── __init__.py
│   │   └── bot.py               # Classe BlazeBot (coordenação)
│   ├── automation/              # 🤖 Automação web
│   │   ├── __init__.py
│   │   └── web_automation.py   # Selenium automation
│   ├── database/                # 💾 Banco de dados
│   │   ├── __init__.py
│   │   └── database.py          # SQLite operations
│   ├── analysis/                # 📊 Análise de padrões
│   │   ├── __init__.py
│   │   └── pattern_analyzer.py  # Pattern analysis
│   ├── notifications/           # 📱 Notificações
│   │   ├── __init__.py
│   │   └── telegram_notifier.py # Telegram bot
│   ├── ui/                      # 🖥️ Interface
│   │   ├── __init__.py
│   │   └── ui.py                # CLI interface (Rich)
│   └── utils/                   # 🛠️ Utilitários
│       ├── __init__.py
│       └── encoding.py          # UTF-8 encoding setup
│
├── scripts/                      # 📜 Scripts auxiliares
│   ├── analyze_database.py     # Análise do banco
│   └── fix_chromedriver.py     # Fix ChromeDriver
│
├── config/                       # ⚙️ Configurações
│   ├── __init__.py
│   └── config.py                # Configurações do projeto
│
├── docs/                         # 📚 Documentação
│   ├── README.md                # Documentação completa
│   ├── INSTALL.md               # Guia de instalação
│   ├── PLANO_ANALISE_SEQUENCIAS.md
│   ├── TELEGRAM_INTEGRACAO.md
│   └── ... (outros documentos)
│
├── main.py                       # 🚀 Ponto de entrada
├── requirements.txt             # 📦 Dependências
├── run.bat                      # 🪟 Script Windows
└── README.md                    # 📖 README principal
```

## 📦 Módulos e Responsabilidades

### `src/core/`
**Responsabilidade**: Lógica principal e coordenação
- `bot.py`: Classe `BlazeBot` que coordena todos os módulos
- Gerencia threads de monitoramento e análise
- Controla fluxo principal do bot

### `src/automation/`
**Responsabilidade**: Automação web
- `web_automation.py`: Classe `BlazeAutomation`
- Interações com Selenium
- Navegação, login, extração de dados
- Detecção de mudanças no DOM

### `src/database/`
**Responsabilidade**: Persistência de dados
- `database.py`: Classe `Database`
- Operações SQLite
- Gerenciamento de jogos, apostas, padrões, sequências
- Estatísticas e queries

### `src/analysis/`
**Responsabilidade**: Análise e previsão
- `pattern_analyzer.py`: Classe `PatternAnalyzer`
- Análise de padrões
- Geração de previsões
- Algoritmos de análise

### `src/notifications/`
**Responsabilidade**: Notificações externas
- `telegram_notifier.py`: Classe `TelegramNotifier`
- Integração com Telegram
- Envio de mensagens
- Controle de spam

### `src/ui/`
**Responsabilidade**: Interface do usuário
- `ui.py`: Classe `UI`
- Interface de linha de comando
- Visualização de dados com Rich
- Formatação e display

### `src/utils/`
**Responsabilidade**: Utilitários gerais
- `encoding.py`: Configuração UTF-8
- Funções auxiliares

## 🔄 Fluxo de Execução

```
main.py
  ↓
src.core.BlazeBot
  ↓
├── src.automation.BlazeAutomation (web)
├── src.database.Database (dados)
├── src.analysis.PatternAnalyzer (análise)
├── src.ui.UI (interface)
└── src.notifications.TelegramNotifier (telegram)
```

## 📝 Como Usar os Módulos

### Importar Módulos

```python
# Classe principal
from src.core import BlazeBot

# Módulos individuais
from src.automation import BlazeAutomation
from src.database import Database
from src.analysis import PatternAnalyzer
from src.notifications import TelegramNotifier
from src.ui import UI

# Utilitários
from src.utils.encoding import setup_encoding
```

### Executar Scripts

```bash
# Bot principal
python main.py

# Análise do banco
python scripts/analyze_database.py

# Fix ChromeDriver
python scripts/fix_chromedriver.py
```

## ✅ Benefícios da Modularização

1. **Organização**: Código organizado por responsabilidade
2. **Manutenibilidade**: Fácil localizar e modificar código
3. **Reutilização**: Módulos podem ser usados independentemente
4. **Testabilidade**: Fácil criar testes unitários
5. **Escalabilidade**: Fácil adicionar novos recursos
6. **Legibilidade**: Código mais limpo e fácil de entender

## 🔧 Configuração de Imports

Todos os módulos usam imports absolutos:

```python
# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.abspath(root_dir))

# Importa usando caminho absoluto
from src.database import Database
from config import config
```

## 📊 Dependências entre Módulos

```
BlazeBot (core)
    ├── BlazeAutomation (automation)
    ├── Database (database)
    ├── PatternAnalyzer (analysis)
    │   └── Database (database)
    ├── UI (ui)
    └── TelegramNotifier (notifications)
        └── config (config)
```

## 🎯 Próximos Passos

1. ✅ Estrutura criada
2. ✅ Arquivos movidos
3. ✅ Imports atualizados
4. ⏳ Testes unitários (futuro)
5. ⏳ Documentação de API (futuro)
6. ⏳ Logging estruturado (futuro)

