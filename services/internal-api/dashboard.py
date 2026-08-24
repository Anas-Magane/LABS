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
<head>
<title>BlueOffice Internal HR Analytics</title>
<style>
  body { font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif; max-width: 720px;
         margin: 48px auto; color: #1c2b3a; padding: 0 1.5rem; }
  .banner { background: #fdecea; border: 1px solid #f3c2bc; color: #8a2c22; padding: 12px 16px;
            border-radius: 6px; margin-bottom: 24px; font-size: 0.9rem; }
  .box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.4rem; }
  code { background: #eef2f6; padding: 2px 6px; border-radius: 4px; font-size: 0.85rem; }
</style>
</head>
<body>
<div class="banner">
  INTERNAL ONLY - do not expose this dashboard outside the BlueOffice
  internal network.
</div>
<h1>BlueOffice Internal HR Analytics</h1>
<div class="box">
  <p>API base URL: <code>http://internal-api.blueoffice.local:5000/api</code></p>
  <p>API documentation is available at <code>/api/docs</code></p>
</div>
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
