#!/bin/bash

# Script para corrigir problemas com ChromeDriver no Linux
# Uso: ./fix_chromedriver_linux.sh

echo "🔧 Corrigindo problemas com ChromeDriver..."

# Limpar cache do webdriver-manager
echo "🗑️  Limpando cache do webdriver-manager..."
rm -rf ~/.wdm 2>/dev/null
rm -rf ~/.cache/selenium 2>/dev/null

# Verificar se Chrome/Chromium está instalado
echo "🔍 Verificando Chrome/Chromium..."
if command -v google-chrome-stable &> /dev/null; then
    CHROME_PATH=$(which google-chrome-stable)
    echo "✅ Chrome encontrado: $CHROME_PATH"
elif command -v chromium-browser &> /dev/null; then
    CHROME_PATH=$(which chromium-browser)
    echo "✅ Chromium encontrado: $CHROME_PATH"
else
    echo "❌ Chrome/Chromium não encontrado!"
    echo "📦 Instalando Chromium..."
    sudo apt update
    sudo apt install chromium-browser chromium-chromedriver -y
    CHROME_PATH=$(which chromium-browser)
fi

# Verificar permissões do Chrome
if [ -f "$CHROME_PATH" ]; then
    echo "🔐 Verificando permissões do Chrome..."
    if [ ! -x "$CHROME_PATH" ]; then
        echo "⚠️  Chrome não é executável, corrigindo..."
        sudo chmod +x "$CHROME_PATH"
    fi
fi

# Instalar ChromeDriver manualmente se necessário
echo "📥 Verificando ChromeDriver..."
if ! command -v chromedriver &> /dev/null; then
    echo "📦 ChromeDriver não encontrado, instalando..."
    
    # Obter versão do Chrome
    CHROME_VERSION=$($CHROME_PATH --version | grep -oP '\d+\.\d+\.\d+\.\d+' | head -1)
    echo "🔍 Versão do Chrome: $CHROME_VERSION"
    
    # Baixar ChromeDriver compatível
    CHROMEDRIVER_VERSION=$(echo $CHROME_VERSION | cut -d. -f1)
    echo "📥 Baixando ChromeDriver versão $CHROMEDRIVER_VERSION..."
    
    wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROMEDRIVER_VERSION" -O /tmp/chromedriver_version.txt 2>/dev/null || \
    wget -q "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROMEDRIVER_VERSION" -O /tmp/chromedriver_version.txt 2>/dev/null
    
    if [ -f /tmp/chromedriver_version.txt ]; then
        DRIVER_VERSION=$(cat /tmp/chromedriver_version.txt)
        echo "📦 Versão do ChromeDriver: $DRIVER_VERSION"
        
        # Baixar ChromeDriver
        wget -q "https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip" -O /tmp/chromedriver.zip 2>/dev/null || \
        wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$DRIVER_VERSION/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip 2>/dev/null
        
        if [ -f /tmp/chromedriver.zip ]; then
            unzip -q /tmp/chromedriver.zip -d /tmp/
            sudo mv /tmp/chromedriver*/chromedriver /usr/local/bin/chromedriver
            sudo chmod +x /usr/local/bin/chromedriver
            echo "✅ ChromeDriver instalado em /usr/local/bin/chromedriver"
        fi
    fi
fi

# Verificar ChromeDriver
if command -v chromedriver &> /dev/null; then
    CHROMEDRIVER_PATH=$(which chromedriver)
    echo "✅ ChromeDriver encontrado: $CHROMEDRIVER_PATH"
    chromedriver --version
else
    echo "⚠️  ChromeDriver não encontrado no PATH"
    echo "💡 Tente instalar: sudo apt install chromium-chromedriver -y"
fi

# Limpar arquivos temporários
rm -f /tmp/chromedriver.zip /tmp/chromedriver_version.txt 2>/dev/null
rm -rf /tmp/chromedriver* 2>/dev/null

echo ""
echo "✅ Correção concluída!"
echo "💡 Se ainda houver problemas, execute:"
echo "   - sudo apt install chromium-browser chromium-chromedriver -y"
echo "   - pip install --upgrade webdriver-manager"

