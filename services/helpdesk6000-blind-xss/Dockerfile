# BlueOffice Breach - Challenge: IT Helpdesk Blind Stored XSS (port 6000)
# Isolated, non-root Flask service. Ticket store and collector logs are
# in-memory only. Ships a headless Chromium + chromedriver so the
# in-process admin bot (bot.py) can really log in and open tickets,
# exactly like a human admin - this is what makes the XSS genuinely
# exploitable rather than self-XSS.

FROM python:3.11-slim

LABEL challenge="blueoffice-helpdesk6000"

RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r helpdesk && useradd -r -g helpdesk -m -d /home/helpdesk -s /usr/sbin/nologin helpdesk

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py
COPY bot.py /app/bot.py
COPY templates/ /app/templates/

RUN chown -R helpdesk:helpdesk /app /home/helpdesk

USER helpdesk

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/', timeout=3)" || exit 1

# Single worker with multiple threads: the admin bot thread and the
# ticket/collector in-memory stores must live in the same process.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "60", "app:app"]
