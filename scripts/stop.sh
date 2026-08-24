#!/usr/bin/env bash
# BlueOffice Breach - stop the machine. Pass --reset to also wipe all
# containers, volumes and rebuild from a clean state next time.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [[ "${1:-}" == "--reset" ]]; then
    echo "[*] Stopping and removing all BlueOffice Breach containers, networks and images..."
    docker compose down --volumes --rmi local
else
    echo "[*] Stopping BlueOffice Breach containers..."
    docker compose down
fi

echo "[*] Done."
