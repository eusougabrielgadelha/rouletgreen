# 📁 Estrutura Modular do Projeto

## 🎯 Nova Estrutura

```
roleta/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── bot.py          # Classe BlazeBot principal
│   │   └── game_state.py    # Gerenciamento de estado do jogo
│   ├── automation/
│   │   ├── __init__.py
│   │   └── web_automation.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── pattern_analyzer.py
│   │   └── sequence_collector.py
│   ├── notifications/
│   │   ├── __init__.py
│   │   └── telegram_notifier.py
│   ├── ui/
│   │   ├── __init__.py
│   │   └── ui.py
│   └── utils/
│       ├── __init__.py
│       ├── encoding.py      # Configuração de encoding UTF-8
│       └── helpers.py      # Funções auxiliares
├── scripts/
│   ├── analyze_database.py
│   └── fix_chromedriver.py
├── config/
│   ├── __init__.py
│   └── config.py
├── docs/
│   ├── *.md (todos os arquivos de documentação)
├── main.py                 # Ponto de entrada principal
├── requirements.txt
├── run.bat
└── README.md
```

## 📦 Módulos

### `src/core/`
- Lógica principal do bot
- Gerenciamento de estado
- Coordenação entre módulos

### `src/automation/`
- Automação web com Selenium
- Interações com o site Blaze

### `src/database/`
- Gerenciamento de banco de dados
- Operações CRUD
- Queries e estatísticas

### `src/analysis/`
- Análise de padrões
- Coleta de sequências
- Algoritmos de previsão

### `src/notifications/`
- Integração com Telegram
- Notificações e alertas

### `src/ui/`
- Interface de linha de comando
- Visualização de dados

### `src/utils/`
- Utilitários gerais
- Helpers e funções auxiliares

## 🔄 Migração

1. Criar estrutura de pastas
2. Mover arquivos para módulos apropriados
3. Atualizar imports
4. Criar __init__.py em cada módulo
5. Testar funcionamento

