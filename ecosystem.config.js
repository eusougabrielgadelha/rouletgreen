module.exports = {
  apps: [{
    name: 'blaze-double-analyzer',
    script: 'main.py',
    interpreter: '/home/rouletgreen/venv/bin/python3',  // CAMINHO ABSOLUTO - AJUSTE CONFORME SEU SERVIDOR
    cwd: '/home/rouletgreen',  // AJUSTE ESTE CAMINHO CONFORME SEU SERVIDOR
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
            env: {
              PYTHONUNBUFFERED: '1',
              DISPLAY: ':99',  // Para Chrome headless
              PATH: '/home/rouletgreen/venv/bin:/usr/local/bin:/usr/bin:/bin',  // Adiciona venv ao PATH
              // Variáveis para Chrome em servidor headless
              CHROME_BIN: '/usr/bin/google-chrome-stable',
              CHROME_PATH: '/usr/bin/google-chrome-stable',
              // Evita problemas de permissões
              HOME: '/root',
              // Para Xvfb (se necessário)
              XAUTHORITY: '/tmp/.X99-authority'
            },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    time: true
  }]
};

