#!/bin/bash

echo "🧹 Limpando processos Chrome e ChromeDriver..."

# Mata todos os processos Chrome
pkill -9 chrome 2>/dev/null || true
pkill -9 chromium 2>/dev/null || true
pkill -9 chromedriver 2>/dev/null || true

# Remove diretórios temporários do Chrome
rm -rf /tmp/chrome-user-data 2>/dev/null || true
rm -rf /tmp/chrome-data 2>/dev/null || true
rm -rf /tmp/chrome-cache 2>/dev/null || true
rm -rf /tmp/.com.google.Chrome* 2>/dev/null || true

# Remove lock files
rm -f /tmp/.X99-lock 2>/dev/null || true
rm -f /tmp/.chrome-* 2>/dev/null || true

echo "✅ Limpeza concluída!"
echo ""
echo "Verificando se ainda há processos:"
ps aux | grep -E "chrome|chromedriver" | grep -v grep || echo "Nenhum processo encontrado"

