# COFINANCE CI — Plateforme de Microfinance

Projet académique — Plateforme digitale de gestion de microcrédits, d'assurance mobile et de support client en temps réel.

Stack : Python / Django 5.x / Django REST Framework / Django Channels

---

## Ce que fait le projet

- Gestion complète du cycle de vie d'un microcrédit (soumission, analyse, approbation, décaissement)
- Suivi des remboursements avec calcul automatique des pénalités
- Souscription à des produits d'assurance mobile
- Chat en temps réel entre clients et agents (WebSocket)
- Tableau de bord avec KPIs et courbes pour l'administration
- API REST documentée automatiquement sur `/api/docs/`

---

## Prérequis

Avant de commencer, assure-toi d'avoir :

- Python 3.11 ou plus
- pip
- Git

C'est tout. Pas besoin de Redis ou de PostgreSQL pour faire tourner le projet en local.

---

## Installation

**1. Clone le projet**  

```bash
git clone https://github.com/ton-username/microfinance.git
cd microfinance
```

**2. Crée un environnement virtuel**  

```bash
python -m venv venv
```

Active-le :

```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

**3. Installe les dépendances**  

```bash
pip install -r requirements.txt
```

**4. Lance les migrations**  

```bash
python manage.py migrate
```

**5. Charge les données de démonstration**  

```bash
python manage.py loaddata fixtures/seed_db.json
```

**6. Lance le serveur**  

```bash
python manage.py runserver
```

Le site est maintenant accessible sur http://127.0.0.1:8000

**7. (Optionnel) Tâches planifiées quotidiennes**

Les alertes d'échéance (J-3, retard J+1) et d'expiration d'assurance (J-15, passage automatique en *Expirée*) sont regroupées dans une commande à lancer chaque jour (via `cron` en production) :

```bash
python manage.py run_daily_tasks
```

---

## Comptes de démonstration

Le mot de passe dépend du rôle : `admin123` pour l'administrateur, `agent123` pour les agents, `client123` pour les clients.

| Utilisateur | Rôle | Mot de passe |
|---|---|---|
| tossou | Administrateur | `admin123` |
| operi | Agent de terrain | `agent123` |
| nguessan | Agent de terrain | `agent123` |
| kouame | Agent de terrain | `agent123` |
| aloukou | Client | `client123` |
| gauli | Client | `client123` |
| ehoussou | Client | `client123` |
| yao | Client | `client123` |

*(12 comptes clients au total : aloukou, gauli, ehoussou, oulai, yao, diabate, kone, bamba, gnagne, soro, toure, gbagbo.)*

---

## Documentation API

La documentation Swagger est générée automatiquement. Une fois le serveur lancé, ouvre :

```
http://127.0.0.1:8000/api/docs/
```

Tu verras tous les endpoints listés avec la possibilité de les tester directement depuis le navigateur.

---

## Démonstration du chat en temps réel

Pour voir le chat WebSocket fonctionner :

1. Lance le serveur avec `python manage.py runserver`
2. Ouvre **deux onglets** dans ton navigateur
3. Dans le premier onglet, connecte-toi avec un compte client (ex: `aloukou_ariel`)
4. Dans le second onglet, connecte-toi avec un agent (ex: `operi_carla`)
5. Le client ouvre une conversation, l'agent répond — les messages arrivent en temps réel sans rechargement de page

---

## Structure du projet

```
microfinance/
├── accounts/        Authentification, profils, rôles, historique connexions
├── credits/         Gestion des microcrédits et workflow d'approbation
├── repayments/      Suivi des remboursements et pénalités de retard
├── insurance/       Produits d'assurance et polices souscrites
├── dashboard/       KPIs et courbes pour l'administrateur
├── notifications/   Notifications in-app déclenchées automatiquement
├── chat/            Chat en temps réel via WebSocket
├── reports/         Exports CSV et PDF
├── base/            Templates HTML et fichiers statiques
├── microfinance/    Configuration du projet (settings, urls, routing)
├── fixtures/        Données de démonstration
└── manage.py
```

---

## Endpoints principaux

```
POST   /api/auth/login/              Connexion
POST   /api/auth/register/           Inscription
GET    /api/credits/                 Liste des demandes de crédit
POST   /api/credits/                 Soumettre une demande
POST   /api/credits/<id>/status/     Changer le statut d'un dossier
POST   /api/repayments/              Enregistrer un paiement
GET    /api/insurance/products/      Catalogue des assurances
POST   /api/insurance/policies/      Souscrire à une assurance
GET    /api/dashboard/               KPIs et courbes (Admin)
GET    /api/notifications/           Mes notifications
GET    /api/chat/                    Mes conversations
GET    /api/docs/                    Documentation Swagger complète
```

WebSocket :
```
ws://127.0.0.1:8000/ws/chat/<conversation_id>/?token=<access_token>
```

---

## Variables d'environnement (optionnel)

Pour la production, crée un fichier `.env` à la racine :

```
SECRET_KEY=change-this-in-production
DEBUG=False
DB_NAME=cofinance
DB_USER=postgres
DB_PASSWORD=motdepasse
DB_HOST=localhost
DB_PORT=5432
```

En développement, les valeurs par défaut dans `settings.py` suffisent.

---

## Passer en production

Deux choses à changer dans `settings.py` :

**Base de données — passer à PostgreSQL**

Décommente le bloc PostgreSQL dans `settings.py` et commente le bloc SQLite.

**WebSocket — passer à Redis**

Remplace `InMemoryChannelLayer` par `RedisChannelLayer` dans `CHANNEL_LAYERS` et installe Redis sur le serveur.

---

Projet réalisé dans le cadre d'un cours académique de développement web.
