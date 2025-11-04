"""
Configuração de encoding UTF-8 para Windows
"""
import sys
import os


def setup_encoding():
    """Configura encoding UTF-8 para Windows"""
    if sys.platform == 'win32':
        try:
            import codecs
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            if hasattr(sys.stderr, 'buffer'):
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
            os.environ['PYTHONIOENCODING'] = 'utf-8'
        except:
            pass

