# BlueOffice Breach - Challenge: IDOR User Records (port 2000)
# Isolated, non-root Flask service. No auth anywhere by design.

FROM python:3.11-slim

LABEL challenge="blueoffice-idor-clock"

RUN groupadd -r idorclock && useradd -r -g idorclock -m -d /home/idorclock -s /usr/sbin/nologin idorclock

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py
COPY templates/ /app/templates/

RUN chown -R idorclock:idorclock /app

USER idorclock

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "app:app"]
