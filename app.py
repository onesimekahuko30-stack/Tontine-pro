from flask import Flask, request, redirect, session
import sqlite3
from datetime import datetime
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "tontine_secret"

DB = "tontine.db"

os.makedirs("static", exist_ok=True)

# =====================================
# DATABASE
# =====================================

def init_db():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS membres(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        paye INTEGER,
        montant REAL,
        date TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS historique(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        membre TEXT,
        montant REAL,
        date TEXT
    )
    """)

    c.execute("SELECT COUNT(*) FROM membres")

    count = c.fetchone()[0]

    if count == 0:

        membres = [
            ("onesime",1,10,"28/05/2026"),
            ("daniel",0,0,""),
            ("kavet",1,10,"28/05/2026"),
            ("edidiat",0,0,""),
            ("iconnu",1,10,"28/05/2026")
        ]

        c.executemany(
            "INSERT INTO membres(nom,paye,montant,date) VALUES(?,?,?,?)",
            membres
        )

    conn.commit()
    conn.close()

init_db()

# =====================================
# ADMINS
# =====================================

ADMINS = {
    "admin":"admin",
    "onesime":"1234"
}

# =====================================
# LOGIN
# =====================================

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        user = request.form.get("user")
        password = request.form.get("pass")

        if user in ADMINS and ADMINS[user] == password:

            session["admin"] = user

            return redirect("/dashboard")

        return "<h1>Login incorrect</h1>"

    return """

    <body style='margin:0;
    background:#0f172a;
    font-family:Arial;
    color:white;'>

    <div style='max-width:350px;
    margin:auto;
    margin-top:120px;
    background:#1e293b;
    padding:30px;
    border-radius:20px;'>

    <h1 style='text-align:center;'>
    💰 Tontine Pro
    </h1>

    <form method='POST'>

    <input name='user'
    placeholder='Utilisateur'

    style='width:100%;
    padding:12px;
    margin-top:10px;
    border:none;
    border-radius:10px;'>

    <input type='password'
    name='pass'
    placeholder='Mot de passe'

    style='width:100%;
    padding:12px;
    margin-top:10px;
    border:none;
    border-radius:10px;'>

    <button type='submit'

    style='width:100%;
    padding:12px;
    margin-top:15px;
    background:#2563eb;
    color:white;
    border:none;
    border-radius:10px;'>

    Login

    </button>

    </form>

    </div>

    </body>

    """

# =====================================
# DASHBOARD
# =====================================

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/")

    mode = request.args.get("mode","dark")

    if mode == "light":

        bg = "#f1f5f9"
        card = "white"
        text = "black"

    else:

        bg = "#0f172a"
        card = "#1e293b"
        text = "white"

    q = request.args.get("q","").lower()

    filtre = request.args.get("filtre","all")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT * FROM membres")

    membres = c.fetchall()

    c.execute("SELECT * FROM historique ORDER BY id DESC")

    historiques = c.fetchall()

    conn.close()

    payes = 0
    non_payes = 0
    total = 0

    page = f"""

    <body style='margin:0;
    background:{bg};
    color:{text};
    font-family:Arial;'>

    <div style='padding:15px;'>

    <h1>💰 Dashboard Tontine</h1>

    <form method='GET'

    style='display:flex;
    gap:10px;
    flex-wrap:wrap;'>

    <input type='hidden'
    name='mode'
    value='{mode}'>

    <input name='q'
    value='{q}'
    placeholder='Recherche membre...'

    style='flex:1;
    padding:10px;
    border-radius:10px;
    border:none;'>

    <select name='filtre'

    style='padding:10px;
    border-radius:10px;'>

    <option value='all'>Tous</option>
    <option value='paye'>Payés</option>
    <option value='non'>Non payés</option>

    </select>

    <button type='submit'

    style='background:#2563eb;
    color:white;
    border:none;
    padding:10px;
    border-radius:10px;'>

    OK

    </button>

    </form>

    <br>

    <a href='/dashboard?mode=dark'
    style='background:black;
    color:white;
    padding:10px;
    border-radius:10px;
    text-decoration:none;'>

    🌙 Dark

    </a>

    <a href='/dashboard?mode=light'
    style='background:white;
    color:black;
    padding:10px;
    border-radius:10px;
    text-decoration:none;'>

    ☀️ Light

    </a>

    <br><br>

    <div style='overflow:auto;'>

    <table border='1'
    width='100%'

    style='border-collapse:collapse;
    background:{card};'>

    <tr>

    <th>Nom</th>
    <th>Statut</th>
    <th>Montant</th>
    <th>Date</th>
    <th>Action</th>
    <th>Supprimer</th>

    </tr>

    """

    for m in membres:

        id, nom, paye, montant, date = m

        if q and q not in nom.lower():
            continue

        if filtre == "paye" and paye == 0:
            continue

        if filtre == "non" and paye == 1:
            continue

        if paye == 1:

            statut = "A payé"
            color = "lightgreen"

            payes += 1

        else:

            statut = "Non payé"
            color = "red"

            non_payes += 1

        total += montant

        page += f"""

        <tr>

        <td>{nom}</td>

        <td style='color:{color};
        font-weight:bold;'>

        {statut}

        </td>

        <td>{montant}$</td>

        <td>{date}</td>

        <td>

        """

        if paye == 0:

            page += f"""

            <a href='/payer/{nom}'

            style='background:green;
            color:white;
            padding:6px;
            border-radius:6px;
            text-decoration:none;'>

            💰 Payer

            </a>

            """

        else:

            page += "✅"

        page += f"""

        </td>

        <td>

        <a href='/supprimer/{nom}'

        style='background:red;
        color:white;
        padding:6px;
        border-radius:6px;
        text-decoration:none;'>

        ❌

        </a>

        </td>

        </tr>

        """

    total_membres = payes + non_payes

    if total_membres > 0:

        progression = round((payes / total_membres) * 100,1)

    else:

        progression = 0

    page += f"""

    </table>

    </div>

    <br>

    <div style='display:grid;
    grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
    gap:15px;'>

    <div style='background:{card};
    padding:20px;
    border-radius:20px;'>

    <h3>Total collecté</h3>

    <h1>{total}$</h1>

    </div>

    <div style='background:{card};
    padding:20px;
    border-radius:20px;'>

    <h3>Payés</h3>

    <h1>{payes}</h1>

    </div>

    <div style='background:{card};
    padding:20px;
    border-radius:20px;'>

    <h3>Non payés</h3>

    <h1>{non_payes}</h1>

    </div>

    <div style='background:{card};
    padding:20px;
    border-radius:20px;'>

    <h3>Progression</h3>

    <h1>{progression}%</h1>

    </div>

    </div>

    <br>

    <div style='background:{card};
    padding:20px;
    border-radius:20px;'>

    <h2>🔔 Notifications retardataires</h2>

    """

    for m in membres:

        if m[2] == 0:

            page += f"<p>⚠️ {m[1]} doit encore payer</p>"

    page += "</div><br>"

    page += f"""

    <div style='background:{card};
    padding:20px;
    border-radius:20px;'>

    <h2>📜 Historique</h2>

    """

    for h in historiques:

        hid, membre, montant, date = h

        page += f"""

        <p>

        💰 {membre} a payé {montant}$ le {date}

        </p>

        """

    page += "</div><br>"

    beneficiaire_actuel = "iconnu"
    prochain_beneficiaire = "daniel"

    page += f"""

    <div style='background:{card};
    padding:20px;
    border-radius:20px;'>

    <h2>🏆 Bénéficiaire actuel</h2>

    <p style='font-size:22px;
    font-weight:bold;
    color:lightgreen;'>

    {beneficiaire_actuel}

    </p>

    <h2>⏭️ Prochain bénéficiaire</h2>

    <p style='font-size:22px;
    font-weight:bold;
    color:orange;'>

    {prochain_beneficiaire}

    </p>

    </div>

    <br>

    <div style='background:{card};
    padding:20px;
    border-radius:20px;'>

    <h2>📊 Statistiques avancées</h2>

    <p>👥 Total membres : {total_membres}</p>

    <p>💰 Total collecté : {total}$</p>

    <p>✅ Membres payés : {payes}</p>

    <p>❌ Membres non payés : {non_payes}</p>

    <p>📈 Progression : {progression}%</p>

    </div>

    <br>

    <a href='/add'

    style='background:green;
    color:white;
    padding:10px;
    border-radius:10px;
    text-decoration:none;'>

    ➕ Ajouter membre

    </a>

    <a href='/graph'

    style='background:#2563eb;
    color:white;
    padding:10px;
    border-radius:10px;
    text-decoration:none;'>

    📊 Graphique

    </a>

    <a href='/reset_month'

    style='background:#dc2626;
    color:white;
    padding:10px;
    border-radius:10px;
    text-decoration:none;'>

    🔄 Nouveau mois

    </a>

    <a href='/logout'

    style='background:black;
    color:white;
    padding:10px;
    border-radius:10px;
    text-decoration:none;'>

    Logout

    </a>

    </div>

    </body>

    """

    return page

# =====================================
# AJOUT MEMBRE
# =====================================

@app.route("/add", methods=["GET","POST"])
def add():

    if request.method == "POST":

        nom = request.form["nom"]

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute(
            "INSERT INTO membres(nom,paye,montant,date) VALUES(?,?,?,?)",
            (nom,0,0,"")
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return """

    <body style='font-family:Arial;
    background:#0f172a;
    color:white;
    padding:40px;'>

    <h1>Ajouter membre</h1>

    <form method='POST'>

    <input name='nom'
    placeholder='Nom membre'

    style='padding:10px;
    border-radius:10px;'>

    <button

    style='padding:10px;
    background:green;
    color:white;
    border:none;
    border-radius:10px;'>

    Ajouter

    </button>

    </form>

    </body>

    """

# =====================================
# PAYER
# =====================================

@app.route("/payer/<nom>")
def payer(nom):

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    date = datetime.now().strftime("%d/%m/%Y")

    c.execute(
        "UPDATE membres SET paye=1,montant=10,date=? WHERE nom=?",
        (date, nom)
    )

    c.execute(
        "INSERT INTO historique(membre,montant,date) VALUES(?,?,?)",
        (nom,10,date)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# =====================================
# RESET MOIS
# =====================================

@app.route("/reset_month")
def reset_month():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "UPDATE membres SET paye=0,montant=0,date=''"
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# =====================================
# SUPPRIMER
# =====================================

@app.route("/supprimer/<nom>")
def supprimer(nom):

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "DELETE FROM membres WHERE nom=?",
        (nom,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# =====================================
# GRAPHIQUE
# =====================================

@app.route("/graph")
def graph():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT paye FROM membres")

    data = c.fetchall()

    conn.close()

    payes = 0
    non_payes = 0

    for d in data:

        if d[0] == 1:
            payes += 1
        else:
            non_payes += 1

    plt.figure(figsize=(5,5))

    plt.pie(
        [payes, non_payes],
        labels=["Payés","Non payés"],
        autopct="%1.1f%%"
    )

    plt.title("Etat des paiements")

    plt.savefig("static/graph.png")

    plt.close()

    return """

    <body style='background:#0f172a;
    color:white;
    text-align:center;
    font-family:Arial;'>

    <h1>📊 Graphique</h1>

    <img src='/static/graph.png'

    style='width:90%;
    max-width:500px;
    background:white;
    border-radius:20px;'>

    <br><br>

    <a href='/dashboard'

    style='background:#2563eb;
    color:white;
    padding:10px;
    border-radius:10px;
    text-decoration:none;'>

    Retour

    </a>

    </body>

    """

# =====================================
# LOGOUT
# =====================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# =====================================
# RUN
# =====================================

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)