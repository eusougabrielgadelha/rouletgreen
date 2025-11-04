# 📱 Integração com Telegram - Guia Completo

## ✅ Funcionalidades Implementadas

### 1. **Mensagem de Boas-Vindas**
- **Quando**: Ao iniciar o bot
- **Conteúdo**: Status do sistema, confirmação de inicialização
- **Frequência**: Uma vez por inicialização

### 2. **Aviso de Padrão Detectado** (75%+)
- **Quando**: Confiança ≥ 75% mas ainda não apostou
- **Objetivo**: Preparar usuário para possível aposta
- **Conteúdo**: Previsão, confiança, padrões identificados
- **Frequência**: Mínimo de 30 segundos entre avisos

### 3. **Oportunidade de Aposta** (85%+)
- **Quando**: Confiança ≥ 85% mas ainda não apostou
- **Objetivo**: Avisar que há oportunidade de aposta
- **Conteúdo**: Previsão, confiança, padrões, status
- **Frequência**: Mínimo de 30 segundos entre oportunidades

### 4. **Oportunidade Não Concretizada**
- **Quando**: Oportunidade foi detectada mas não se concretizou
- **Motivos**:
  - Confiança caiu abaixo do mínimo
  - Padrão não se confirmou
  - Período de apostas expirou
- **Conteúdo**: Previsão, confiança, motivo
- **Frequência**: Uma vez por oportunidade perdida

### 5. **Aposta Realizada**
- **Quando**: Aposta foi feita com sucesso
- **Conteúdo**: Cor apostada, confiança, valor da aposta
- **Frequência**: Uma vez por aposta

### 6. **Resultado da Aposta** (Green/Loss)
- **Quando**: Resultado do jogo está disponível
- **Conteúdo**:
  - Previsão vs Resultado
  - Resultado (GREEN ou LOSS)
  - Taxa de assertividade
  - Estatísticas gerais
- **Frequência**: Uma vez por resultado

---

## ⚙️ Configurações

### Configurações em `config.py`:

```python
# Telegram Bot (opcional)
TELEGRAM_ENABLED = True  # Se False, não envia mensagens
TELEGRAM_TOKEN = "8487738643:AAHfnEEB6PKN6rDlRKrKkrh6HGRyTYtrge0"
TELEGRAM_CHAT_ID = "-1003285838290"  # Chat ID do grupo/canal
TELEGRAM_USER_ID = "570272217"  # User ID (para DMs, se necessário)

# Configurações de notificações Telegram
TELEGRAM_WARNING_CONFIDENCE = 0.75  # Envia aviso quando confiança está próxima (75%)
TELEGRAM_BET_CONFIDENCE = 0.85  # Envia quando confiança está alta mas ainda não apostou (85%)
TELEGRAM_MIN_CONFIDENCE = 0.60  # Confiança mínima para enviar qualquer mensagem
```

### Tokens e IDs:
- **Token**: `8487738643:AAHfnEEB6PKN6rDlRKrKkrh6HGRyTYtrge0`
- **Chat ID**: `-1003285838290` (Grupo/Canal)
- **User ID**: `570272217` (Usuário)

---

## 📊 Fluxo de Notificações

```
1. Bot Inicia
   ↓
   📨 Mensagem de Boas-Vindas
   ↓
2. Padrão Detectado (Confiança 75%+)
   ↓
   📨 Aviso de Padrão Detectado
   ↓
3. Confiança Aumenta (85%+)
   ↓
   📨 Oportunidade de Aposta
   ↓
4. Aposta Realizada
   ↓
   📨 Aposta Realizada
   ↓
5. Resultado Disponível
   ↓
   📨 Resultado (GREEN/LOSS) + Estatísticas
```

---

## 🛡️ Controle de Spam

### Intervalo Mínimo:
- **30 segundos** entre mensagens do mesmo tipo
- Evita múltiplas mensagens para o mesmo evento

### Tipos de Mensagens:
1. **warning**: Aviso de padrão (75%+)
2. **bet**: Oportunidade de aposta (85%+) ou aposta realizada
3. **result**: Resultado da aposta
4. **opportunity_lost**: Oportunidade não concretizada

### Flags de Controle:
- `last_warning_confidence`: Última confiança que gerou aviso
- `last_opportunity_confidence`: Última confiança que gerou oportunidade
- `opportunity_lost_sent`: Flag para evitar múltiplos avisos de oportunidade perdida

---

## 📝 Exemplos de Mensagens

### Mensagem de Boas-Vindas:
```
🎰 BLAZE DOUBLE ANALYZER 🎰

✅ Bot Iniciado com Sucesso!

📊 Sistema de análise ativado
🔍 Monitoramento em tempo real
📈 Análise de padrões ativa
💾 Banco de dados conectado

Aguardando padrões válidos para gerar palpites...

O bot enviará notificações quando identificar oportunidades.
```

