module.exports = {
  apps: [{
    name: 'wa-bot',
    script: 'index.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    // Auto restart on crash
    min_uptime: '10s',
    max_restarts: 10,
    restart_delay: 5000,
    // Kill timeout
    kill_timeout: 5000,
    // Cron restart (optional: restart setiap 6 jam untuk refresh session)
    cron_restart: '0 */6 * * *'
  }]
};
