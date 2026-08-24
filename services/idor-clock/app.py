#!/usr/bin/env python3
import hashlib
from datetime import datetime, timezone

from flask import Flask, request, render_template

app = Flask(__name__)

_RAW_USERS = [
    ("Sara Amrani", "sara.amrani@fst.local", "password",
     "Loves morning coffee and early lectures.", "Just finished my first semester project!"),
    ("Youssef Idrissi", "youssef.idrissi@fst.local", "admin",
     "Studying computer science, into competitive programming.", "Anyone up for a study group this weekend?"),
    ("Imane Benali", "imane.benali@fst.local", "qwerty",
     "President of the robotics club.", "Our robot took 2nd place at the regional contest!"),
    ("Karim Ziani", "karim.ziani@fst.local", "123456",
     "Third-year physics student.", "Lab report due Friday, send help."),
    ("Nadia El Fassi", "nadia.elfassi@fst.local", "welcome",
     "Enjoys hiking and open-source contributions.", "Merged my first pull request today!"),
    ("Omar Chraibi", "omar.chraibi@fst.local", "student123",
     "Math club treasurer.", "Exam season is rough this year."),
    ("Salma Bennis", "salma.bennis@fst.local", "fst2025",
     "Loves painting and databases.", "SQL is basically art if you think about it."),
    ("Hamza Tazi", "hamza.tazi@fst.local", "anas123",
     "Football team captain.", "Match this Saturday, come support us!"),
    ("Fatima Zahra Idrissi", "fatimazahra.idrissi@fst.local", "nabil123",
     "Volunteers at the campus library.", "Looking for study partners for finals."),
    ("Adil Kabbaj", "adil.kabbaj@fst.local", "letmein",
     "Runs the university's Linux user group.", "Setting up a new practice server soon."),
    ("Rania Alaoui", "rania.alaoui@fst.local", "monkey",
     "Chemistry major, part-time barista.", "Coffee and chemistry go hand in hand."),
    ("Bilal Ouahbi", "bilal.ouahbi@fst.local", "dragon",
     "Enjoys chess and puzzles.", "Solved today's puzzle in record time."),
    ("Zineb Amine", "zineb.amine@fst.local", "sunshine",
     "Biology student, plant enthusiast.", "My succulent collection keeps growing."),
    ("Mehdi Saadi", "mehdi.saadi@fst.local", "iloveyou",
     "Guitar player and part-time DJ.", "Campus concert next Friday, don't miss it!"),
    ("Houda Cherkaoui", "houda.cherkaoui@fst.local", "master",
     "Data science enthusiast.", "Competition results are in!"),
    ("Yassine Bouzid", "yassine.bouzid@fst.local", "football",
     "Studies mechanical engineering.", "3D printed my first working prototype today."),
    ("Lina Fikri", "lina.fikri@fst.local", "shadow",
     "Enjoys photography around campus.", "Sunset shots from the library rooftop."),
    ("Anas Mrabet", "anas.mrabet@fst.local", "trustno1",
     "Loves reverse engineering old software.", "Found an interesting old binary to analyze."),
    ("Nabil Amrani", "nabil.amrani@fst.local", "superman",
     "Runs the campus radio station.", "New episode dropping this weekend!"),
    ("Khadija Ait", "khadija.ait@fst.local", "batman",
     "Loves morning runs and clean code.", "flag14: CTF{1D0R_ByPaSS_SuccEeSS!!!!!!}"),
]

USERS = [
    {
        "id": i + 1,
        "name": name,
        "email": email,
        "password": password,
        "description": description,
        "post": post,
    }
    for i, (name, email, password, description, post) in enumerate(_RAW_USERS)
]


@app.route("/")
def index():
    user_id = request.args.get("id")
    if user_id is not None:
        return _profile_response(user_id)
    now = datetime.now(timezone.utc)
    return render_template(
        "index.html",
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S UTC"),
    )


@app.route("/profile")
def profile():
    return _profile_response(request.args.get("id"))


def _profile_response(user_id):
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        return render_template("notfound.html"), 404
    user = next((u for u in USERS if u["id"] == uid), None)
    if user is None:
        return render_template("notfound.html"), 404
    return render_template("profile.html", user=user)


@app.route("/db")
def db_dump():
    rows = [
        {
            "id": u["id"],
            "name": u["name"],
            "email": u["email"],
            "md5": hashlib.md5(u["password"].encode()).hexdigest(),
        }
        for u in USERS
    ]
    return render_template("db.html", rows=rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
