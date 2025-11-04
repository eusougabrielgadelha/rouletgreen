#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] Iniciando setup para Ubuntu (Playwright + Chromium)"

# Diretório do projeto = pasta onde está este script
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "[INFO] Verificando Python e pip..."
command -v python3 >/dev/null 2>&1 || { echo "[ERRO] python3 não encontrado"; exit 1; }
python3 -m pip --version >/dev/null 2>&1 || { echo "[ERRO] pip do Python não encontrado"; exit 1; }

echo "[INFO] Atualizando pip..."
python3 -m pip install --upgrade pip

echo "[INFO] Instalando dependências Python do projeto..."
python3 -m pip install -r requirements.txt

echo "[INFO] Instalando Playwright e dependências do Chromium..."
# install-deps: instala bibliotecas do SO necessárias ao Chromium (requer sudo em ambientes sem libs)
python3 -m pip install playwright
if command -v sudo >/dev/null 2>&1; then
  sudo python3 -m playwright install-deps chromium || true
else
  python3 -m playwright install-deps chromium || true
fi

echo "[INFO] Baixando navegador Chromium do Playwright..."
python3 -m playwright install chromium

echo "[SUCCESS] Setup concluído. Para executar:"
echo "         python main.py"


