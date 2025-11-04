# 🎰 Blaze Double Analyzer - Bot de Análise e Previsão

Bot inteligente para análise e previsão de resultados do jogo Double da plataforma Blaze, utilizando técnicas avançadas de web scraping, análise de padrões e machine learning.

## 🚀 Funcionalidades Principais

### ✨ Automação Web Avançada
- **Bypass do Cloudflare Turnstile**: Utiliza `undetected-chromedriver` e técnicas de stealth para contornar proteções anti-bot
- **Interação Humana Realista**: Simula cliques reais, digitação letra por letra e movimentos de mouse naturais
- **Detecção Inteligente de Elementos**: Múltiplas estratégias de seleção (CSS, XPath, JavaScript) para máxima robustez
- **Sistema de Recuperação Automática**: Detecta travamentos e reinicializa o Chrome automaticamente

### 📊 Análise de Padrões
- **Análise de Sequências**: Identifica padrões em sequências de cores e números
- **Análise de Tendências**: Detecta tendências de vermelho, preto e branco
- **Múltiplos Algoritmos**: Implementa diversos algoritmos de previsão com diferentes níveis de confiança
- **Validação de Sinais**: Sistema de validação antes de enviar apostas

### 💾 Persistência de Dados
- **Banco de Dados SQLite**: Armazena histórico completo de jogos, apostas e padrões
- **Timestamps Precisos**: Registra data, hora, minuto, segundo e microssegundos
- **Coleta de Sequências**: Armazena sequências de diferentes tamanhos para análise futura
- **Estatísticas Detalhadas**: Taxa de acerto, lucro total, histórico completo

### 📱 Notificações Telegram
- **Mensagem de Boas-vindas**: Notifica quando o bot inicia
- **Avisos de Oportunidade**: Alerta quando confiança está alta (75%+)
- **Confirmação de Apostas**: Notifica quando uma aposta é realizada
- **Resultados em Tempo Real**: Envia resultado (WIN/LOSS) com estatísticas

### 🔄 Sistema de Resiliência
- **Recuperação Automática**: Detecta e recupera de travamentos do Chrome
- **Reinicialização Inteligente**: Reinicia Chrome e tenta fazer login novamente se necessário
- **Modo Sem Login**: Continua funcionando mesmo se o login falhar
- **Verificação Periódica**: Monitora status do Chrome a cada 10 segundos

## 📁 Estrutura do Projeto

```
roleta/
├── src/
│   ├── core/           # Lógica principal do bot
│   ├── automation/     # Automação web (Selenium)
│   ├── database/       # Gerenciamento de banco de dados
│   ├── analysis/       # Análise de padrões e previsões
│   ├── ui/             # Interface de linha de comando
│   ├── notifications/  # Integração com Telegram
│   └── utils/          # Utilitários diversos
├── config/             # Configurações do projeto
├── scripts/            # Scripts auxiliares
├── docs/               # Documentação completa
├── main.py             # Ponto de entrada
└── requirements.txt     # Dependências Python
```

## 🛠️ Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Google Chrome instalado
- Conta no Blaze (opcional, para apostas)

### Passos de Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/eusougabrielgadelha/rouletgreen.git
cd rouletgreen
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente**
   - Crie um arquivo `.env` na raiz do projeto
   - Ou edite `config/config.py` diretamente

4. **Execute o bot**
```bash
python main.py
```

Ou no Windows:
```bash
run.bat
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)
```env
BLAZE_EMAIL=seu_email@exemplo.com
BLAZE_PASSWORD=sua_senha
```

### Configurações Principais (config/config.py)
- `MIN_CONFIDENCE`: Confiança mínima para apostar (0-1)
- `DEFAULT_BET_AMOUNT`: Valor padrão de aposta
- `TELEGRAM_ENABLED`: Habilitar notificações Telegram
- `HEADLESS`: Executar sem interface gráfica

## 📖 Documentação

Documentação completa disponível na pasta `docs/`:
- **ESTRUTURA_PROJETO.md**: Estrutura modular do projeto
- **TELEGRAM_INTEGRACAO.md**: Configuração do Telegram
- **MELHORIAS_LOGIN.md**: Melhorias no processo de login
- **PLANO_ANALISE_SEQUENCIAS.md**: Estratégias de análise

## 🔧 Tecnologias Utilizadas

- **Selenium**: Automação web
- **undetected-chromedriver**: Bypass do Cloudflare
- **BeautifulSoup4**: Parsing HTML
- **SQLite3**: Banco de dados
- **python-telegram-bot**: Integração Telegram
- **Rich**: Interface de linha de comando avançada

## 🎯 Funcionalidades em Detalhe

### Análise de Padrões
- Identifica padrões de sequências (3, 5, 7, 10, 15, 20, 24)
- Analisa tendências de cores
- Calcula confiança baseada em histórico
- Valida sinais antes de apostar

### Sistema de Recuperação
- Detecta travamentos do Chrome automaticamente
- Reinicializa o navegador quando necessário
- Tenta fazer login novamente se perder sessão
- Continua funcionando mesmo sem login (modo análise)

### Bypass do Cloudflare
- Utiliza `undetected-chromedriver` para evitar detecção
- Injeta scripts de stealth no navegador
- Remove flags de automação
- Protege contra fingerprinting

## 📊 Estatísticas

O bot calcula e exibe:
- Taxa de acerto (win rate)
- Total de apostas
- Total de vitórias/derrotas
- Lucro total
- Histórico completo de jogos

## 🔒 Segurança

- Credenciais armazenadas via variáveis de ambiente
- `.env` incluído no `.gitignore`
- Banco de dados local (não compartilhado)
- Comunicação Telegram segura via HTTPS

## 📝 Licença

Este projeto é fornecido "como está", sem garantias. Use por sua conta e risco.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

## ⚠️ Aviso Legal

Este bot é apenas para fins educacionais e de pesquisa. O uso para apostas reais é de sua responsabilidade. Respeite os termos de serviço da plataforma Blaze.

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação em `docs/`
2. Execute `scripts/analyze_database.py` para analisar o banco de dados
3. Verifique os logs no console

---

**Desenvolvido com ❤️ para análise de padrões e aprendizado de máquina aplicado a jogos de azar.**
