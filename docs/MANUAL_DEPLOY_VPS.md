# 🚀 Manual de Deploy no VPS Ubuntu (Hostinger)

Guia completo passo a passo para configurar e executar o Blaze Double Analyzer no VPS Ubuntu usando PM2.

## 📋 Pré-requisitos

- VPS Ubuntu (Hostinger) com acesso SSH
- Git instalado no servidor
- Python 3.8+ instalado
- PM2 instalado globalmente
- Google Chrome ou Chromium instalado

---

## 🔐 Passo 1: Conectar via SSH

### 1.1 Obter credenciais SSH
- Acesse o painel da Hostinger
- Vá em **SSH Access** ou **Servidor**
- Anote:
  - **IP do servidor** (ex: `123.456.789.0`)
  - **Porta SSH** (geralmente `22`)
  - **Usuário SSH** (geralmente `root` ou `u123456789`)
  - **Senha SSH** ou chave privada

### 1.2 Conectar via SSH

**No Windows (PowerShell ou CMD):**
```bash
ssh usuario@ip_do_servidor -p porta
```

**Exemplo:**
```bash
ssh root@123.456.789.0 -p 22
```

**Ou se usar chave privada:**
```bash
ssh -i caminho/para/chave.pem usuario@ip_do_servidor -p porta
```

**No Linux/Mac:**
```bash
ssh usuario@ip_do_servidor -p porta
```

### 1.3 Verificar conexão
Após conectar, você verá algo como:
```
Welcome to Ubuntu 22.04 LTS
root@vps:~#
```

---

## 📦 Passo 2: Instalar Dependências do Sistema

### 2.1 Atualizar sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 2.2 Instalar Python e pip
```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 2.3 Instalar Google Chrome/Chromium
```bash
# Opção 1: Chromium (mais leve)
sudo apt install chromium-browser chromium-chromedriver -y

# Opção 2: Google Chrome (recomendado)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y
```

### 2.4 Instalar Git (se não estiver instalado)
```bash
sudo apt install git -y
```

### 2.5 Instalar PM2 globalmente
```bash
sudo npm install -g pm2
```

**Se não tiver Node.js/npm:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2
```

### 2.6 Instalar dependências do sistema para Chrome
```bash
sudo apt install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxshmfence1
```

---

## 📥 Passo 3: Clonar o Repositório

### 3.1 Navegar para diretório de projetos
```bash
cd /home
# ou
cd /opt
# ou
cd ~
```

### 3.2 Clonar o repositório
```bash
git clone https://github.com/eusougabrielgadelha/rouletgreen.git
```

### 3.3 Entrar no diretório do projeto
```bash
cd rouletgreen
```

---

## 🔧 Passo 4: Configurar o Ambiente Python

### 4.1 Criar ambiente virtual
```bash
python3 -m venv venv
```

### 4.2 Ativar ambiente virtual
```bash
source venv/bin/activate
```

### 4.3 Instalar dependências Python
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 Verificar instalação
```bash
python3 --version
pip list
```

---

## ⚙️ Passo 5: Configurar Variáveis de Ambiente

### 5.1 Criar arquivo .env
```bash
nano .env
```

### 5.2 Adicionar configurações
```env
BLAZE_EMAIL=seu_email@exemplo.com
BLAZE_PASSWORD=sua_senha
```

### 5.3 Salvar e sair
- Pressione `Ctrl + O` para salvar
- Pressione `Enter` para confirmar
- Pressione `Ctrl + X` para sair

### 5.4 Configurar permissões
```bash
chmod 600 .env
```

---

## 🔄 Passo 6: Atualizar o Código (Git Pull)

### 6.1 Verificar status do repositório
```bash
git status
```

### 6.2 Atualizar código do GitHub
```bash
git pull origin main
```

### 6.3 Se houver conflitos
```bash
# Verificar mudanças locais
git stash
git pull origin main
git stash pop
```

---

## 🚀 Passo 7: Configurar PM2

### 7.1 Criar arquivo de configuração PM2
```bash
nano ecosystem.config.js
```

### 7.2 Adicionar configuração do PM2
```javascript
module.exports = {
  apps: [{
    name: 'blaze-double-analyzer',
    script: 'main.py',
    interpreter: 'venv/bin/python3',
    cwd: '/home/rouletgreen',  // Ajuste o caminho conforme necessário
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      PYTHONUNBUFFERED: '1',
      DISPLAY: ':99'  // Para Chrome headless
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    time: true
  }]
};
```

**Ajuste o caminho `cwd` conforme o local onde você clonou o repositório!**

### 7.3 Criar diretório de logs
```bash
mkdir -p logs
```

---

## 🎯 Passo 8: Iniciar o Projeto com PM2

### 8.1 Iniciar aplicação
```bash
pm2 start ecosystem.config.js
```

### 8.2 Verificar status
```bash
pm2 status
```

### 8.3 Ver logs em tempo real
```bash
pm2 logs blaze-double-analyzer
```

### 8.4 Ver logs específicos
```bash
# Logs de saída
pm2 logs blaze-double-analyzer --lines 50

# Apenas erros
pm2 logs blaze-double-analyzer --err

# Apenas saída
pm2 logs blaze-double-analyzer --out
```

---

## 📊 Passo 9: Comandos Úteis do PM2

### 9.1 Gerenciamento básico
```bash
# Parar aplicação
pm2 stop blaze-double-analyzer

# Reiniciar aplicação
pm2 restart blaze-double-analyzer

# Recarregar aplicação (sem downtime)
pm2 reload blaze-double-analyzer

# Deletar aplicação do PM2
pm2 delete blaze-double-analyzer

# Parar e deletar
pm2 stop blaze-double-analyzer && pm2 delete blaze-double-analyzer
```

