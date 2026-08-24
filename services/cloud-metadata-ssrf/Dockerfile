# BlueOffice Breach - Challenge: Cloud Metadata SSRF (port 4000)
# Isolated, non-root Flask service. The "cloud metadata" endpoint is
# simulated inside this same container and only answers requests that
# originate from 127.0.0.1 (i.e. only reachable through the app's own
# SSRF-vulnerable URL fetcher, never directly from outside).

FROM python:3.11-slim

LABEL challenge="blueoffice-cloud-metadata-ssrf"

RUN groupadd -r ssrfapp && useradd -r -g ssrfapp -m -d /home/ssrfapp -s /usr/sbin/nologin ssrfapp

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py
COPY templates/ /app/templates/

RUN chown -R ssrfapp:ssrfapp /app

USER ssrfapp

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "app:app"]
