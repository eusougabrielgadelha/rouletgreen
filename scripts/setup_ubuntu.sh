#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] Iniciando setup para Ubuntu (Playwright + Chromium)"

# Diretório do projeto = pasta onde está este script
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "[INFO] Verificando Python e pip..."
command -v python3 >/dev/null 2>&1 || { echo "[ERRO] python3 não encontrado. Instale com: sudo apt -y install python3"; exit 1; }

echo "[INFO] Instalando módulo venv (se necessário)..."
if ! dpkg -s python3-venv >/dev/null 2>&1; then
  if command -v sudo >/dev/null 2>&1; then
    sudo apt -y install python3-venv
  else
    echo "[AVISO] sudo não disponível. Instale python3-venv manualmente: apt -y install python3-venv"
  fi
fi

VENV_DIR="$PROJECT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "[INFO] Criando ambiente virtual em .venv"
  python3 -m venv "$VENV_DIR"
fi

PY="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

echo "[INFO] Atualizando pip dentro do venv..."
"$PY" -m pip install --upgrade pip

echo "[INFO] Instalando dependências Python do projeto no venv..."
"$PIP" install -r requirements.txt

echo "[INFO] Instalando Playwright no venv..."
"$PIP" install playwright

echo "[INFO] Instalando dependências do sistema para Chromium (install-deps)..."
if command -v sudo >/dev/null 2>&1; then
  sudo "$PY" -m playwright install-deps chromium || true
else
  "$PY" -m playwright install-deps chromium || true
fi

echo "[INFO] Baixando navegador Chromium do Playwright (no venv)..."
"$PY" -m playwright install chromium

echo "[SUCCESS] Setup concluído. Para executar:"
echo "         source .venv/bin/activate && python main.py"


