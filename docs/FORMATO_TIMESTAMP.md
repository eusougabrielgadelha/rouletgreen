# 📅 Formato de Timestamp no Banco de Dados

## ✅ Confirmação

**SIM, todos os dados estão sendo salvos com data, hora, minuto, segundo e microssegundos.**

---

## 📊 Formato Utilizado

### Formato Padrão:
```
YYYY-MM-DD HH:MM:SS.ffffff
```

### Exemplo:
```
2025-11-04 00:07:19.458113
```

### Componentes:
- **YYYY-MM-DD**: Data (ano-mês-dia)
- **HH:MM:SS**: Hora (hora:minuto:segundo)
- **ffffff**: Microssegundos (6 dígitos)

---

## 🗄️ Tabelas que Usam Timestamp

### 1. **games** (Jogos)
- Campo: `timestamp DATETIME`
- Formato: `YYYY-MM-DD HH:MM:SS.ffffff`
- Quando: Sempre que um jogo é salvo
- Função: `get_timestamp()`

### 2. **bets** (Apostas)
- Campo: `timestamp DATETIME`
- Formato: `YYYY-MM-DD HH:MM:SS.ffffff`
- Quando: Sempre que uma aposta é feita
- Função: `get_timestamp()`

### 3. **patterns** (Padrões)
- Campo: `last_seen DATETIME`
- Campo: `created_at DATETIME`
- Formato: `YYYY-MM-DD HH:MM:SS.ffffff`
- Quando: Sempre que um padrão é identificado
- Função: `get_timestamp()`

### 4. **statistics** (Estatísticas)
- Campo: `last_updated DATETIME`
- Formato: `YYYY-MM-DD HH:MM:SS.ffffff`
- Quando: Sempre que estatísticas são atualizadas
- Função: `get_timestamp()`

### 5. **sequences** (Sequências)
- Campo: `timestamp DATETIME`
- Formato: `YYYY-MM-DD HH:MM:SS.ffffff`
- Quando: Sempre que uma sequência é coletada
- Função: `get_timestamp()`

---

## 🔧 Função Utilizada

### `get_timestamp()`
```python
def get_timestamp() -> str:
    """Retorna timestamp formatado com data, hora, minuto, segundo e microssegundos"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
```

### Características:
- ✅ **Data completa**: YYYY-MM-DD
- ✅ **Hora completa**: HH:MM:SS
- ✅ **Microssegundos**: .ffffff (6 dígitos)
- ✅ **Formato ISO**: Compatível com SQLite DATETIME
- ✅ **Precisão**: Até microssegundos

---

## 📝 Exemplos de Timestamps Salvos

### Jogo:
```
game_id: game_red_5_1733261239
color: red
number: 5
timestamp: 2025-11-04 00:07:19.458113
```

### Aposta:
```
game_id: game_1733261239
predicted_color: red
confidence: 0.95
timestamp: 2025-11-04 00:07:20.123456
```

### Sequência:
```
sequence_length: 3
sequence_colors: red,black,white
timestamp: 2025-11-04 00:07:19.475427
```

---

## ✅ Validação

### Teste Realizado:
```python
from database import get_timestamp
print(get_timestamp())
# Output: 2025-11-04 00:07:19.420972
```

### Componentes Verificados:
- ✅ Data: `2025-11-04` (YYYY-MM-DD)
- ✅ Hora: `00:07:19` (HH:MM:SS)
- ✅ Microssegundos: `.420972` (6 dígitos)

---

## 🔍 Consultas SQL com Timestamp

### Por Data:
```sql
SELECT * FROM games 
WHERE DATE(timestamp) = '2025-11-04'
```

### Por Hora:
```sql
SELECT * FROM games 
WHERE strftime('%H', timestamp) = '23'
```

### Por Minuto:
```sql
SELECT * FROM games 
WHERE strftime('%M', timestamp) = '30'
```

### Por Segundo:
```sql
SELECT * FROM games 
WHERE strftime('%S', timestamp) = '45'
```

### Ordenação:
```sql
SELECT * FROM games 
ORDER BY timestamp DESC
```

---

## 📊 Análise Temporal

Com o timestamp completo, podemos analisar:
- ✅ Padrões por **dia da semana**
- ✅ Padrões por **hora do dia**
- ✅ Padrões por **minuto** (útil para jogos rápidos)
- ✅ Padrões por **segundo** (útil para análise detalhada)
- ✅ Intervalos entre jogos
- ✅ Frequência de jogos por período

---

## ✅ Conclusão

**Todos os dados estão sendo salvos com:**
- ✅ Data completa (YYYY-MM-DD)
- ✅ Hora completa (HH:MM:SS)
- ✅ Microssegundos (.ffffff)
- ✅ Precisão de até 6 dígitos de microssegundos

**Formato padrão**: `YYYY-MM-DD HH:MM:SS.ffffff`

**Função utilizada**: `get_timestamp()` garante formato consistente em todas as inserções.

