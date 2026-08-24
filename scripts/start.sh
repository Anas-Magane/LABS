#!/usr/bin/env bash
# BlueOffice Breach - build (if needed) and start the full machine.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [ ! -f .env ]; then
    echo "[*] No .env found, copying .env.example -> .env"
    echo "[*] Edit .env and set PUBLIC_IP to your Oracle Cloud VM's public IP."
    cp .env.example .env
fi

echo "[*] Starting BlueOffice Breach (docker compose up -d --build)..."
docker compose up -d --build

echo
echo "[*] Status:"
docker compose ps

cat <<'EOF'

[*] BlueOffice Breach is up. Exposed challenge ports:
      21/tcp    - FTP
      80/tcp    - Web command injection
      445/tcp   - SMB
      2222/tcp  - SSH + privilege escalation
      3000/tcp  - Client-side auth + SSTI dashboard
      7777/tcp  - BlueOffice HR Recruitment Portal (JBoss RCE + pivot)
      8000/tcp  - Dev Panel SQL Injection
      8888/tcp  - Apache Struts2 CVE-2017-5638
      9999/tcp  - LFI
      1000/tcp  - Weak JWT HS256 admin bypass
      2000/tcp  - IDOR user records
      9000/tcp  - Next.js middleware auth bypass (CVE-2025-29927)
      9005/tcp  - FST School Portal (access control bypass + SQLi)
      4000/tcp  - Cloud metadata SSRF
      4500/tcp  - File upload extension bypass RCE

Make sure your Oracle Cloud Security List / Network Security Group
and the host firewall (iptables/ufw/firewalld) allow exactly these
ports inbound. See SECURITY.md before exposing this publicly.
EOF
