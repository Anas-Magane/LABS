#!/usr/bin/env python3
"""
BlueOffice IT Helpdesk (port 6000)

Blind stored XSS -> admin session hijack.

Employees submit support tickets through the public form. A ticket's
"message" is rendered unescaped on the internal admin ticket-detail page
(the in-fiction excuse: tickets are supposed to support light rich-text /
emoji formatting so IT replies render nicely). A headless-Chromium bot
(bot.py) plays the role of the IT admin: it really logs in through
/admin/login with its own (never-exposed) credentials and then opens every
open ticket, so any injected script genuinely executes inside an
authenticated admin browser session - exactly like a real blind-XSS bug.

The flag lives behind /admin/flag, gated on that same session cookie. The
cookie itself is a normal Flask session cookie (HttpOnly, as it should be
in real life) - stealing document.cookie is NOT the intended path. The
intended path is a same-origin authenticated fetch() from inside the
stored payload, which rides the admin's session regardless of HttpOnly,
exfiltrated to the self-hosted mini "collector" below so no outbound
internet access is ever required.
"""
import os
import secrets
import threading
from datetime import datetime, timezone

from flask import Flask, Response, abort, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

FLAG = "CTF{BL1ND_XSS_H1J4CK5_TH3_4DM1N_B0T_0F_AR4M0n}"

# Real credentials for the simulated IT admin. Never rendered to any
# player-reachable page or response - bot.py imports them directly since
# it runs in the same process, exactly like a real admin who already
# knows their own password.
ADMIN_USERNAME = "itadmin"
ADMIN_PASSWORD = secrets.token_urlsafe(24)

TICKETS = []
_next_id = [1]
_lock = threading.Lock()
COLLECTORS = {}  # token -> list[dict]


def _new_ticket(name, subject, message):
    with _lock:
        tid = _next_id[0]
        _next_id[0] += 1
        TICKETS.append(
            {
                "id": tid,
                "name": name[:120],
                "subject": subject[:200],
                "message": message[:4000],
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
        )
        return tid


@app.route("/")
def index():
    return render_template("index.html", tickets=list(reversed(TICKETS)))


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip() or "Anonymous"
    subject = request.form.get("subject", "").strip() or "(no subject)"
    message = request.form.get("message", "")
    if not message.strip():
        return redirect(url_for("index"))
    tid = _new_ticket(name, subject, message)
    return redirect(url_for("submitted", ticket_id=tid))


@app.route("/submitted/<int:ticket_id>")
def submitted(ticket_id):
    return render_template("submitted.html", ticket_id=ticket_id)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            session.clear()
            session["is_admin"] = True
            return redirect(url_for("admin_tickets"))
        error = "Invalid credentials."
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


def _require_admin():
    if not session.get("is_admin"):
        abort(403)


@app.route("/admin/tickets")
def admin_tickets():
    _require_admin()
    return render_template("admin_tickets.html", tickets=list(reversed(TICKETS)))


@app.route("/admin/tickets/<int:ticket_id>")
def admin_ticket_detail(ticket_id):
    _require_admin()
    ticket = next((t for t in TICKETS if t["id"] == ticket_id), None)
    if not ticket:
        abort(404)
    return render_template("admin_ticket_detail.html", ticket=ticket)


@app.route("/admin/flag")
def admin_flag():
    _require_admin()
    return {"flag": FLAG}


@app.route("/collector/new")
def collector_new():
    token = secrets.token_urlsafe(16)
    with _lock:
        COLLECTORS[token] = []
    return render_template("collector_new.html", token=token)


_PIXEL_GIF = bytes.fromhex(
    "47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b"
)


@app.route("/collector/<token>/hit")
def collector_hit(token):
    if token not in COLLECTORS:
        abort(404)
    with _lock:
        COLLECTORS[token].append(
            {
                "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "query": request.query_string.decode("utf-8", "replace"),
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get("User-Agent", ""),
            }
        )
    return Response(_PIXEL_GIF, mimetype="image/gif")


@app.route("/collector/<token>/log")
def collector_log(token):
    if token not in COLLECTORS:
        abort(404)
    return render_template("collector_log.html", token=token, hits=list(reversed(COLLECTORS[token])))


@app.errorhandler(403)
def forbidden(_e):
    return render_template("forbidden.html"), 403


# Start the admin bot in-process (single gunicorn worker, so this thread
# is created exactly once). Local import avoids a circular import at
# module load time, since bot.py itself imports TICKETS from this module.
def _start_bot():
    from bot import run_bot_loop

    threading.Thread(
        target=run_bot_loop, args=(ADMIN_USERNAME, ADMIN_PASSWORD), daemon=True
    ).start()


if os.environ.get("HELPDESK_DISABLE_BOT") != "1":
    _start_bot()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
