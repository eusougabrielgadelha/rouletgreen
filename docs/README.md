# 🎰 Blaze Double Analyzer

Sistema robótico de análise e previsão de padrões para o jogo Double da plataforma Blaze.

## 📋 Funcionalidades

- ✅ Automação completa do navegador (aceita cookies, confirma idade, faz login)
- ✅ Análise de padrões do histórico de jogos
- ✅ Sistema de previsão baseado em múltiplos algoritmos
- ✅ Validação de sinais antes de apostar
- ✅ Armazenamento de histórico em banco de dados SQLite
- ✅ Interface CMD rica e informativa
- ✅ Medição de assertividade e estatísticas
- ✅ Identificação e aprendizado de padrões

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Google Chrome instalado
- Conta na Blaze (opcional, para apostas automáticas)

### Passos

1. Clone ou baixe o projeto:
```bash
cd roleta
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as credenciais (opcional):
```bash
# Copie o arquivo de exemplo
copy .env.example .env

# Edite o arquivo .env e adicione suas credenciais
BLAZE_EMAIL=seu_email@exemplo.com
BLAZE_PASSWORD=sua_senha_aqui
```

## 📖 Como Usar

### Execução Básica

```bash
python main.py
```

### Configurações

Você pode editar o arquivo `config.py` para ajustar:

- `HEADLESS`: True/False - Executar navegador sem interface gráfica
- `MIN_CONFIDENCE`: 0.0-1.0 - Confiança mínima para apostar
- `DEFAULT_BET_AMOUNT`: Valor padrão de aposta
- `HISTORY_SIZE`: Quantidade de jogos a analisar

## 🎯 Como Funciona

1. **Inicialização**: O bot acessa o site, aceita cookies, confirma idade e faz login (se configurado)

2. **Análise**: O sistema monitora o histórico de jogos e analisa padrões usando múltiplos algoritmos:
   - Análise de sequências
   - Análise de frequência
   - Análise de padrões alternados
   - Análise de tendências

3. **Previsão**: Com base nos padrões identificados, gera uma previsão com nível de confiança

4. **Validação**: Valida se o sinal é forte o suficiente para apostar

5. **Aposta**: Se validado, realiza a aposta automaticamente

6. **Resultado**: Aguarda o resultado e atualiza as estatísticas

7. **Aprendizado**: Armazena padrões e resultados para melhorar previsões futuras

## 📊 Interface

O bot exibe em tempo real:

- 📈 Estatísticas (taxa de acerto, lucro, etc.)
- 🎲 Histórico de jogos recentes
- 🎯 Previsões com nível de confiança
- 🎮 Estado atual do jogo
- ✅ Resultados das apostas

## ⚠️ Avisos Importantes

- **Este é um projeto educacional**. Não garante lucros ou resultados positivos
- **Jogos de azar envolvem risco**. Use com responsabilidade
- **A análise de padrões não garante previsões corretas**
- **Configure valores de aposta adequados ao seu orçamento**

## 🗂️ Estrutura do Projeto

```
roleta/
├── main.py              # Script principal
├── config.py            # Configurações
├── database.py          # Gerenciamento de banco de dados
├── web_automation.py    # Automação web com Selenium
├── pattern_analyzer.py  # Análise de padrões
├── ui.py                # Interface de linha de comando
├── requirements.txt     # Dependências
├── .env.example        # Exemplo de configuração
└── README.md           # Este arquivo
```

## 🔧 Dependências

- `selenium`: Automação web
- `webdriver-manager`: Gerenciamento de drivers
- `rich`: Interface de linha de comando rica
- `sqlalchemy`: ORM para banco de dados
- `numpy` e `pandas`: Análise de dados

## 📝 Licença

Este projeto é fornecido "como está", sem garantias. Use por sua conta e risco.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se livre para abrir issues ou pull requests.

---

**Desenvolvido para fins educacionais e de análise de padrões**

