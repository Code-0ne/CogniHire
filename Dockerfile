FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        procps \
        python3-tk \
        xvfb \
        x11vnc \
        websockify \
        fluxbox \
        wget \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir --upgrade pip uv

# Copy dependency files first
COPY pyproject.toml uv.lock README.md ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy project
COPY . .

# Download noVNC
RUN wget -qO- https://github.com/novnc/noVNC/archive/refs/tags/v1.4.0.tar.gz \
    | tar xz && \
    mv noVNC-1.4.0 /opt/novnc

# Create startup script (LF line endings guaranteed)
RUN printf '%s\n' \
'#!/bin/sh' \
'set -e' \
'' \
'export DISPLAY=:0' \
'' \
'echo "Starting Xvfb..."' \
'Xvfb :0 -screen 0 1920x1080x24 &' \
'sleep 2' \
'' \
'echo "Starting Window Manager..."' \
'fluxbox & ' \
'sleep 2' \
'' \
'echo "Starting x11vnc..."' \
'x11vnc -display :0 -forever -shared -nopw -listen localhost -rfbport 5900 &' \
'' \
'echo "Starting noVNC..."' \
'/opt/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 &' \
'' \
'sleep 2' \
'' \
'echo "DISPLAY=$DISPLAY"' \
'env | grep DISPLAY' \
'' \
'echo "Starting CogniHire..."' \
'exec uv run python app_final.py' \
> /usr/local/bin/start.sh && \
chmod +x /usr/local/bin/start.sh

EXPOSE 6080

CMD ["/usr/local/bin/start.sh"]