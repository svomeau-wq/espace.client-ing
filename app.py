import os
from dotenv import load_dotenv

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
import resend

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")

if not RESEND_API_KEY:
    raise RuntimeError("RESEND_API_KEY n'est pas configurée.")

if not SENDER_EMAIL:
    raise RuntimeError("SENDER_EMAIL n'est pas configurée.")

resend.api_key = RESEND_API_KEY


# ------------------------------------------------------------------
# Données simulées (en mémoire, pas de base de données)
# ------------------------------------------------------------------
USER = {
    "first_name": "FREDERICK",
    "last_name": "ROUSELLE",
    "full_name": "FREDERICK ROUSSELLE",
    "client_number": "****",
    "email": "fredericrousselles01@gmail.com",
    "password": "****",  
}

ACCOUNTS = [
    {"id": "acc_courant", "type": "courant", "name": "Compte Courant",
     "iban": "FR76 3000 3010 4000 0201 8837 421", "bic": "MEINFRPP",
     "balance": 2000000.55, "available": 4620.55, "color": "#FF6200"},
    {"id": "acc_epargne", "type": "epargne", "name": "Livret Épargne Orange",
     "iban": "FR76 3000 3010 4000 0201 8837 999", "bic": "MEINFRPP",
     "balance": 645000.00, "available": 15230.00, "color": "#2C2A29", "rate": 3.0},
    {"id": "acc_joint", "type": "courant", "name": "Compte PRO",
     "iban": "FR76 3000 3010 4000 0201 8837 555", "bic": "MEINFRPP",
     "balance": 2000000.30, "available": 1090.30, "color": "#5A5A5A"},
]

TRANSACTIONS = [
    {"id": "t1", "account": "acc_courant", "date": "14 juil. 2026", "label": "Carrefour Market", "category": "Alimentation", "amount": -64.32, "method": "Carte"},
    {"id": "t2", "account": "acc_courant", "date": "14 juil. 2026", "label": "Salaire - Groupe Solaris", "category": "Revenus", "amount": 3200.00, "method": "Virement"},
    {"id": "t3", "account": "acc_courant", "date": "13 juil. 2026", "label": "SNCF Connect", "category": "Transport", "amount": -89.90, "method": "Carte"},
    {"id": "t4", "account": "acc_courant", "date": "12 juil. 2026", "label": "Spotify Premium", "category": "Abonnements", "amount": -10.99, "method": "Prélèvement"},
    {"id": "t5", "account": "acc_courant", "date": "11 juil. 2026", "label": "Pharmacie du Centre", "category": "Santé", "amount": -23.50, "method": "Carte"},
    {"id": "t6", "account": "acc_courant", "date": "10 juil. 2026", "label": "Virement vers Livret", "category": "Épargne", "amount": -500.00, "method": "Virement"},
    {"id": "t7", "account": "acc_courant", "date": "09 juil. 2026", "label": "EDF Électricité", "category": "Énergie", "amount": -78.40, "method": "Prélèvement"},
    {"id": "t8", "account": "acc_courant", "date": "08 juil. 2026", "label": "Amazon.fr", "category": "Shopping", "amount": -134.20, "method": "Carte"},
    {"id": "t9", "account": "acc_courant", "date": "07 juil. 2026", "label": "Boulangerie Lenôtre", "category": "Alimentation", "amount": -8.60, "method": "Carte"},
    {"id": "t10", "account": "acc_courant", "date": "06 juil. 2026", "label": "Remboursement Ameli", "category": "Santé", "amount": 42.00, "method": "Virement"},
    {"id": "t11", "account": "acc_epargne", "date": "10 juil. 2026", "label": "Virement depuis Courant", "category": "Épargne", "amount": 500.00, "method": "Virement"},
    {"id": "t12", "account": "acc_epargne", "date": "01 juil. 2026", "label": "Intérêts mensuels", "category": "Revenus", "amount": 38.07, "method": "Virement"},
    {"id": "t13", "account": "acc_joint", "date": "12 juil. 2026", "label": "Restaurant Le Comptoir", "category": "Loisirs", "amount": -76.00, "method": "Carte"},
    {"id": "t14", "account": "acc_joint", "date": "09 juil. 2026", "label": "Netflix", "category": "Abonnements", "amount": -15.49, "method": "Prélèvement"},
]

