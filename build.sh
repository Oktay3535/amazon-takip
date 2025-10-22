#!/usr/bin/env bash
# Render ortamı için Playwright kurulumu

# Paket yöneticisini sadece gerekli kütüphaneler için çalıştır
apt-get update -yq || true
apt-get install -yq --no-install-recommends \
    wget \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    xdg-utils || true

# Python bağımlılıklarını yükle
pip install --upgrade pip
pip install -r requirements.txt

# Playwright kurulumu
python -m playwright install --with-deps chromium
