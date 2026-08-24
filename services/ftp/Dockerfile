# BlueOffice Breach - Challenge 1: FTP (vsFTPd 2.3.4 style backdoor)
# Isolated, non-root FTP service. Any shell obtained via the simulated
# backdoor is a process inside THIS container only.

FROM python:3.11-slim

LABEL challenge="blueoffice-ftp"

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# Non-root service account
RUN groupadd -r ftpsvc && useradd -r -g ftpsvc -m -d /home/ftpsvc -s /bin/sh ftpsvc

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ftp_server.py /app/ftp_server.py

# Anonymous FTP root (read-only content for players)
RUN mkdir -p /srv/ftp/anonymous
COPY anonymous/fake_flag.txt /srv/ftp/anonymous/fake_flag.txt

# Real flag, only reachable through the backdoor shell, never via FTP itself
COPY flag.txt /home/ftpsvc/flag.txt

RUN chown -R ftpsvc:ftpsvc /srv/ftp /home/ftpsvc /app && \
    chmod 444 /srv/ftp/anonymous/fake_flag.txt && \
    chmod 400 /home/ftpsvc/flag.txt

USER ftpsvc
WORKDIR /home/ftpsvc

EXPOSE 2121 6200 21100-21110

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import socket; s=socket.create_connection(('127.0.0.1',2121),3); s.close()" || exit 1

CMD ["python3", "/app/ftp_server.py"]
