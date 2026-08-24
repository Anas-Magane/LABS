#!/usr/bin/env python3
import datetime

import jwt
from flask import Flask, request, render_template, redirect, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

JWT_SECRET = "Nabil2027@"
JWT_ALGO = "HS256"

USERS = {}


def issue_token(username, role="user"):
    payload = {
        "username": username,
        "role": role,
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def read_token():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[len("Bearer "):].strip()
    return request.cookies.get("token")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            error = "Username and password are required."
        elif username in USERS:
            error = "That username is already taken."
        else:
            USERS[username] = generate_password_hash(password)
            token = issue_token(username, role="user")
            resp = make_response(render_template("token.html", username=username, token=token))
            resp.set_cookie("token", token, httponly=False)
            return resp
    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        stored = USERS.get(username)
        if stored and check_password_hash(stored, password):
            token = issue_token(username, role="user")
            resp = make_response(render_template("token.html", username=username, token=token))
            resp.set_cookie("token", token, httponly=False)
            return resp
        error = "Invalid credentials."
    return render_template("login.html", error=error)


@app.route("/admin")
def admin():
    token = read_token()
    if not token:
        return render_template("forbidden.html"), 403
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.PyJWTError:
        return render_template("forbidden.html"), 403

    if payload.get("role") != "admin":
        return render_template("forbidden.html"), 403

    return render_template("admin.html", username=payload.get("username", "admin"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
