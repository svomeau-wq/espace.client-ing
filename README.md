# Meindjo — Application bancaire (Flask)

Application web bancaire (style ING) en **Flask** avec templates Jinja2.
Aucune base de données : toutes les données sont simulées en mémoire.
Le formulaire de virement envoie un **email de confirmation au bénéficiaire** via **Resend**.

## Structure
```
meindjo_flask/
├── app.py              # Application Flask (routes + données + envoi email)
├── requirements.txt    # Dépendances
├── static/
│   └── style.css       # Styles (thème orange ING)
└── templates/          # Pages HTML (Jinja2)
    ├── base.html
    ├── _macros.html
    ├── login.html
    ├── dashboard.html
    ├── comptes.html
    ├── releve.html
    ├── virements.html
    ├── cartes.html
    ├── epargne.html
    ├── domiciliations.html
    ├── credit.html
    ├── rib.html
    └── alertes.html
```

## Installation & lancement
```bash
pip install -r requirements.txt

# Configurez vos variables (voir .env.example) :
export RESEND_API_KEY="re_votre_cle"
export SENDER_EMAIL="noreply@crasdor.org"
export SECRET_KEY="une-cle-secrete"

python app.py
```
Ouvrez ensuite http://localhost:5000

## Connexion (démo)
Les identifiants sont pré-remplis, cliquez simplement sur « Se connecter ».

## Email de virement (Resend)
- Renseignez `RESEND_API_KEY` et `SENDER_EMAIL` (domaine vérifié sur Resend).
- À la validation d'un virement, un email HTML récapitulatif est envoyé à l'adresse du bénéficiaire.
- Si l'email échoue, le virement est tout de même enregistré (l'app le signale).

> Note : la clé API par défaut dans `app.py` est fournie pour la démo. En production,
> définissez-la via variable d'environnement et ne la stockez jamais en clair.
