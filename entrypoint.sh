#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Generating missing SSH host keys..."
if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
  ssh-keygen -A
fi

echo "[entrypoint] Starting cron and ssh services..."
service cron start
service ssh start

echo "[entrypoint] Launching Flask application..."
cd /app
exec python -u app.py
