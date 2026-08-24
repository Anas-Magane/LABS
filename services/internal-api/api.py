#!/usr/bin/env python3
"""
BlueOffice Breach - Challenge 9 (internal): HR Analytics internal API.

Only reachable inside the `pivotnet` Docker network (172.30.80.0/24) -
never published to the host. Intended to be reached by a player who has
pivoted through the rh-jboss container (e.g. with ligolo-ng) after
landing on 172.30.80.50:5000.

/api/files?name=... is an intentionally lazy "file read" helper: local
names are sandboxed to FILES_DIR, but any value that looks like a
host:port (or a full URL) is instead fetched over HTTP - a classic
SSRF bug hiding behind what looks like a simple file-read parameter.
"""

import os
import re

import requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

FILES_DIR = "/app/files"
URL_RE = re.compile(r"^https?://", re.IGNORECASE)
HOSTPORT_RE = re.compile(r"^[A-Za-z0-9_.\-]+:\d+/")

API_INDEX = {
    "service": "BlueOffice Internal HR API",
    "status": "running",
    "version": "1.0-internal",
    "message": "Internal HR analytics API. Documentation is available.",
    "endpoints": [
        "/api/status",
        "/api/candidates",
        "/api/interviews",
        "/api/docs",
        "/api/files?name=readme.txt",
    ],
}


@app.route("/api")
def api_index():
    return jsonify(API_INDEX)


@app.route("/api/status")
def api_status():
    return jsonify({"status": "ok", "uptime": "internal", "node": "internal-api"})


@app.route("/api/candidates")
def api_candidates():
    return jsonify(
        {
            "candidates": [
                {"name": "Karim El Idrissi", "position": "Java Backend Engineer"},
                {"name": "Nadia Chraibi", "position": "Network Security Analyst"},
                {"name": "Omar Fassi", "position": "Systems Administrator"},
            ]
        }
    )


@app.route("/api/interviews")
def api_interviews():
    return jsonify(
        {
            "interviews": [
                {"candidate": "Karim El Idrissi", "interviewer": "Sana Amrani", "when": "Mon 10:00"},
                {"candidate": "Omar Fassi", "interviewer": "Youssef Bennani", "when": "Tue 14:30"},
            ]
        }
    )


@app.route("/api/docs")
def api_docs():
    return jsonify(
        {
            "docs": "BlueOffice Internal HR API v1.0-internal",
            "note": "File helper: GET /api/files?name=readme.txt",
        }
    )


@app.route("/api/files")
def api_files():
    name = request.args.get("name", "")
    if not name:
        return jsonify({"error": "missing name parameter"}), 400

    # SSRF path: anything that looks like a URL or a host:port/path is
    # fetched over HTTP instead of being treated as a local filename.
    if URL_RE.match(name):
        target = name
    elif HOSTPORT_RE.match(name):
        target = f"http://{name}"
    else:
        safe_name = os.path.basename(name)
        path = os.path.join(FILES_DIR, safe_name)
        if not os.path.isfile(path):
            return jsonify({"error": "file not found"}), 404
        with open(path, "r", errors="replace") as fh:
            return Response(fh.read(), mimetype="text/plain")

    try:
        resp = requests.get(target, timeout=5)
        return Response(resp.content, status=resp.status_code, mimetype="text/plain")
    except requests.RequestException as exc:
        return jsonify({"error": f"upstream fetch failed: {exc}"}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
