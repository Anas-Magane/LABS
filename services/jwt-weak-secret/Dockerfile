# BlueOffice Breach - Challenge: Weak JWT HS256 Admin Bypass (port 1000)
# Isolated, non-root Flask service. Token store is in-memory only.

FROM python:3.11-slim

LABEL challenge="blueoffice-jwt-weak-secret"

RUN groupadd -r jwtapp && useradd -r -g jwtapp -m -d /home/jwtapp -s /usr/sbin/nologin jwtapp

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py
COPY templates/ /app/templates/

RUN chown -R jwtapp:jwtapp /app

USER jwtapp

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "2", "--timeout", "30", "app:app"]
