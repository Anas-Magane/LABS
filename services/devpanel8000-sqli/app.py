#!/usr/bin/env python3
"""
BlueOffice Breach - Challenge 7: Dev Panel SQL Injection (port 8000)

The login form builds its SQL query via raw string formatting instead
of parameterized queries - a classic, intentional SQL injection bug.
A payload such as:

    username: ' OR '1'='1' -- -
    password: anything

bypasses authentication entirely. The SQLite database lives only
inside this container (no host mounts), so the injection can never
reach anything outside it.
"""

import os
import sqlite3

from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get("DEVPANEL_SECRET", "dev-panel-not-so-secret-key")

DB_PATH = "/app/data/devpanel.db"

# Base64 token intentionally left reachable in localStorage after login.
LOCALSTORAGE_TOKEN = "RkxBRzEgOiBDVEZ7NExXNFlTXzFOU1AzQ1RfRDNWVDAwTFNfQzRSM0ZVTExZfQ=="


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT)"
    )
    conn.execute("DELETE FROM users")
    conn.execute(
        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
        ("hamza", "Tr0ub4dor&3_DevPanel_2026", "hamza@technoIT.local"),
    )
    conn.commit()
    conn.close()


@app.route("/", methods=["GET"])
def root():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # VULNERABLE: raw string formatting straight into the SQL query.
        query = (
            "SELECT * FROM users WHERE username = '"
            + username
            + "' AND password = '"
            + password
            + "'"
        )

        conn = get_db()
        try:
            cur = conn.execute(query)
            row = cur.fetchone()
        except sqlite3.OperationalError:
            row = None
        finally:
            conn.close()

        if row:
            session["logged_in"] = True
            session["username"] = row["username"]
            session["email"] = row["email"]
            return redirect(url_for("dashboard"))
        error = "Invalid credentials"

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template(
        "dashboard.html",
        username=session.get("username"),
        email=session.get("email"),
        token=LOCALSTORAGE_TOKEN,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
