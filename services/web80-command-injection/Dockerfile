# BlueOffice Breach - Challenge 2: Web Command Injection (port 80)
# Isolated, non-root Flask service. Command injection via /flag?cmd=
# only ever touches files inside THIS container.

FROM python:3.11-slim

LABEL challenge="blueoffice-web80-cmdi"

# A small, harmless toolbox of file-reading utilities players can pivot
# to once they discover "cat" is blacklisted. coreutils/util-linux
# (tac, head, tail, od, sort, more) already ship in the base image;
# "less" and "binutils strings" are added explicitly.
RUN apt-get update && \
    apt-get install -y --no-install-recommends less binutils && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r webapp && useradd -r -g webapp -m -d /home/webapp -s /usr/sbin/nologin webapp

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py
COPY files/ /app/files/

RUN chown -R webapp:webapp /app && chmod 644 /app/files/*.txt

USER webapp

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "app:app"]
