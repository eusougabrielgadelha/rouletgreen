# 🎯 Condições para o Bot Dar Palpites

## Requisitos Obrigatórios

### 1. Histórico Mínimo
- **Mínimo**: 3 jogos coletados
- **Ideal**: Quanto mais jogos, melhor a análise
- O bot coleta automaticamente enquanto monitora

### 2. Confiança Mínima
- **Padrão**: 60% (0.6)
- **Configuração**: `MIN_CONFIDENCE` em `config.py`
- Apenas palpites com confiança ≥ 60% serão apostados

### 3. Período de Apostas
- Deve estar no período válido para apostar
- Timer não pode estar em "Girando" ou "Aguardando"

### 4. Padrão Identificado
- O analisador precisa identificar pelo menos um padrão:
  - Sequências repetidas
  - Frequência de cores
  - Padrões alternados
  - Tendências recentes
  - Associação número-cor

## ⚙️ Como Ajustar

### Para Começar Mais Rápido (Menor Confiança)
Edite `config.py`:
```python
MIN_CONFIDENCE = 0.5  # 50% em vez de 60%
```

### Para Ser Mais Conservador (Maior Confiança)
Edite `config.py`:
```python
MIN_CONFIDENCE = 0.7  # 70% em vez de 60%
```

### Para Analisar Mais Histórico
Edite `config.py`:
```python
HISTORY_SIZE = 100  # Analisa últimos 100 jogos (em vez de 50)
```

## 📊 Fluxo do Bot

1. **Monitoramento** → Coleta resultados automaticamente
2. **Acumulação** → Espera ter pelo menos 3 jogos
3. **Análise** → Analisa padrões quando há mudanças no DOM
4. **Validação** → Verifica se confiança ≥ 60%
5. **Aposta** → Faz aposta automaticamente se todas condições forem atendidas

## ⏱️ Tempo Estimado

- **Primeiros palpites**: ~3-5 minutos (após coletar histórico mínimo)
- **Frequência**: A cada período de apostas quando padrão válido é identificado

## 🔍 Mensagens que Você Verá

- `"Histórico insuficiente para análise"` → Ainda coletando jogos
- `"Analisando padrões..."` → Procurando padrões válidos
- `"Nenhum sinal válido identificado"` → Padrões não atingiram 60% de confiança
- `"Sinal! Confiança: XX%"` → Padrão válido encontrado!
- `"Fazendo aposta..."` → Aposta sendo realizada

