#!/bin/bash

# Script de atualização rápida do projeto no servidor
# Uso: ./update.sh

echo "🔄 Atualizando Blaze Double Analyzer..."

# AJUSTE ESTE CAMINHO CONFORME SEU SERVIDOR
PROJECT_DIR="/home/rouletgreen"

# Verificar se o diretório existe
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Erro: Diretório $PROJECT_DIR não encontrado!"
    echo "Por favor, ajuste o caminho PROJECT_DIR no script."
    exit 1
fi

# Navegar para o diretório do projeto
cd "$PROJECT_DIR" || exit 1

echo "📁 Diretório: $(pwd)"

# Ativar ambiente virtual
echo "🐍 Ativando ambiente virtual..."
source venv/bin/activate

# Parar aplicação
echo "⏸️  Parando aplicação..."
pm2 stop blaze-double-analyzer || echo "Aplicação não estava rodando"

# Atualizar código
echo "📥 Atualizando código do GitHub..."
git pull origin main

# Atualizar dependências
echo "📦 Atualizando dependências Python..."
pip install -r requirements.txt --quiet

# Reiniciar aplicação
echo "🚀 Reiniciando aplicação..."
pm2 restart blaze-double-analyzer

# Aguardar um pouco
sleep 2

# Mostrar status
echo "📊 Status da aplicação:"
pm2 status

# Mostrar últimas linhas dos logs
echo ""
echo "📋 Últimas 30 linhas dos logs:"
pm2 logs blaze-double-analyzer --lines 30 --nostream

echo ""
echo "✅ Atualização concluída!"
echo "💡 Use 'pm2 logs blaze-double-analyzer' para ver logs em tempo real"

