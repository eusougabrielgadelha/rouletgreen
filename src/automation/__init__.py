"""
Módulo de automação web
"""
import os

# Verifica se deve usar Playwright (recomendado) ou Selenium
USE_PLAYWRIGHT = os.getenv('USE_PLAYWRIGHT', 'true').lower() == 'true'

# Se houver loop asyncio ativo (ex.: rodando sob um orchestrator), evita Playwright sync API
if USE_PLAYWRIGHT:
	try:
		import asyncio
		try:
			loop = asyncio.get_running_loop()
			if loop.is_running():
				print("[AVISO] Loop asyncio ativo detectado no import - usando Selenium em vez de Playwright")
				USE_PLAYWRIGHT = False
		except RuntimeError:
			# Sem loop em execução, ok
			pass
	except Exception:
		pass

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

