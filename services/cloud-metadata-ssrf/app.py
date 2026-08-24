#!/usr/bin/env python3
"""
BlueOffice Breach - Cloud Metadata SSRF (port 4000)

The report preview feature fetches whatever URL the caller supplies,
server-side, with no restriction on the destination host - a classic
SSRF. Pointed at this same instance's own (simulated) cloud instance
metadata endpoint, it leaks metadata that should never be reachable
from outside the machine.
"""

import requests
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    preview = None
    error = None
    url = ""
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            error = "Only http:// or https:// URLs are supported."
        else:
            try:
                resp = requests.get(url, timeout=3)
                preview = resp.text[:2000]
            except requests.RequestException:
                error = "Could not fetch that URL."
    return render_template("index.html", preview=preview, error=error, url=url)


@app.route("/opc/v2/instance/")
@app.route("/opc/v2/instance")
def instance_metadata():
    if request.remote_addr != "127.0.0.1":
        return "Forbidden", 403
    return {
        "availabilityDomain": "US-ASHBURN-AD-1",
        "compartmentId": "ocid1.compartment.oc1..aaaaaaaablueofficefakecompartment",
        "displayName": "blueoffice-report-gen-01",
        "hostname": "blueoffice-report-gen-01",
        "id": "ocid1.instance.oc1.iad.anuwcljsfakefakefakeinstanceid",
        "region": "us-ashburn-1",
        "metadata": {
            "flag": "flag15: CTF{SSRF_TO_TH3_CL0UD_M3T4D4T4_OWN3D}",
        },
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
