# 📦 Guia de Instalação

## Instalação Rápida

### Windows

1. **Instale o Python 3.8+**
   - Baixe em: https://www.python.org/downloads/
   - Marque a opção "Add Python to PATH" durante a instalação

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure suas credenciais (opcional)**
   - Crie um arquivo `.env` na pasta do projeto
   - Adicione suas credenciais:
   ```
   BLAZE_EMAIL=seu_email@exemplo.com
   BLAZE_PASSWORD=sua_senha_aqui
   ```

4. **Execute o bot**
   ```bash
   python main.py
   ```
   
   Ou use o script:
   ```bash
   run.bat
   ```

### Linux/Mac

1. **Instale o Python 3.8+**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3 python3-pip
   
   # Mac (com Homebrew)
   brew install python3
   ```

2. **Instale as dependências**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure suas credenciais**
   - Crie um arquivo `.env`:
   ```bash
   cp config_example.txt .env
   nano .env  # Edite com suas credenciais
   ```

4. **Execute o bot**
   ```bash
   python3 main.py
   ```

## Requisitos do Sistema

- **Python**: 3.8 ou superior
- **Google Chrome**: Versão mais recente
- **RAM**: Mínimo 2GB recomendado
- **Conexão**: Internet estável

## Solução de Problemas

### Erro: "ChromeDriver não encontrado"
- O webdriver-manager baixa automaticamente o driver
- Certifique-se de ter conexão com a internet

### Erro: "Módulo não encontrado"
- Execute: `pip install -r requirements.txt`
- Verifique se está usando Python 3.8+

### Erro: "Login falhou"
- Verifique suas credenciais no arquivo `.env`
- Certifique-se de que a conta está ativa

### Navegador não abre
- Verifique se o Chrome está instalado
- Tente desabilitar o modo headless em `config.py`

## Primeira Execução

Na primeira execução, o bot irá:
1. Baixar automaticamente o ChromeDriver
2. Criar o banco de dados SQLite
3. Abrir o navegador e fazer login (se configurado)
4. Começar a analisar os jogos

## Configuração Avançada

Edite o arquivo `config.py` para ajustar:
- Modo headless (sem interface gráfica)
- Confiança mínima para apostar
- Valor de aposta padrão
- Tamanho do histórico a analisar

