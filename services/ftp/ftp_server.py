#!/usr/bin/env python3
"""
BlueOffice Breach - Challenge 1: FTP (port 21)

Self-contained FTP server (built on pyftpdlib) that:
  - Advertises the classic "220 (vsFTPd 2.3.4)" banner.
  - Allows anonymous login into /srv/ftp/anonymous (read-only).
  - Reproduces the externally-observable behaviour of the historical
    vsFTPd 2.3.4 "smiley face" backdoor (CVE-2011-2523): if a USER
    command contains the trigger string ":)", a bind shell listener is
    opened on TCP/6200 *inside this container only*.

This does not run the real backdoored vsftpd binary/source - it is an
intentional, sandboxed re-implementation of the trigger -> bind-shell
behaviour, built so the challenge is solved the same way the real CVE
is solved (smiley-face username, then connect to port 6200), while
guaranteeing the resulting shell can never leave this container.
"""

import os
import socket
import subprocess
import threading

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# NOTE: vsFTPd traditionally listens on TCP/21, but binding to a port
# below 1024 requires root. To keep this service running as a non-root
# user, the server listens internally on FTP_PORT (default 2121) and
# docker-compose publishes it externally as host port 21.
FTP_PORT = int(os.environ.get("FTP_PORT", "2121"))
BACKDOOR_PORT = int(os.environ.get("BACKDOOR_PORT", "6200"))
ANON_ROOT = "/srv/ftp/anonymous"
TRIGGER = ":)"

_backdoor_lock = threading.Lock()
_backdoor_started = False


def _handle_backdoor_client(conn):
    """Spawn a restricted, non-root shell wired directly to the socket."""
    fd = conn.fileno()
    try:
        proc = subprocess.Popen(["/bin/sh", "-i"], stdin=fd, stdout=fd, stderr=fd)
        proc.wait()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except OSError:
            pass


def _backdoor_listener():
    """Listen on 6200 (this container's namespace only) and hand out shells."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", BACKDOOR_PORT))
    srv.listen(5)
    while True:
        conn, _addr = srv.accept()
        threading.Thread(target=_handle_backdoor_client, args=(conn,), daemon=True).start()


def trigger_backdoor_if_needed(username: str):
    global _backdoor_started
    if TRIGGER not in (username or ""):
        return
    with _backdoor_lock:
        if _backdoor_started:
            return
        _backdoor_started = True
        threading.Thread(target=_backdoor_listener, daemon=True).start()


class BackdoorAwareHandler(FTPHandler):
    def ftp_USER(self, line):
        trigger_backdoor_if_needed(line)
        return super().ftp_USER(line)


def main():
    authorizer = DummyAuthorizer()
    authorizer.add_anonymous(ANON_ROOT, perm="elr")

    handler = BackdoorAwareHandler
    handler.authorizer = authorizer
    # pyftpdlib prepends the "220 " response code itself, so banner
    # must NOT include it (otherwise the code is sent twice).
    handler.banner = "(vsFTPd 2.3.4)"

    # Passive mode setup so the data channel works through Docker's NAT.
    pasv_ports = os.environ.get("FTP_PASV_PORTS", "21100-21110")
    lo, hi = (int(x) for x in pasv_ports.split("-"))
    handler.passive_ports = range(lo, hi + 1)

    masquerade = os.environ.get("FTP_PASV_ADDRESS")
    if masquerade:
        handler.masquerade_address = masquerade

    server = FTPServer(("0.0.0.0", FTP_PORT), handler)
    server.max_cons = 64
    server.max_cons_per_ip = 16
    server.serve_forever()


if __name__ == "__main__":
    main()
