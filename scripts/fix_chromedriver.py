"""
Script auxiliar para verificar e corrigir problemas com ChromeDriver
"""
import os
import sys
from pathlib import Path

def check_chrome_installed():
    """Verifica se o Chrome está instalado"""
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"[OK] Chrome encontrado em: {path}")
            return True
    
    print("[ERRO] Chrome nao encontrado nos caminhos padrao")
    return False

def check_chromedriver():
    """Verifica e limpa o cache do ChromeDriver"""
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.os_manager import ChromeType
        
        print("Verificando ChromeDriver...")
        
        # Limpa o cache
        cache_path = Path.home() / ".wdm"
        if cache_path.exists():
            print(f"Cache encontrado em: {cache_path}")
            print("Para limpar o cache, delete a pasta .wdm")
        
        # Tenta baixar o driver
        print("Tentando baixar ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"[OK] ChromeDriver instalado em: {driver_path}")
        
        # Verifica se o arquivo existe e não está corrompido
        if os.path.exists(driver_path):
            file_size = os.path.getsize(driver_path)
            print(f"Tamanho do arquivo: {file_size} bytes")
            if file_size < 1000:  # Arquivo muito pequeno provavelmente está corrompido
                print("[AVISO] Arquivo parece estar corrompido (muito pequeno)")
                return False
            return True
        else:
            print("[ERRO] Arquivo do ChromeDriver nao encontrado")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao verificar ChromeDriver: {e}")
        return False

def main():
    print("=" * 60)
    print("VERIFICAÇÃO DO CHROMEDRIVER")
    print("=" * 60)
    print()
    
    # Verifica Chrome
    chrome_ok = check_chrome_installed()
    print()
    
    # Verifica ChromeDriver
    driver_ok = check_chromedriver()
    print()
    
    if chrome_ok and driver_ok:
        print("=" * 60)
        print("[OK] Tudo parece estar OK!")
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("[AVISO] PROBLEMAS DETECTADOS")
        print("=" * 60)
        print()
        print("Soluções:")
        print("1. Certifique-se de que o Google Chrome está instalado")
        print("2. Execute: pip install --upgrade webdriver-manager")
        print("3. Delete a pasta .wdm em seu diretório home e tente novamente")
        print("4. Baixe manualmente o ChromeDriver de:")
        print("   https://chromedriver.chromium.org/downloads")
        return 1

if __name__ == "__main__":
    sys.exit(main())