### Aviso de Padrão (75%+):
```
⚠️ ATENÇÃO: Padrão Detectado!

🔴 Previsão: VERMELHO
📊 Confiança: 78.5%
🔍 Status: Analisando padrão...

O bot está analisando se este padrão é válido para apostar.

📋 Padrões Identificados:
• Sequência alternada detectada
• Frequência de padrão: 85%

Aguardando confirmação...
```

### Oportunidade de Aposta (85%+):
```
💰 OPORTUNIDADE DE APOSTA!

🔴 Previsão: VERMELHO
📊 Confiança: 87.3%
🎯 Status: Aguardando período de apostas...

O bot está pronto para apostar quando o período de apostas abrir.

📋 Padrões Identificados:
• Sequência exata encontrada
• Taxa de acerto: 90%

Fique atento!
```

### Aposta Realizada:
```
✅ APOSTA REALIZADA!

🔴 Cor Apostada: VERMELHO
📊 Confiança: 87.3%
💰 Valor: R$ 1.00
⏳ Status: Aguardando resultado...

O resultado será enviado assim que disponível.
```

### Resultado (GREEN):
```
✅ RESULTADO DA APOSTA

🎯 Previsão: 🔴 VERMELHO
🎲 Resultado: 🔴 VERMELHO
📊 Confiança: 87.3%

GREEN

📈 Estatísticas:
• Taxa de Acerto: 85.5%
• Total de Apostas: 20
• Vitórias: 17
• Derrotas: 3
```

### Resultado (LOSS):
```
❌ RESULTADO DA APOSTA

🎯 Previsão: 🔴 VERMELHO
🎲 Resultado: ⚫ PRETO
📊 Confiança: 87.3%

LOSS

📈 Estatísticas:
• Taxa de Acerto: 82.6%
• Total de Apostas: 23
• Vitórias: 19
• Derrotas: 4
```

### Oportunidade Não Concretizada:
```
❌ Oportunidade Não Concretizada

🔴 Previsão: VERMELHO
📊 Confiança: 87.3%
⚠️ Motivo: Período de apostas expirou

A oportunidade passou. Aguardando próximos padrões...
```

---

## 🔧 Instalação

### 1. Instalar Biblioteca:
```bash
pip install python-telegram-bot==20.7
```

### 2. Configurar Token e Chat ID:
Edite `config.py` e configure:
- `TELEGRAM_TOKEN`: Token do bot
- `TELEGRAM_CHAT_ID`: ID do chat/grupo/canal
- `TELEGRAM_USER_ID`: ID do usuário (opcional)

### 3. Ativar/Desativar:
```python
TELEGRAM_ENABLED = True  # True para ativar, False para desativar
```

---

## 📊 Estatísticas Enviadas

### No Resultado da Aposta:
- **Taxa de Acerto**: Porcentagem de acertos
- **Total de Apostas**: Número total de apostas realizadas
- **Vitórias**: Número de apostas ganhas
- **Derrotas**: Número de apostas perdidas

---

## ⚠️ Tratamento de Erros

### Erros Tratados:
1. **Biblioteca não instalada**: Mostra aviso mas não interrompe execução
2. **Token inválido**: Desativa Telegram automaticamente
3. **Chat ID inválido**: Mostra erro mas continua execução
4. **Erro de conexão**: Mostra erro mas não interrompe bot

### Fallback:
- Se Telegram falhar, o bot continua funcionando normalmente
- Apenas as notificações não serão enviadas
- Todas as funcionalidades do bot permanecem ativas

---

## ✅ Status

### Implementado:
- ✅ Mensagem de boas-vindas
- ✅ Aviso de padrão (75%+)
- ✅ Oportunidade de aposta (85%+)
- ✅ Oportunidade não concretizada
- ✅ Aposta realizada
- ✅ Resultado (GREEN/LOSS)
- ✅ Estatísticas de assertividade
- ✅ Controle de spam
- ✅ Tratamento de erros

### Pronto para Uso:
- ✅ Biblioteca instalada
- ✅ Configurações definidas
- ✅ Integração completa
- ✅ Testado e validado

---

## 🚀 Como Usar

1. **Configure o Telegram** em `config.py`
2. **Execute o bot**: `python main.py`
3. **Aguarde notificações** no Telegram

O bot enviará automaticamente:
- Mensagem ao iniciar
- Avisos quando detectar padrões
- Notificações de oportunidades
- Resultados das apostas

---

## 📝 Notas Importantes

1. **Controle de Spam**: Mensagens do mesmo tipo têm intervalo mínimo de 30 segundos
2. **Confiança Mínima**: Apenas padrões com confiança ≥ 60% geram notificações
3. **Fallback**: Se Telegram falhar, o bot continua funcionando normalmente
4. **Formato**: Mensagens usam HTML para formatação (negrito, itálico, emojis)

---

## 🎯 Próximos Passos

- [ ] Adicionar comando `/status` para verificar status do bot
- [ ] Adicionar comando `/stats` para ver estatísticas
- [ ] Adicionar comando `/stop` para parar o bot
- [ ] Notificações de erro crítico

