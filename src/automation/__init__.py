"""
Módulo de automação web
"""
import os

# Verifica se deve usar Playwright (recomendado) ou Selenium
USE_PLAYWRIGHT = os.getenv('USE_PLAYWRIGHT', 'true').lower() == 'true'

if USE_PLAYWRIGHT:
    try:
        from .playwright_automation import BlazeAutomation
        print("[INFO] Usando Playwright para automação (recomendado)")
    except ImportError:
        print("[AVISO] Playwright não disponível, usando Selenium")
        from .web_automation import BlazeAutomation
else:
    from .web_automation import BlazeAutomation
    print("[INFO] Usando Selenium para automação")

__all__ = ['BlazeAutomation']

