#!/usr/bin/env python3
"""
BlueOffice Employee Kudos Wall (port 5050)

A second, differently-shaped blind stored XSS -> manager session hijack.

Anyone can post a "kudos" card for a colleague. Approved kudos show up on
the public wall (escaped, safe). Before that, every kudos sits in a
moderation queue that only the HR manager reviews - and the moderation
preview renders a kudos card's message unescaped (in-fiction excuse: kudos
cards support emoji/GIF embeds so they preview exactly as they'll appear
on the wall). A headless-Chromium bot (bot.py) plays the HR manager: it
really logs into /manager/login with its own credentials, then opens
every pending kudos card in the queue.

The flag lives behind /manager/secret-notes, gated on that manager
session. As in the helpdesk challenge, the intended path is a same-origin
authenticated fetch() from inside the stored payload (works regardless of
HttpOnly), exfiltrated to this app's own self-hosted mini "collector" -
no outbound internet access required.
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

FLAG = "CTF{5T0R3D_XSS_1S_5T1LL_D4NG3R0U5_4_4R4M0N}"

# Real credentials for the simulated HR manager. Never rendered to any
# player-reachable page - bot.py imports them directly since it runs in
# the same process, exactly like a real manager who already knows their
# own password.
MANAGER_USERNAME = "hr.manager"
MANAGER_PASSWORD = secrets.token_urlsafe(24)

PENDING = []  # kudos awaiting moderation
APPROVED = []  # kudos published to the public wall (rendered escaped)
_next_id = [1]
_lock = threading.Lock()
COLLECTORS = {}  # token -> list[dict]


def _new_kudos(sender, recipient, message):
    with _lock:
        kid = _next_id[0]
        _next_id[0] += 1
        PENDING.append(
            {
                "id": kid,
                "sender": sender[:80],
                "recipient": recipient[:80],
                "message": message[:2000],
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
        )
        return kid


@app.route("/")
def index():
    return render_template("index.html", wall=list(reversed(APPROVED)))


@app.route("/post", methods=["POST"])
def post():
    sender = request.form.get("sender", "").strip() or "Anonymous"
    recipient = request.form.get("recipient", "").strip() or "the team"
    message = request.form.get("message", "")
    if not message.strip():
        return redirect(url_for("index"))
    kid = _new_kudos(sender, recipient, message)
    return redirect(url_for("posted", kudos_id=kid))


@app.route("/posted/<int:kudos_id>")
def posted(kudos_id):
    return render_template("posted.html", kudos_id=kudos_id)


@app.route("/manager/login", methods=["GET", "POST"])
def manager_login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u == MANAGER_USERNAME and p == MANAGER_PASSWORD:
            session.clear()
            session["is_manager"] = True
            return redirect(url_for("manager_queue"))
        error = "Invalid credentials."
    return render_template("manager_login.html", error=error)


@app.route("/manager/logout")
def manager_logout():
    session.clear()
    return redirect(url_for("manager_login"))


def _require_manager():
    if not session.get("is_manager"):
        abort(403)


@app.route("/manager/queue")
def manager_queue():
    _require_manager()
    return render_template("manager_queue.html", pending=list(reversed(PENDING)))


@app.route("/manager/queue/<int:kudos_id>")
def manager_queue_detail(kudos_id):
    _require_manager()
    kudos = next((k for k in PENDING if k["id"] == kudos_id), None)
    if not kudos:
        abort(404)
    return render_template("manager_queue_detail.html", kudos=kudos)


@app.route("/manager/queue/<int:kudos_id>/approve", methods=["POST"])
def manager_approve(kudos_id):
    _require_manager()
    with _lock:
        kudos = next((k for k in PENDING if k["id"] == kudos_id), None)
        if kudos:
            PENDING.remove(kudos)
            APPROVED.append(kudos)
    return redirect(url_for("manager_queue"))


@app.route("/manager/secret-notes")
def manager_secret_notes():
    _require_manager()
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


# Start the HR manager bot in-process (single gunicorn worker, so this
# thread is created exactly once). Local import avoids a circular import
# at module load time, since bot.py imports PENDING from this module.
def _start_bot():
    from bot import run_bot_loop

    threading.Thread(
        target=run_bot_loop, args=(MANAGER_USERNAME, MANAGER_PASSWORD), daemon=True
    ).start()


if os.environ.get("KUDOSWALL_DISABLE_BOT") != "1":
    _start_bot()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
