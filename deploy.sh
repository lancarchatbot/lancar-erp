#!/bin/bash
# Script deploy otomatis — jalankan sekali di server VPS
# Dibuat untuk: Lancar ERP v2.0

set -e
echo "======================================"
echo "  DEPLOY LANCAR ERP v2.0"
echo "======================================"

# 1. Ambil update terbaru dari GitHub
echo ""
echo "[1/4] Mengambil update terbaru dari GitHub..."
git pull origin main

# 2. Build ulang jika ada perubahan
echo ""
echo "[2/4] Build aplikasi..."
docker compose build --no-cache

# 3. Jalankan semua service
echo ""
echo "[3/4] Menjalankan database + backend + web..."
docker compose up -d

# 4. Cek status
echo ""
echo "[4/4] Mengecek status..."
sleep 5
docker compose ps

echo ""
echo "======================================"
echo "  SELESAI! Aplikasi sudah online."
echo "  Buka: http://$(curl -s ifconfig.me)"
echo "======================================"
