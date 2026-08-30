# BlueOffice Breach - Challenge: Employee Kudos Wall Blind Stored XSS (port 5050)
# Isolated, non-root Flask service. Kudos queue/wall and collector logs
# are in-memory only. Ships a headless Chromium + chromedriver so the
# in-process HR manager bot (bot.py) can really log in and review the
# moderation queue, exactly like a human manager - this is what makes
# the XSS genuinely exploitable rather than self-XSS.

FROM python:3.11-slim

LABEL challenge="blueoffice-kudoswall5050"

RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r kudoswall && useradd -r -g kudoswall -m -d /home/kudoswall -s /usr/sbin/nologin kudoswall

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py
COPY bot.py /app/bot.py
COPY templates/ /app/templates/

RUN chown -R kudoswall:kudoswall /app /home/kudoswall

USER kudoswall

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/', timeout=3)" || exit 1

# Single worker with multiple threads: the manager bot thread and the
# in-memory queue/wall/collector stores must live in the same process.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "60", "app:app"]
