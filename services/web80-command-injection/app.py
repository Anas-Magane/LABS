#!/usr/bin/env python3
"""
BlueOffice Breach - Challenge 2: Web Command Injection (port 80)

A tiny internal "portal" with an intentionally vulnerable /internal endpoint.
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

SITE_STYLE = """
    :root {
      --navy: #0a1628; --navy-2: #0f2137; --surface: #16233a; --surface-2: #1c2c46;
      --text: #e6edf5; --text-dim: #94a7bf; --accent: #38bdf8; --accent-2: #2563eb;
      --border: rgba(255,255,255,0.08);
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
           background: var(--navy); color: var(--text); }
    header.site { display: flex; align-items: center; justify-content: space-between;
           padding: 1.1rem 2.5rem; background: var(--navy-2); border-bottom: 1px solid var(--border); }
    .brand { display: flex; align-items: center; gap: 0.6rem; font-weight: 700; font-size: 1.15rem;
             color: var(--text); text-decoration: none; }
    .brand .mark { width: 28px; height: 28px; border-radius: 7px;
             background: linear-gradient(135deg, var(--accent), var(--accent-2)); }
    nav.site a { color: var(--text-dim); text-decoration: none; margin-left: 1.75rem; font-size: 0.92rem; }
    nav.site a:hover { color: var(--text); }
    main.wrap { max-width: 880px; margin: 0 auto; padding: 4rem 2rem; }
    .eyebrow { color: var(--accent); text-transform: uppercase; letter-spacing: 0.08em;
               font-size: 0.78rem; font-weight: 600; }
    h1 { font-size: 2.1rem; margin: 0.6rem 0 0.8rem; }
    .lead { color: var(--text-dim); font-size: 1.05rem; max-width: 560px; line-height: 1.6; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.1rem; margin-top: 2.5rem; }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
            padding: 1.4rem; }
    .card h3 { margin: 0 0 0.4rem; font-size: 1rem; }
    .card p { margin: 0; color: var(--text-dim); font-size: 0.9rem; line-height: 1.5; }
    .status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%;
            background: #34d399; margin-right: 0.4rem; box-shadow: 0 0 6px #34d399; }
    footer.site { text-align: center; padding: 2rem; color: var(--text-dim); font-size: 0.82rem;
            border-top: 1px solid var(--border); margin-top: 3rem; }
"""

INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BlueOffice | Internal Portal</title>
<style>""" + SITE_STYLE + """
    .hero-actions { margin-top: 2rem; }
    .btn { display: inline-block; padding: 0.7rem 1.3rem; border-radius: 6px; text-decoration: none;
           font-size: 0.9rem; font-weight: 600; }
    .btn.primary { background: var(--accent-2); color: white; }
    .btn.ghost { color: var(--text-dim); border: 1px solid var(--border); margin-left: 0.75rem; }
</style>
</head>
<body>
<header class="site">
  <a class="brand" href="/"><span class="mark"></span> BlueOffice</a>
  <nav class="site">
    <a href="/app">Internal Tools</a>
    <a href="/admin">Admin</a>
  </nav>
</header>
<main class="wrap">
  <div class="eyebrow">Internal Portal</div>
  <h1>Employee &amp; Systems Portal</h1>
  <p class="lead">
    Central access point for BlueOffice internal applications - status pages,
    administrative tooling, and IT-managed services. This portal is being
    migrated to the new identity platform; some pages remain on the legacy
    stack during the transition.
  </p>
  <div class="hero-actions">
    <a class="btn primary" href="/app">Internal Tools</a>
    <a class="btn ghost" href="/admin">Admin Console</a>
  </div>
  <div class="grid">
    <div class="card">
      <h3><span class="status-dot"></span>Platform status</h3>
      <p>All monitored internal services are currently operating normally.</p>
    </div>
    <div class="card">
      <h3>Maintenance window</h3>
      <p>Scheduled maintenance is posted here ahead of any planned downtime.</p>
    </div>
    <div class="card">
      <h3>IT support</h3>
      <p>For access issues or outages, contact the IT helpdesk through the intranet.</p>
    </div>
  </div>
</main>
<footer class="site">&copy; BlueOffice. Internal use only.</footer>
</body>
</html>
"""

APP_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BlueOffice | Internal Tools</title>
<style>""" + SITE_STYLE + """</style>
</head>
<body>
<header class="site">
  <a class="brand" href="/"><span class="mark"></span> BlueOffice</a>
  <nav class="site">
    <a href="/">Portal</a>
    <a href="/admin">Admin</a>
  </nav>
</header>
<main class="wrap">
  <div class="eyebrow">Internal Tools</div>
  <h1>BlueOffice App <span style="color:var(--text-dim);font-weight:400;font-size:1.1rem;">v1.0</span></h1>
  <p class="lead"><span class="status-dot"></span>Internal tools status: OK</p>
  <div class="grid">
    <div class="card">
      <h3>Service health</h3>
      <p>All internal tooling endpoints reported healthy on the last check.</p>
    </div>
    <div class="card">
      <h3>Deployment</h3>
      <p>Running the current internal build. No pending updates.</p>
    </div>
  </div>
</main>
<footer class="site">&copy; BlueOffice. Internal use only.</footer>
</body>
</html>
"""

ADMIN_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BlueOffice | Admin</title>
<style>""" + SITE_STYLE + """
    .center { display: flex; align-items: center; justify-content: center; min-height: 70vh; text-align: center; }
    .code { color: var(--text-dim); font-size: 0.85rem; margin-top: 0.5rem; }
</style>
</head>
<body>
<header class="site">
  <a class="brand" href="/"><span class="mark"></span> BlueOffice</a>
  <nav class="site"><a href="/">Portal</a></nav>
</header>
<div class="center">
  <div>
    <h1>403 &mdash; Forbidden</h1>
    <p class="lead" style="margin:0 auto;">Admins only. This area requires elevated internal credentials.</p>
  </div>
</div>
</body>
</html>
"""

FLAG_PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>BlueOffice | Internal Tools</title>
</head>
<body style="margin:0;font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;background:#0a1628;color:#e6edf5;">
<div style="padding:1.1rem 2.5rem;background:#0f2137;border-bottom:1px solid rgba(255,255,255,0.08);font-weight:700;">BlueOffice</div>
<div style="max-width:880px;margin:0 auto;padding:2.5rem 2rem;">
{output}
</div>
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


@app.route("/internal")
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
