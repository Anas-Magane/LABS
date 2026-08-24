#!/usr/bin/env python3
"""
BlueOffice Breach - Challenge 9 (internal): HR Analytics dashboard.

Runs on port 3000 in the SAME container as the internal-api service
(api.py, port 5000). Never published to the host or to any other
container - only reachable as 127.0.0.1:3000 from inside this
container, which is exactly what the /api/files SSRF bug in api.py is
used to reach.
"""

from flask import Flask, Response

app = Flask(__name__)

DASHBOARD_HTML = """<!doctype html>
<html>
<head><title>BlueOffice Internal HR Analytics</title></head>
<body style="font-family:sans-serif;max-width:800px;margin:40px auto;color:#222">
<div style="background:#fee;border:1px solid #c00;padding:10px;margin-bottom:20px">
  INTERNAL ONLY - do not expose this dashboard outside the BlueOffice
  internal network.
</div>
<h1>BlueOffice Internal HR Analytics</h1>
<p>API base URL: <code>http://internal-api.blueoffice.local:5000/api</code></p>
<p>API documentation is available at <code>/api/docs</code></p>
</body>
</html>
"""

FLAG_PATH = "/app/flag8.txt"


@app.route("/")
def index():
    return Response(DASHBOARD_HTML, mimetype="text/html")


@app.route("/flag8.txt")
def flag():
    with open(FLAG_PATH, "r") as fh:
        return Response(fh.read(), mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