### 9.2 Monitoramento
```bash
# Dashboard interativo
pm2 monit

# Informações detalhadas
pm2 show blaze-double-analyzer

# Status resumido
pm2 list

# Uso de recursos
pm2 info blaze-double-analyzer
```

### 9.3 Logs
```bash
# Limpar logs
pm2 flush

# Ver logs com menos linhas
pm2 logs blaze-double-analyzer --lines 20

# Ver logs de erro
pm2 logs blaze-double-analyzer --err --lines 50
```

---

## 🔄 Passo 10: Atualizar Código no Servidor

### 10.1 Processo completo de atualização
```bash
# 1. Entrar no diretório do projeto
cd /home/rouletgreen  # Ajuste o caminho

# 2. Ativar ambiente virtual
source venv/bin/activate

# 3. Parar aplicação
pm2 stop blaze-double-analyzer

# 4. Atualizar código
git pull origin main

# 5. Atualizar dependências (se necessário)
pip install -r requirements.txt

# 6. Reiniciar aplicação
pm2 restart blaze-double-analyzer

# 7. Verificar logs
pm2 logs blaze-double-analyzer --lines 30
```

### 10.2 Script rápido de atualização
Crie um arquivo `update.sh`:
```bash
nano update.sh
```

Adicione:
```bash
#!/bin/bash
cd /home/rouletgreen  # Ajuste o caminho
source venv/bin/activate
pm2 stop blaze-double-analyzer
git pull origin main
pip install -r requirements.txt
pm2 restart blaze-double-analyzer
pm2 logs blaze-double-analyzer --lines 30
```

Tornar executável:
```bash
chmod +x update.sh
```

Usar:
```bash
./update.sh
```

---

## 🔧 Passo 11: Configurar PM2 para Iniciar no Boot

### 11.1 Salvar configuração atual
```bash
pm2 save
```

### 11.2 Gerar script de startup
```bash
pm2 startup
```

### 11.3 Executar comando gerado
O comando será algo como:
```bash
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u usuario --hp /home/usuario
```

**Copie e execute o comando exibido!**

### 11.4 Salvar novamente
```bash
pm2 save
```

Agora o PM2 iniciará automaticamente após reiniciar o servidor.

---

## 🐛 Passo 12: Resolução de Problemas

### 12.1 Chrome não encontrado
```bash
# Verificar se Chrome está instalado
which google-chrome
which chromium-browser

# Se não encontrar, instalar novamente
sudo apt install chromium-browser -y

# Ou usar Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y
```

### 12.2 Erro de permissões
```bash
# Dar permissões ao diretório
chmod -R 755 /home/rouletgreen

# Verificar permissões do .env
chmod 600 .env
```

### 12.3 Erro de dependências Python
```bash
# Ativar venv
source venv/bin/activate

# Reinstalar dependências
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 12.4 PM2 não inicia
```bash
# Verificar logs
pm2 logs blaze-double-analyzer --err

# Verificar se Python está correto
which python3
venv/bin/python3 --version

# Tentar iniciar manualmente primeiro
cd /home/rouletgreen
source venv/bin/activate
python3 main.py
```

### 12.5 Verificar se aplicação está rodando
```bash
# Verificar processos Python
ps aux | grep python

# Verificar processos Chrome
ps aux | grep chrome

# Verificar portas em uso
netstat -tulpn | grep python
```

---

## 📝 Passo 13: Verificar Funcionamento

### 13.1 Verificar logs
```bash
pm2 logs blaze-double-analyzer --lines 50
```

### 13.2 Verificar status
```bash
pm2 status
pm2 show blaze-double-analyzer
```

### 13.3 Monitorar em tempo real
```bash
pm2 monit
```

---

## 🔐 Passo 14: Segurança Adicional

### 14.1 Firewall (UFW)
```bash
# Verificar status
sudo ufw status

# Permitir SSH
sudo ufw allow 22/tcp

# Habilitar firewall (cuidado!)
sudo ufw enable
```

### 14.2 Proteger arquivo .env
```bash
# Garantir que .env não seja commitado
echo ".env" >> .gitignore

# Verificar permissões
ls -la .env
# Deve mostrar: -rw------- (600)
```

---

## 📋 Checklist Final

- [ ] SSH conectado com sucesso
- [ ] Python 3.8+ instalado
- [ ] Chrome/Chromium instalado
- [ ] Git instalado
- [ ] PM2 instalado
- [ ] Repositório clonado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] ecosystem.config.js criado
- [ ] PM2 iniciado com sucesso
- [ ] Logs funcionando
- [ ] PM2 configurado para iniciar no boot
- [ ] Aplicação rodando corretamente

---

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique os logs:**
   ```bash
   pm2 logs blaze-double-analyzer --err
   ```

2. **Verifique o status:**
   ```bash
   pm2 status
   pm2 show blaze-double-analyzer
   ```

3. **Teste manualmente:**
   ```bash
   cd /home/rouletgreen
   source venv/bin/activate
   python3 main.py
   ```

4. **Verifique dependências:**
   ```bash
   pip list
   python3 --version
   which python3
   ```

---

## 📚 Comandos Rápidos de Referência

```bash
# Conectar SSH
ssh usuario@ip -p porta

# Atualizar código
cd /home/rouletgreen && source venv/bin/activate && git pull origin main

# Reiniciar aplicação
pm2 restart blaze-double-analyzer

# Ver logs
pm2 logs blaze-double-analyzer

# Status
pm2 status

# Parar
pm2 stop blaze-double-analyzer

# Iniciar
pm2 start ecosystem.config.js
```

---

**Desenvolvido para facilitar o deploy no VPS Ubuntu da Hostinger** 🚀

