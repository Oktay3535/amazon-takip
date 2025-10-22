#!/bin/bash
# Playwright browser kurulumu Render'da root erişimi gerektirir, o yüzden atlıyoruz
echo "Skipping Playwright browsers install (Render environment has no root access)"

# Ortam değişkeniyle tarayıcı kurulumunu atla
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Gerekirse virtualenv aktif et
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Gereken paketleri kur
pip install -r requirements.txt

# Flask veya başka bir servis başlat
gunicorn app:app