CARDS = [
    {"id": "card_gold", "label": "ING BANQUE Gold", "holder": "FREDERICK ROUSSELLE",
     "number": "4021 88•• •••• 3742", "full_number": "4021 8845 9021 3742",
     "expiry": "08/28", "type": "Mastercard Gold", "variant": "gold",
     "linked": "Compte Courant", "ceiling": 3000, "spent": 842.60, "contactless": True},
    {"id": "card_classic", "label": "ING BANQUE Classic", "holder": "FREDERICK ROUSSELLE",
     "number": "5355 22•• •••• 1098", "full_number": "5355 2210 4471 1098",
     "expiry": "03/27", "type": "Visa Classic", "variant": "classic",
     "linked": "Compte Joint", "ceiling": 1500, "spent": 91.49, "contactless": True},
]

SAVINGS = [
    {"id": "s1", "name": "Vacances 2026", "target": 3000, "current": 1850, "color": "#FF6200", "deadline": "01 août 2026"},
    {"id": "s2", "name": "Fonds d'urgence", "target": 10000, "current": 7200, "color": "#2C2A29", "deadline": "01 janv. 2026"},
    {"id": "s3", "name": "Nouvelle voiture", "target": 15000, "current": 4300, "color": "#009B7D", "deadline": "01 déc. 2026"},
]

DOMICILIATIONS = [
    {"id": "d1", "name": "EDF Électricité", "category": "Énergie", "amount": 78.40, "frequency": "Mensuel", "next": "09 août 2026", "active": True},
    {"id": "d2", "name": "Spotify Premium", "category": "Abonnements", "amount": 10.99, "frequency": "Mensuel", "next": "12 août 2026", "active": True},
    {"id": "d3", "name": "Netflix", "category": "Abonnements", "amount": 15.49, "frequency": "Mensuel", "next": "09 août 2026", "active": True},
    {"id": "d4", "name": "Assurance Habitat Plus", "category": "Assurance", "amount": 32.50, "frequency": "Mensuel", "next": "05 août 2026", "active": True},
    {"id": "d5", "name": "Free Mobile", "category": "Télécom", "amount": 19.99, "frequency": "Mensuel", "next": "03 août 2026", "active": False},
]

CREDITS = [
    {"id": "c1", "name": "Crédit Immobilier", "type": "Immobilier", "borrowed": 180000, "remaining": 142350, "monthly": 845.20, "rate": 1.85, "end": "01 juin 2039", "next": "01 août 2026", "progress": 21},
    {"id": "c2", "name": "Prêt Auto", "type": "Automobile", "borrowed": 18000, "remaining": 6420, "monthly": 312.50, "rate": 3.2, "end": "01 févr. 2027", "next": "01 août 2026", "progress": 64},
]

CREDIT_OFFERS = [
    {"name": "Prêt Personnel", "rate": 2.9, "max_amount": 75000, "max_duration": 84, "desc": "Financez vos projets sans justificatif d'utilisation."},
    {"name": "Prêt Auto", "rate": 2.5, "max_amount": 60000, "max_duration": 72, "desc": "Un taux avantageux pour votre véhicule neuf ou d'occasion."},
    {"name": "Prêt Travaux", "rate": 3.1, "max_amount": 50000, "max_duration": 120, "desc": "Rénovez et améliorez votre habitat en toute sérénité."},
]

ALERTS = [
    {"id": "al1", "type": "info", "title": "Virement reçu", "message": "Vous avez reçu 3 200,00 € de Groupe Solaris.", "date": "14/07/2026 09:12", "read": False},
    {"id": "al2", "type": "warning", "title": "Plafond carte proche", "message": "Votre carte ING BANQUE Gold a atteint 28% de son plafond mensuel.", "date": "13/07/2026 18:30", "read": False},
    {"id": "al3", "type": "success", "title": "Objectif épargne", "message": "Vacances 2026 : vous avez atteint 61% de votre objectif.", "date": "11/07/2026 10:05", "read": True},
    {"id": "al4", "type": "info", "title": "Prélèvement à venir", "message": "Assurance Habitat Plus (32,50 €) sera prélevé le 05/08.", "date": "10/07/2026 08:00", "read": True},
    {"id": "al5", "type": "warning", "title": "Nouvelle connexion", "message": "Connexion depuis un nouvel appareil (Paris, France).", "date": "09/07/2026 21:44", "read": True},
]

SPENDING = [
    {"category": "Alimentation", "amount": 320, "color": "#FF6200"},
    {"category": "Transport", "amount": 190, "color": "#2C2A29"},
    {"category": "Abonnements", "amount": 52, "color": "#009B7D"},
    {"category": "Shopping", "amount": 240, "color": "#F5A623"},
    {"category": "Énergie", "amount": 156, "color": "#7B61FF"},
    {"category": "Santé", "amount": 48, "color": "#00A3E0"},
]

