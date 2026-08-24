#!/usr/bin/env python3
"""
BlueOffice Breach - FST School Portal (port 9005)

/login builds its SQL query via raw string formatting on the
username/email field instead of parameterized queries - a classic,
intentional SQL injection bug, dumpable with sqlmap.

/admin trusts the client-supplied X-Forwarded-For header as if it
were a reliable indicator of the caller's real address - a classic
access-control bypass.
"""

import os
import sqlite3

from flask import Flask, request, render_template

app = Flask(__name__)

DB_PATH = "/app/data/FST.db"

STUDENTS = [
    ("Amine Rachidi", "amine.r", "amine.rachidi@fst.local", "R130245871", 20, "Rachidi@21"),
    ("Salma Idrissi", "salma.i", "salma.idrissi@fst.local", "R139988452", 21, "SalmaFST2024"),
    ("Younes Belkadi", "younes.b", "younes.belkadi@fst.local", "R127765511", 19, "Younes!987"),
    ("Nada Chafai", "nada.c", "nada.chafai@fst.local", "R141122987", 22, "Chafai_2023"),
    ("Anas Amine", "anas", "anas@fst.local", "R135566210", 21, "CTF{My_password}"),
    ("Khalid Mernissi", "khalid.m", "khalid.mernissi@fst.local", "R118834455", 20, "Khalid#20"),
    ("Yasmine Toumi", "yasmine.t", "yasmine.toumi@fst.local", "R129900112", 19, "Yasmine@Toumi"),
    ("Rachid Fassi", "rachid.f", "rachid.fassi@fst.local", "R144556677", 23, "FassiPass1"),
    ("Ikram Zerouali", "ikram.z", "ikram.zerouali@fst.local", "R122334455", 20, "Ikram_Z99"),
    ("Othmane Sabri", "othmane.s", "othmane.sabri@fst.local", "R136677889", 21, "OthmaneS2025"),
]

PROFS = [
    ("Prof. Hassan Idris", "h.idris@fst.local", "Computer Science", "A204"),
    ("Prof. Malika Ennasiri", "m.ennasiri@fst.local", "Mathematics", "B110"),
    ("Prof. Said Bouzid", "s.bouzid@fst.local", "Physics", "C305"),
    ("Prof. Widad Chraibi", "w.chraibi@fst.local", "Chemistry", "A118"),
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS students ("
        "id INTEGER PRIMARY KEY, full_name TEXT, username TEXT, email TEXT, "
        "CNE TEXT, age INTEGER, password TEXT)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS profs ("
        "id INTEGER PRIMARY KEY, full_name TEXT, email TEXT, department TEXT, office TEXT)"
    )
    conn.execute("DELETE FROM students")
    conn.execute("DELETE FROM profs")
    conn.executemany(
        "INSERT INTO students (full_name, username, email, CNE, age, password) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        STUDENTS,
    )
    conn.executemany(
        "INSERT INTO profs (full_name, email, department, office) VALUES (?, ?, ?, ?)",
        PROFS,
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    welcome = None
    if request.method == "POST":
        identifier = request.form.get("username", "")
        password = request.form.get("password", "")

        # VULNERABLE: raw string formatting straight into the SQL query.
        query = (
            "SELECT * FROM students WHERE username = '"
            + identifier
            + "' OR email = '"
            + identifier
            + "' AND password = '"
            + password
            + "'"
        )

        conn = get_db()
        try:
            cur = conn.execute(query)
            row = cur.fetchone()
        except sqlite3.Error:
            row = None
        finally:
            conn.close()

        if row:
            welcome = row["full_name"]
        else:
            error = "Invalid credentials."

    return render_template("login.html", error=error, welcome=welcome)


@app.route("/admin")
def admin():
    xff = request.headers.get("X-Forwarded-For", "").strip().lower()
    if xff in ("127.0.0.1", "localhost"):
        return render_template("admin.html")
    return render_template("forbidden.html"), 403


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
