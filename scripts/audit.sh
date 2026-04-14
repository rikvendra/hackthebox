#!/usr/bin/env bash
set -euo pipefail

echo "[audit.sh] Started at $(date -u)" >> /var/log/internal-audit.log
echo "[audit.sh] Health-check for rajptRishi internal network" >> /var/log/internal-audit.log
touch /tmp/.audit-ok
