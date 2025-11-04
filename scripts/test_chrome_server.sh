#!/bin/bash

# Script de teste para verificar se o Chrome funciona no servidor
# Uso: ./test_chrome_server.sh

echo "🔍 Testando configuração do Chrome no servidor..."
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar se Chrome está instalado
echo "1️⃣  Verificando se Chrome está instalado..."
if command -v google-chrome-stable &> /dev/null; then
    CHROME_PATH=$(which google-chrome-stable)
    echo -e "${GREEN}✅ Chrome encontrado: $CHROME_PATH${NC}"
    CHROME_VERSION=$(google-chrome-stable --version 2>/dev/null)
    echo "   Versão: $CHROME_VERSION"
else
    echo -e "${RED}❌ Chrome não encontrado!${NC}"
    echo "   Execute: sudo apt install google-chrome-stable -y"
    exit 1
fi
echo ""

# 2. Verificar permissões
echo "2️⃣  Verificando permissões do Chrome..."
if [ -x "$CHROME_PATH" ]; then
    echo -e "${GREEN}✅ Chrome é executável${NC}"
else
    echo -e "${YELLOW}⚠️  Chrome não é executável, tentando corrigir...${NC}"
    sudo chmod +x "$CHROME_PATH"
    if [ -x "$CHROME_PATH" ]; then
        echo -e "${GREEN}✅ Permissões corrigidas${NC}"
    else
        echo -e "${RED}❌ Não foi possível corrigir permissões${NC}"
    fi
fi
echo ""

# 3. Testar execução básica do Chrome
echo "3️⃣  Testando execução básica do Chrome (--version)..."
if google-chrome-stable --version &>/dev/null; then
    VERSION_OUTPUT=$(google-chrome-stable --version 2>&1)
    echo -e "${GREEN}✅ Chrome executou com sucesso${NC}"
    echo "   Output: $VERSION_OUTPUT"
else
    echo -e "${RED}❌ Chrome não conseguiu executar${NC}"
    exit 1
fi
echo ""

# 4. Testar Chrome em modo headless
echo "4️⃣  Testando Chrome em modo headless..."
if google-chrome-stable --headless --disable-gpu --no-sandbox --version &>/dev/null; then
    HEADLESS_OUTPUT=$(google-chrome-stable --headless --disable-gpu --no-sandbox --version 2>&1)
    echo -e "${GREEN}✅ Chrome headless funcionou${NC}"
    echo "   Output: $HEADLESS_OUTPUT"
else
    echo -e "${RED}❌ Chrome headless falhou${NC}"
    echo "   Verifique dependências do sistema"
fi
echo ""

# 5. Verificar dependências do sistema
echo "5️⃣  Verificando dependências do sistema..."
MISSING_DEPS=()
DEPS_TO_CHECK=(
    "libnss3"
    "libatk-bridge2.0-0"
    "libdrm2"
    "libxkbcommon0"
    "libxcomposite1"
    "libxdamage1"
    "libxfixes3"
    "libxrandr2"
    "libgbm1"
    "libasound2"
    "libxshmfence1"
    "libxss1"
    "libgconf-2-4"
    "libpangocairo-1.0-0"
    "libatk1.0-0"
    "libcairo-gobject2"
    "libgtk-3-0"
    "libgdk-pixbuf2.0-0"
    "xvfb"
)

for dep in "${DEPS_TO_CHECK[@]}"; do
    if ! dpkg -l | grep -q "^ii.*$dep "; then
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ Todas as dependências estão instaladas${NC}"
else
    echo -e "${YELLOW}⚠️  Dependências faltando:${NC}"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "   - $dep"
    done
    echo ""
    echo "   Instale com:"
    echo "   sudo apt install -y ${MISSING_DEPS[*]}"
fi
echo ""

# 6. Verificar Python e dependências
echo "6️⃣  Verificando Python e dependências..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python encontrado: $PYTHON_VERSION${NC}"
    
    # Verificar se está em venv
    if [ -n "$VIRTUAL_ENV" ]; then
        echo -e "${GREEN}✅ Ambiente virtual ativado: $VIRTUAL_ENV${NC}"
    else
        echo -e "${YELLOW}⚠️  Ambiente virtual não está ativado${NC}"
        echo "   Execute: source venv/bin/activate"
    fi
    
    # Verificar undetected-chromedriver
    if python3 -c "import undetected_chromedriver" &>/dev/null; then
        echo -e "${GREEN}✅ undetected-chromedriver está instalado${NC}"
    else
        echo -e "${YELLOW}⚠️  undetected-chromedriver não está instalado${NC}"
        echo "   Execute: pip install undetected-chromedriver"
    fi
else
    echo -e "${RED}❌ Python não encontrado${NC}"
fi
echo ""

# 7. Verificar ChromeDriver
echo "7️⃣  Verificando ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    CHROMEDRIVER_PATH=$(which chromedriver)
    echo -e "${GREEN}✅ ChromeDriver encontrado: $CHROMEDRIVER_PATH${NC}"
    CHROMEDRIVER_VERSION=$(chromedriver --version 2>&1 | head -1)
    echo "   Versão: $CHROMEDRIVER_VERSION"
else
    echo -e "${YELLOW}⚠️  ChromeDriver não encontrado no PATH${NC}"
    echo "   O webdriver-manager baixará automaticamente"
fi
echo ""

# 8. Testar execução do script Python
echo "8️⃣  Testando execução básica do script..."
if [ -f "main.py" ]; then
    echo "   Arquivo main.py encontrado"
    if python3 -c "import sys; sys.path.insert(0, '.'); from src.core.bot import BlazeBot" &>/dev/null; then
        echo -e "${GREEN}✅ Módulos Python podem ser importados${NC}"
    else
        echo -e "${YELLOW}⚠️  Erro ao importar módulos${NC}"
        echo "   Verifique se todas as dependências estão instaladas"
    fi
else
    echo -e "${YELLOW}⚠️  Arquivo main.py não encontrado${NC}"
    echo "   Execute este script no diretório do projeto"
fi
echo ""

# 9. Verificar variáveis de ambiente
echo "9️⃣  Verificando variáveis de ambiente..."
if [ -n "$DISPLAY" ]; then
    echo -e "${GREEN}✅ DISPLAY está definido: $DISPLAY${NC}"
else
    echo -e "${YELLOW}⚠️  DISPLAY não está definido${NC}"
    echo "   Configure: export DISPLAY=:99"
fi

if [ -n "$CHROME_BIN" ]; then
    echo -e "${GREEN}✅ CHROME_BIN está definido: $CHROME_BIN${NC}"
else
    echo -e "${YELLOW}⚠️  CHROME_BIN não está definido${NC}"
fi
echo ""

# 10. Resumo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 RESUMO DO TESTE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ${#MISSING_DEPS[@]} -eq 0 ] && \
   [ -x "$CHROME_PATH" ] && \
   google-chrome-stable --headless --disable-gpu --no-sandbox --version &>/dev/null; then
    echo -e "${GREEN}✅ Sistema parece estar configurado corretamente!${NC}"
    echo ""
    echo "Próximos passos:"
    echo "1. Atualize o código: git pull origin main"
    echo "2. Reinicie o PM2: pm2 restart blaze-double-analyzer --update-env"
    echo "3. Verifique logs: pm2 logs blaze-double-analyzer"
else
    echo -e "${YELLOW}⚠️  Alguns problemas foram encontrados${NC}"
    echo ""
    echo "Corrija os problemas acima e execute este script novamente"
fi

echo ""

