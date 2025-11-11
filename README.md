# 🛡️ AEGIS — Mission & Resource Management System

**AEGIS** est une plateforme de gestion d’opérations permettant de planifier, suivre et analyser des missions avec une interface moderne et sécurisée.  
Le projet a été développé dans le cadre du **Portfolio Project – Stage 4 (Holberton School)**.

---

## 🚀 Objectif du projet

Offrir aux coordinateurs et administrateurs un tableau de bord centralisé pour :
- Créer et gérer des **missions**.
- Assigner des **ressources** à ces missions.
- Visualiser les **données météo** selon la localisation de la mission.
- Superviser l’activité via une **carte interactive**.

---

## 🧩 Fonctionnalités principales

| Rôle | Fonctionnalité |
|------|----------------|
| Utilisateur | Connexion sécurisée (JWT), consultation des missions. |
| Coordinateur | Création et modification des missions, affectation des ressources. |
| Administrateur | Gestion des utilisateurs et des rôles. |
| Tous | Accès au tableau de bord (missions, météo, carte, ressources). |

---

## 🏗️ Stack technique

### Backend (API)
- **Framework** : Flask  
- **ORM** : SQLAlchemy  
- **Authentification** : JWT (PyJWT + bcrypt)  
- **Migrations** : Alembic  
- **Tests** : Pytest / Postman  
- **Base de données** : SQLite (MVP) – compatible PostgreSQL

### Frontend (Interface)
- **Framework** : React (Vite)
- **UI** : TailwindCSS v4
- **API Calls** : Axios
- **Map** : Leaflet (OpenStreetMap)
- **Météo** : OpenWeatherMap API

---

## 📂 Structure du projet

AEGIS/
├── backend/
│ ├── app.py # Point d'entrée Flask
│ ├── models/ # User, Mission, Resource...
│ ├── routes/ # Auth, Users, Missions, Resources
│ ├── services/ # Logique métier (assignations)
│ ├── test/ # Tests unitaires Pytest
│ ├── config.py, db.py, extensions.py
│ └── alembic/ # Migrations de schéma
│
├── frontend/
│ ├── public/ # favicon/logo
│ ├── src/
│ │ ├── api/ # appels Axios (missions, auth, etc.)
│ │ ├── components/ # Sidebar, Dashboard, MapView, WeatherWidget
│ │ ├── pages/ # Login, Dashboard, Missions
│ │ └── main.jsx, index.css
│ └── vite.config.js
│
├── docs/ # Documentation technique
├── requirements.txt # Dépendances Python
└── README.md

---

## 🧪 Tests

### 🧰 1. Tests API (Postman / Newman)

Une collection **AEGIS Backend.postman_collection.json** est fournie pour valider les endpoints clés :

| Endpoint | Méthode | Objectif | Résultat attendu |
|-----------|----------|----------|------------------|
| `/auth/login` | POST | Connexion utilisateur | Retourne un token JWT |
| `/users` | POST | Création d’un utilisateur | 201 Created |
| `/missions` | GET | Lister les missions | 200 OK (liste paginée) |
| `/missions` | POST | Créer une mission | 201 Created |
| `/missions/:id` | PATCH | Modifier une mission | 200 OK |
| `/resources` | POST | Ajouter une ressource | 201 Created |
| `/assign` | POST | Assigner une ressource | 201 Created |
| `/missions/:id/assign` | POST | Alias assignation | 201 Created |

⚙️ Pour lancer la suite de tests :
```
newman run docs/AEGIS_Backend.postman_collection.json
🧱 2. Tests unitaires (Pytest)
Les fichiers de test se trouvent dans backend/test/.

Exemples :

Copier le code
pytest backend/test/test_mission_model.py -v
pytest backend/test/test_db.py -v
Exemple : test_mission_model.py
python
Copier le code
def test_create_mission(db_session):
    mission = Mission(title="Recon", status=Status.PLANNED)
    db_session.add(mission)
    db_session.flush()
    assert mission.id is not None
    assert mission.status == Status.PLANNED
Exemple : test_user_creation.py
python
Copier le code
def test_user_password_hash(app_client):
    user = User(first_name="Test", email="test@aegis.fr", password_hash="hash")
    assert user.first_name == "Test"
✅ Tous les tests Postman et Pytest passent sur le MVP.

🌦️ API externe
OpenWeatherMap
URL : https://api.openweathermap.org/data/2.5/weather

Utilisation : météo basée sur lat / lon de la mission sélectionnée

Gestion : composant WeatherWidget.jsx

Exemple :

javascript
Copier le code
const res = await axios.get(
  `https://api.openweathermap.org/data/2.5/weather`,
  { params: { lat, lon, units: "metric", appid: import.meta.env.VITE_WEATHER_KEY } }
);
💻 Lancement du projet
Backend
Copier le code
cd backend
source ../.venv/bin/activate   # ou .venv\Scripts\activate sous Windows
flask run
Frontend
Copier le code
cd frontend
npm install
npm run dev
Application accessible sur :
👉 http://localhost:5173

🔒 Sécurité & rôles
Rôle	Droits
Admin	CRUD complet sur utilisateurs, missions, ressources
Coordinateur	Créer / éditer missions + assigner ressources
Observateur	Lecture seule
Authentification	JWT avec expiration (15 min)
Mots de passe	Hashés via bcrypt

🌍 Évolutions prévues
Export PDF/CSV post-mission

Notifications temps réel

PWA mobile terrain

Passage à PostgreSQL pour déploiement (Railway / Render)

👨‍💻 Auteur
Shakib Rojas
Développeur Fullstack — Projet réalisé dans le cadre de la formation Holberton School