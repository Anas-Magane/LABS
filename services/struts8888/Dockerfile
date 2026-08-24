# BlueOffice Breach - Challenge 6: Apache Struts2 CVE-2017-5638 (port 8888)
# Isolated, non-root service. RCE triggered via the Content-Type header
# exploit only ever runs inside THIS container.

FROM python:3.11-slim

LABEL challenge="blueoffice-struts8888"

RUN groupadd -r struts && useradd -r -g struts -m -d /home/struts -s /bin/bash struts

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py

# Flag readable by whatever low-privileged user ends up running shell
# commands through the exploit (mirrors how real-world CVE boxes leave
# world-readable flags reachable from any uid).
COPY flag2.txt /flag2.txt
RUN chmod 444 /flag2.txt

RUN chown -R struts:struts /app

USER struts

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "30", "app:app"]
