#!/usr/bin/env python3
"""
BlueOffice Breach - Challenge 2: Web Command Injection (port 80)

A tiny internal "portal" with an intentionally vulnerable /flag endpoint.
The cmd parameter is passed straight into a shell (classic command
injection). The literal command "cat" is blacklisted, forcing players
to use an alternative file-reading technique (tac, head, less, more,
od, strings, python -c, etc.) to read flag1.txt.

Everything this app touches lives inside /app/files in THIS container.
There are no host bind-mounts, so command injection here can never
reach the Oracle Cloud host.
"""

import subprocess

from flask import Flask, request, Response

app = Flask(__name__)

FILES_DIR = "/app/files"
BLACKLIST = ["cat"]

INDEX_HTML = """<!doctype html>
<html>
<head><title>BlueOffice Internal Portal</title></head>
<body>
<h1>BlueOffice Internal Portal</h1>
<p>Welcome. This page is under maintenance.</p>
</body>
</html>
"""

APP_HTML = """<!doctype html>
<html>
<head><title>BlueOffice App</title></head>
<body>
<h1>BlueOffice App v1.0</h1>
<p>Internal tools status: OK</p>
</body>
</html>
"""

ADMIN_HTML = """<!doctype html>
<html>
<head><title>Admin</title></head>
<body>
<h1>403 Forbidden</h1>
<p>Admins only.</p>
</body>
</html>
"""

FLAG_PAGE_TEMPLATE = """<!doctype html>
<html>
<head><title>.</title></head>
<body>
{output}
</body>
</html>
"""


def is_blacklisted(cmd: str) -> bool:
    lowered = cmd.lower()
    return any(bad in lowered for bad in BLACKLIST)


@app.route("/")
def index():
    return Response(INDEX_HTML, mimetype="text/html")


@app.route("/app")
def app_page():
    return Response(APP_HTML, mimetype="text/html")


@app.route("/admin")
def admin_page():
    return Response(ADMIN_HTML, mimetype="text/html")


@app.route("/flag")
def flag_page():
    cmd = request.args.get("cmd", "")
    output_html = ""

    if cmd:
        if is_blacklisted(cmd):
            output_html = "<pre>blocked: 'cat' is blacklisted. Some commands may be blacklisted.</pre>"
        else:
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=FILES_DIR,
                    capture_output=True,
                    timeout=5,
                    text=True,
                )
                raw = (result.stdout or "") + (result.stderr or "")
                escaped = (
                    raw.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                output_html = f"<pre>{escaped}</pre>"
            except subprocess.TimeoutExpired:
                output_html = "<pre>command timed out</pre>"

    return Response(FLAG_PAGE_TEMPLATE.format(output=output_html), mimetype="text/html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
