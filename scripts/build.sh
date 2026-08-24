#!/usr/bin/env bash
# BlueOffice Breach - build all challenge images without starting them.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [ ! -f .env ]; then
    echo "[*] No .env found, copying .env.example -> .env"
    echo "[*] Edit .env and set PUBLIC_IP to your Oracle Cloud VM's public IP."
    cp .env.example .env
fi

echo "[*] Building all BlueOffice Breach challenge images..."
docker compose build

echo "[*] Build complete. Run scripts/start.sh to launch the machine."
