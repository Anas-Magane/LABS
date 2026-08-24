#!/usr/bin/env python3
"""
BlueOffice Breach - Challenge 3: Client-Side Auth + SSTI (port 3000)

Two intentional bugs:
  1. Authentication is enforced only in client-side JavaScript
     (see templates/index.html) - credentials are hardcoded in the
     page source.
  2. The /welcome endpoint builds a Jinja2 template via plain string
     concatenation of user input and renders it with
     render_template_string -> classic Server-Side Template Injection
     leading to remote code execution.

Any code executed through the SSTI runs as the unprivileged "sstiuser"
account inside THIS container only. There are no host bind-mounts and
no elevated capabilities, so it can never reach the Oracle Cloud host.
"""

from flask import Flask, request, render_template, render_template_string

app = Flask(__name__)

FLAG0 = "CTF{WelCome_t0_TH2_CTF_lets_G000_4_THe_NEXT!!}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", flag=FLAG0)


@app.route("/welcome", methods=["POST"])
def welcome():
    name = request.form.get("name", "")
    # VULNERABLE: user input is concatenated directly into a Jinja2
    # template string before rendering -> Server-Side Template Injection.
    template = "welcome " + name + " !"
    return render_template_string(template)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
