# BlueOffice Breach - Challenge 7: Dev Panel SQL Injection (port 8000)
# Isolated, non-root Flask + SQLite service. The SQLite database lives
# entirely inside THIS container - no host mounts.

FROM python:3.11-slim

LABEL challenge="blueoffice-devpanel8000-sqli"

RUN groupadd -r devpanel && useradd -r -g devpanel -m -d /home/devpanel -s /usr/sbin/nologin devpanel

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py
COPY templates/ /app/templates/

RUN mkdir -p /app/data && chown -R devpanel:devpanel /app

USER devpanel

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/login', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "30", "app:app"]
