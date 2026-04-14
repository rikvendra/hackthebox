FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    APP_PORT=80

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openssh-server \
        cron \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash developer \
    && echo \"developer:DevPass123!\" | chpasswd

RUN mkdir -p /app /opt/internal /var/run/sshd
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py templates/ entrypoint.sh /app/
COPY scripts/audit.sh /opt/internal/audit.sh
COPY scripts/cron/internal-audit.cron /etc/cron.d/internal-audit

COPY user.txt /home/developer/user.txt
COPY root.txt /root/root.txt

RUN chmod 0644 /etc/cron.d/internal-audit \
    && chmod +x /opt/internal/audit.sh \
    && chown root:developer /opt/internal/audit.sh \
    && chmod 0760 /opt/internal/audit.sh \
    && chmod +x /app/entrypoint.sh \
    && chown -R developer:developer /home/developer

EXPOSE 80 22

ENTRYPOINT [\"/app/entrypoint.sh\"]
