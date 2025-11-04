module.exports = {
  apps: [{
    name: 'blaze-double-analyzer',
    script: 'main.py',
    interpreter: 'venv/bin/python3',
    cwd: '/home/rouletgreen',  // AJUSTE ESTE CAMINHO CONFORME SEU SERVIDOR
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      PYTHONUNBUFFERED: '1',
      DISPLAY: ':99'  // Para Chrome headless
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    time: true
  }]
};

