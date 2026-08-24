#!/usr/bin/env python3
"""
BlueOffice Breach - Challenge 6: "Apache Struts2" CVE-2017-5638 (port 8888)

This service presents itself as an old Apache Struts2 Showcase
application and reproduces the *externally observable* behaviour of
CVE-2017-5638 (the Jakarta Multipart parser OGNL injection RCE): a
crafted `Content-Type` header containing an OGNL payload of the form
`#cmd='<command>'` results in that command being executed on the
server and its output streamed back in the HTTP response - exactly
how the real vulnerability is exploited in the wild (e.g. the
well-known public proof-of-concept payload format).

It is a contained, from-scratch re-implementation (no real Java/OGNL
stack, no real Struts2 code) built specifically so that the same
exploitation technique used against the real CVE works against this
lab: a Content-Type header carrying `#cmd='...'`. Any command executed
this way runs as an unprivileged user inside THIS container only.
"""

import re
import subprocess

from flask import Flask, request, Response

app = Flask(__name__)

CMD_PATTERN = re.compile(r"#cmd\s*=\s*(['\"])(.*?)\1")

SHOWCASE_HTML = """<!doctype html>
<html>
<head><title>Struts2 Showcase</title></head>
<body>
<h1>Welcome to Struts2 Showcase!</h1>
<p>Powered by Apache Struts2 2.3.x</p>
<hr>
<h3>File Upload</h3>
<form action="/doUpload.action" method="post" enctype="multipart/form-data">
  <input type="file" name="upload">
  <input type="submit" value="Upload">
</form>
<p style="color:#999;font-size:12px">BlueOffice internal mirror - scheduled for decommission.</p>
</body>
</html>
"""


@app.before_request
def jakarta_multipart_parser():
    """
    Reproduces the CVE-2017-5638 trigger point: the vulnerable code path
    runs while the Content-Type header is being parsed by the multipart
    parser, BEFORE any action/controller logic executes - so this check
    applies to every endpoint, exactly like the real bug.
    """
    content_type = request.headers.get("Content-Type", "")
    match = CMD_PATTERN.search(content_type)
    if not match:
        return None

    command = match.group(2)
    try:
        result = subprocess.run(
            ["/bin/bash", "-c", command],
            capture_output=True,
            timeout=10,
        )
        body = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        body = b"command timed out\n"

    return Response(body, mimetype="text/plain")


@app.route("/", methods=["GET", "POST"])
def index():
    return Response(SHOWCASE_HTML, mimetype="text/html")


@app.route("/doUpload.action", methods=["GET", "POST"])
def do_upload():
    return Response(SHOWCASE_HTML, mimetype="text/html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
