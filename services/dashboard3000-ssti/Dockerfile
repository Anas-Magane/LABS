# BlueOffice Breach - Challenge 3: Client-Side Auth + SSTI (port 3000)
# Isolated, non-root Flask service. SSTI/RCE here is confined to THIS
# container's filesystem and process namespace only.

FROM python:3.11-slim

LABEL challenge="blueoffice-dashboard3000-ssti"

RUN groupadd -r sstiuser && useradd -r -g sstiuser -m -d /home/sstiuser -s /bin/bash sstiuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py
COPY templates/ /app/templates/

# Credential file the player is meant to find via SSTI RCE
RUN mkdir -p /opt
COPY opt/creds.txt /opt/creds.txt

RUN chown -R sstiuser:sstiuser /app && \
    chown sstiuser:sstiuser /opt/creds.txt && \
    chmod 440 /opt/creds.txt

USER sstiuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "app:app"]
