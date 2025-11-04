"""
Script principal do Blaze Double Analyzer
Ponto de entrada da aplicação
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configura encoding UTF-8 para Windows
from src.utils.encoding import setup_encoding
setup_encoding()

# Importa a classe principal do bot
from src.core import BlazeBot


def main():
    """Função principal"""
    bot = BlazeBot()
    try:
        bot.run()
    except Exception as e:
        print(f"Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
