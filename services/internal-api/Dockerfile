# BlueOffice Breach - Challenge 9 (internal): HR Analytics internal API + dashboard
# NOT published to the host. Only reachable inside the `pivotnet` network at
# the static address 172.30.80.50 (ports 5000 and 3000).

FROM python:3.11-slim

LABEL challenge="blueoffice-internal-api"

RUN groupadd -r hrapi && useradd -r -g hrapi -m -d /home/hrapi -s /bin/bash hrapi

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py dashboard.py entrypoint.sh /app/
COPY files/ /app/files/
COPY flag8.txt /app/flag8.txt

RUN chmod 444 /app/flag8.txt /app/files/readme.txt && \
    chmod 755 /app/entrypoint.sh && \
    chown -R hrapi:hrapi /app

USER hrapi

EXPOSE 5000 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api', timeout=3)" || exit 1

CMD ["/app/entrypoint.sh"]