MONTHLY_FLOW = [
    {"month": "Fév", "income": 3200, "expense": 2100},
    {"month": "Mar", "income": 3240, "expense": 2450},
    {"month": "Avr", "income": 3200, "expense": 1980},
    {"month": "Mai", "income": 3380, "expense": 2620},
    {"month": "Juin", "income": 3200, "expense": 2210},
    {"month": "Juil", "income": 3242, "expense": 1006},
]

# Virements réalisés (en mémoire)
TRANSFERS = []


# ------------------------------------------------------------------
# Filtres & utilitaires
# ------------------------------------------------------------------
@app.template_filter("eur")
def eur(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    s = f"{value:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s} €"


def nav_items():
    return [
        ("dashboard", "Tableau de bord", "grid"),
        ("comptes", "Mes comptes", "wallet"),
        ("releve", "Relevé", "file"),
        ("virements", "Virements", "swap"),
        ("cartes", "Cartes", "card"),
        ("epargne", "Épargne", "piggy"),
        ("domiciliations", "Domiciliations", "repeat"),
        ("credit", "Crédit", "bank"),
        ("rib", "RIB", "receipt"),
    ]


@app.context_processor
def inject_globals():
    unread = sum(1 for a in ALERTS if not a["read"])
    return {"USER": USER, "NAV": nav_items(), "UNREAD": unread}


def login_required():
    return session.get("auth") is True


# ------------------------------------------------------------------
# Email de confirmation (Resend)
# ------------------------------------------------------------------
def build_email_html(t):
    amount_str = f"{t['amount']:,.2f}".replace(",", " ").replace(".", ",") + " €"
    address_line = ""
    if t.get("address"):
        address_line += t["address"]
    if t.get("city"):
        address_line += (", " if address_line else "") + t["city"]
    if t.get("country"):
        address_line += (", " if address_line else "") + t["country"]
    return f"""
<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f5f5f4;font-family:Arial,Helvetica,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f4;padding:24px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;">
<tr><td style="background:#FF6200;padding:28px 32px;">
<table width="100%"><tr>
<td style="color:#fff;font-size:24px;font-weight:900;">Banque & Assurances pour les particuliers et les entreprises -ING</td>
<td align="right" style="color:#fff;font-size:13px;">Confirmation de virement</td>
</tr></table></td></tr>
<tr><td style="padding:32px;">
<h1 style="margin:0 0 8px;font-size:20px;color:#2C2A29;">Bonjour {t['b_first']},</h1>
<p style="margin:0 0 20px;font-size:15px;color:#57534e;line-height:1.5;">
Vous allez recevoir un virement de la part de <strong>{t['s_name']}</strong>. Voici le récapitulatif.</p>
<table width="100%" style="background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;margin-bottom:24px;">
<tr><td style="padding:20px 24px;text-align:center;">
<div style="font-size:13px;color:#9a3412;text-transform:uppercase;">Montant reçu</div>
<div style="font-size:34px;font-weight:900;color:#FF6200;margin-top:4px;">{amount_str}</div>
</td></tr></table>
<h3 style="margin:0 0 10px;font-size:14px;color:#2C2A29;text-transform:uppercase;">Expéditeur</h3>
<table width="100%" style="font-size:14px;color:#44403c;margin-bottom:22px;">
<tr><td style="padding:6px 0;color:#78716c;">Nom</td><td style="padding:6px 0;text-align:right;font-weight:bold;">{t['s_name']}</td></tr>
<tr><td style="padding:6px 0;color:#78716c;">IBAN émetteur</td><td style="padding:6px 0;text-align:right;font-family:monospace;">{t['s_iban']}</td></tr>
</table>
<h3 style="margin:0 0 10px;font-size:14px;color:#2C2A29;text-transform:uppercase;">Bénéficiaire</h3>
<table width="100%" style="font-size:14px;color:#44403c;margin-bottom:22px;">
<tr><td style="padding:6px 0;color:#78716c;">Nom complet</td><td style="padding:6px 0;text-align:right;font-weight:bold;">{t['b_first']} {t['b_last']}</td></tr>
<tr><td style="padding:6px 0;color:#78716c;">Email</td><td style="padding:6px 0;text-align:right;">{t['b_email']}</td></tr>
<tr><td style="padding:6px 0;color:#78716c;">Téléphone</td><td style="padding:6px 0;text-align:right;">{t.get('phone') or '—'}</td></tr>
<tr><td style="padding:6px 0;color:#78716c;">Adresse</td><td style="padding:6px 0;text-align:right;">{address_line or '—'}</td></tr>
<tr><td style="padding:6px 0;color:#78716c;">IBAN</td><td style="padding:6px 0;text-align:right;font-family:monospace;">{t['b_iban']}</td></tr>
<tr><td style="padding:6px 0;color:#78716c;">BIC</td><td style="padding:6px 0;text-align:right;font-family:monospace;">{t.get('bic') or '—'}</td></tr>
</table>
<h3 style="margin:0 0 10px;font-size:14px;color:#2C2A29;text-transform:uppercase;">Opération</h3>
<table width="100%" style="font-size:14px;color:#44403c;">
<tr><td style="padding:6px 0;color:#78716c;">Référence</td><td style="padding:6px 0;text-align:right;font-family:monospace;">{t['reference']}</td></tr>
<tr><td style="padding:6px 0;color:#78716c;">Motif</td><td style="padding:6px 0;text-align:right;">{t.get('motif') or '—'}</td></tr>
<tr><td style="padding:6px 0;color:#78716c;">Statut</td><td style="padding:6px 0;text-align:right;"><span style="background:#dcfce7;color:#15803d;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:bold;">Confirmé</span></td></tr>
</table>
</td></tr>
<tr><td style="background:#2C2A29;padding:20px 32px;text-align:center;">
<p style="margin:0;color:#a8a29e;font-size:12px;line-height:1.5;">
Email envoyé automatiquement par ING Banque.<br>© 2026 ING BANK. Tous droits réservés.</p>
</td></tr>
</table></td></tr></table></body></html>
"""


def send_confirmation_email(t):
    if not RESEND_API_KEY:
        return False, "Clé API Resend manquante."
    try:
        resend.Emails.send({
            "from": f"ING BANQUE <{SENDER_EMAIL}>",
            "to": [t["b_email"]],
            "subject": f"Virement reçu de {t['s_name']} — {t['amount']:.2f} €",
            "html": build_email_html(t),
        })
        return True, None
    except Exception as e:
        return False, str(e)


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------
@app.route("/")
def index():
    if login_required():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["auth"] = True
        return redirect(url_for("dashboard"))
    return render_template("login.html", user=USER)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    total = sum(a["balance"] for a in ACCOUNTS)
    spending_total = sum(s["amount"] for s in SPENDING)
    flow_max = max(max(f["income"], f["expense"]) for f in MONTHLY_FLOW)
    # segments du donut (conic-gradient)
    segments, acc = [], 0.0
    for s in SPENDING:
        frac = s["amount"] / spending_total * 100
        segments.append({"color": s["color"], "start": acc, "end": acc + frac})
        acc += frac
    return render_template(
        "dashboard.html", accounts=ACCOUNTS, total=total,
        transactions=TRANSACTIONS[:6], spending=SPENDING,
        spending_total=spending_total, segments=segments,
        flow=MONTHLY_FLOW, flow_max=flow_max, active="dashboard",
    )


@app.route("/comptes")
def comptes():
    if not login_required():
        return redirect(url_for("login"))
    sel = request.args.get("acc", ACCOUNTS[0]["id"])
    account = next((a for a in ACCOUNTS if a["id"] == sel), ACCOUNTS[0])
    txs = [t for t in TRANSACTIONS if t["account"] == account["id"]]
    return render_template("comptes.html", accounts=ACCOUNTS, account=account,
                           transactions=txs, active="comptes")


@app.route("/releve")
def releve():
    if not login_required():
        return redirect(url_for("login"))
    acc = request.args.get("acc", "all")
    typ = request.args.get("type", "all")
    q = request.args.get("q", "").strip().lower()
    items = list(TRANSACTIONS)
    if acc != "all":
        items = [t for t in items if t["account"] == acc]
    if typ == "in":
        items = [t for t in items if t["amount"] > 0]
    elif typ == "out":
        items = [t for t in items if t["amount"] < 0]
    if q:
        items = [t for t in items if q in t["label"].lower() or q in t["category"].lower()]
    total_in = sum(t["amount"] for t in items if t["amount"] > 0)
    total_out = sum(t["amount"] for t in items if t["amount"] < 0)
    return render_template("releve.html", accounts=ACCOUNTS, transactions=items,
                           total_in=total_in, total_out=total_out,
                           acc=acc, typ=typ, q=q, active="releve")


@app.route("/virements", methods=["GET", "POST"])
def virements():
    if not login_required():
        return redirect(url_for("login"))
    result = None
    if request.method == "POST":
        f = request.form
        try:
            amount = float(f.get("amount", "0").replace(",", "."))
        except ValueError:
            amount = 0
        errors = []
        if not f.get("b_first") or not f.get("b_last"):
            errors.append("Le prénom et le nom du bénéficiaire sont requis.")
        if not f.get("b_email") or "@" not in f.get("b_email", ""):
            errors.append("Un email de bénéficiaire valide est requis.")
        if not f.get("b_iban"):
            errors.append("L'IBAN du bénéficiaire est requis.")
        if amount <= 0:
            errors.append("Le montant doit être supérieur à 0.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("virements.html", accounts=ACCOUNTS,
                                   form=f, result=None, active="virements")

        from_acc = next((a for a in ACCOUNTS if a["id"] == f.get("from_account")), ACCOUNTS[0])
        reference = "MJ-" + os.urandom(5).hex().upper()
        transfer = {
            "reference": reference,
            "s_name": USER["full_name"],
            "s_iban": from_acc["iban"],
            "from_account": from_acc["name"],
            "b_first": f.get("b_first"), "b_last": f.get("b_last"),
            "b_email": f.get("b_email"),
            "address": f.get("address", ""), "city": f.get("city", ""),
            "country": f.get("country", ""), "phone": f.get("phone", ""),
            "b_iban": f.get("b_iban"), "bic": f.get("bic", ""),
            "amount": amount, "motif": f.get("motif", ""),
        }
        ok, err = send_confirmation_email(transfer)
        transfer["email_sent"] = ok
        TRANSFERS.insert(0, transfer)
        result = {"reference": reference, "email_sent": ok, "error": err,
                  "email": transfer["b_email"]}
        if ok:
            flash(f"Virement effectué ! Email de confirmation envoyé à {transfer['b_email']}.", "success")
        else:
            flash(f"Virement enregistré, mais l'email n'a pas pu être envoyé ({err}).", "error")
        return render_template("virements.html", accounts=ACCOUNTS,
                               form={}, result=result, active="virements")

    return render_template("virements.html", accounts=ACCOUNTS, form={},
                           result=None, active="virements")


@app.route("/cartes")
def cartes():
    if not login_required():
        return redirect(url_for("login"))
    for c in CARDS:
        c["usage"] = min(100, round(c["spent"] / c["ceiling"] * 100))
    return render_template("cartes.html", cards=CARDS, active="cartes")


@app.route("/epargne")
def epargne():
    if not login_required():
        return redirect(url_for("login"))
    livret = next((a for a in ACCOUNTS if a["type"] == "epargne"), None)
    for g in SAVINGS:
        g["pct"] = min(100, round(g["current"] / g["target"] * 100))
    total_saved = sum(g["current"] for g in SAVINGS)
    total_target = sum(g["target"] for g in SAVINGS)
    return render_template("epargne.html", livret=livret, savings=SAVINGS,
                           total_saved=total_saved, total_target=total_target,
                           active="epargne")


@app.route("/domiciliations")
def domiciliations():
    if not login_required():
        return redirect(url_for("login"))
    active_items = [d for d in DOMICILIATIONS if d["active"]]
    monthly = sum(d["amount"] for d in active_items)
    return render_template("domiciliations.html", domiciliations=DOMICILIATIONS,
                           count=len(active_items), monthly=monthly, active="domiciliations")


@app.route("/credit")
def credit():
    if not login_required():
        return redirect(url_for("login"))
    total_remaining = sum(c["remaining"] for c in CREDITS)
    total_monthly = sum(c["monthly"] for c in CREDITS)
    return render_template("credit.html", credits=CREDITS, offers=CREDIT_OFFERS,
                           total_remaining=total_remaining, total_monthly=total_monthly,
                           active="credit")


@app.route("/rib")
def rib():
    if not login_required():
        return redirect(url_for("login"))
    sel = request.args.get("acc", ACCOUNTS[0]["id"])
    account = next((a for a in ACCOUNTS if a["id"] == sel), ACCOUNTS[0])
    return render_template("rib.html", accounts=ACCOUNTS, account=account, active="rib")


@app.route("/alertes")
def alertes():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("alertes.html", alerts=ALERTS, active="alertes")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
