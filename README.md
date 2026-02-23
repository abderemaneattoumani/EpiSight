# 🦠 EpiSight — Dashboard Épidémiologique Interactif

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)
![Data](https://img.shields.io/badge/Données-Santé_Publique_France-green)
![Rows](https://img.shields.io/badge/Dataset-38.6M_cas_analysés-orange)
![Prophet](https://img.shields.io/badge/IA-Prophet_(Meta)-purple)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

Dashboard interactif d'analyse épidémiologique Covid-19 en France,
construit sur les données officielles de Santé Publique France (data.gouv.fr).
Pipeline complet : collecte → nettoyage → analyse → visualisation → prédiction IA → déploiement.

## 🎯 Objectifs

- Télécharger et traiter les vraies données publiques de Santé Publique France
- Calculer les indicateurs épidémiologiques officiels (taux d'incidence, taux de positivité)
- Détecter automatiquement les vagues épidémiques par algorithme (SciPy)
- Visualiser l'évolution via un dashboard interactif Plotly/Streamlit
- Prédire l'évolution des cas sur 7 jours avec le modèle Prophet (Meta)

## 📊 Résultats clés

| Métrique | Valeur |
|---|---|
| Cas positifs analysés | 38 673 066 |
| Tests virologiques traités | 313 405 199 |
| Période couverte | Mai 2020 → Juin 2023 |
| Jours de données | 1 141 jours |
| Vagues détectées automatiquement | 8 vagues |
| Pic Omicron (MM7) | 354 350 cas/jour — 24 jan. 2022 |
| Pic réanimation | 7 019 patients — 8 avr. 2020 |
| Couverture vaccinale atteinte | 76,6% (schéma complet) |
| Intervalle de confiance Prophet | 95% |

> **Note sur la détection des vagues :** L'algorithme `find_peaks` (SciPy)
> détecte les maxima locaux avec un seuil de prominence de 15 000 cas/jour
> et une distance minimale de 60 jours entre pics.
> Les résultats sont cohérents avec les données officielles publiées par SPF.

## 🌐 Démo en ligne

**[👉 Accéder au Dashboard EpiSight](https://episight.streamlit.app)**

## 🗂️ Structure du projet

```
EpiSight/
├── data/
│   ├── raw/                          # Données brutes SPF (non versionnées)
│   └── processed/                    # Données nettoyées et indicateurs calculés
├── dashboard/
│   └── app.py                        # Application Streamlit (dark theme)
├── notebooks/
│   ├── 01_exploration.ipynb          # Découverte et compréhension des données
│   ├── 02_nettoyage.ipynb            # Nettoyage, types, valeurs manquantes
│   └── 03_analyse_indicateurs.ipynb  # Calcul des KPIs épidémiologiques
├── src/
│   ├── data_loader.py                # Pipeline ETL automatisé
│   ├── indicators.py                 # Calcul des indicateurs
│   └── predictions.py               # Modèle prédictif Prophet
├── assets/                           # Graphiques et visuels exportés
├── models/                           # Modèles entraînés (.pkl)
├── requirements.txt
└── README.md
```

## 🚀 Installation et utilisation

```bash
# 1. Cloner le projet
git clone https://github.com/abderemaneattoumani/EpiSight.git
cd EpiSight

# 2. Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le dashboard
streamlit run dashboard/app.py
```

Les données sont téléchargées automatiquement depuis data.gouv.fr
au premier lancement si elles sont absentes.

## 🔮 Modèle prédictif

```bash
# Générer les prédictions 7 jours (à relancer pour mettre à jour)
python src/predictions.py
```

## 📈 Indicateurs calculés

| Indicateur | Méthode |
|---|---|
| Taux d'incidence | Cas 7j glissants / population × 100 000 |
| Taux de positivité | Cas positifs / tests réalisés × 100 |
| Moyenne mobile 7j | Rolling mean — lissage effet week-end |
| Détection de vagues | `scipy.signal.find_peaks` (prominence=15 000, distance=60j) |
| Prédiction 7j | Prophet (Meta) — saisonnalités hebdo + annuelle |
| Taux occupation réa | Patients réa / capacité normale (5 000 lits) × 100 |

## 🧠 Concepts clés abordés

- **Pipeline ETL** — téléchargement, nettoyage et transformation de données publiques
- **Séries temporelles** — lissage, moyennes mobiles, détection de tendances
- **Feature Engineering épidémiologique** — taux d'incidence, seuils d'alerte SPF
- **Détection de pics** — algorithme `find_peaks` avec paramètres métier
- **Prévision par Prophet** — modèle additif avec composantes saisonnières
- **Données ouvertes** — manipulation d'APIs publiques (data.gouv.fr)

## 🔢 Fonctionnalités du dashboard

| Onglet | Contenu |
|---|---|
| 📈 Évolution temporelle | Cas, taux de positivité MM7, zones de vagues |
| 🏥 Hospitalisations | Patients hospitalisés, réanimation, décès |
| 💉 Vaccination | Couverture vaccinale par dose, doses journalières |
| 🗺️ Analyse départementale | Taux d'incidence avec seuils d'alerte officiels |
| 🔮 Prédiction IA | Prévision Prophet 7 jours avec intervalle de confiance 95% |

## ⚙️ Stack technique

| Outil | Rôle |
|---|---|
| Python 3.11 | Langage principal |
| Streamlit | Interface web interactive |
| Plotly | Visualisations dynamiques |
| Prophet (Meta) | Prédiction de séries temporelles |
| Pandas / NumPy | Traitement et manipulation des données |
| SciPy | Détection algorithmique des vagues (`find_peaks`) |
| Requests | Téléchargement automatique des datasets |
| data.gouv.fr | Source des données officielles SPF |

## 👤 Auteur

**Abderemane Attoumani**  
GitHub : [@abderemaneattoumani](https://github.com/abderemaneattoumani)

---
*Projet portfolio — Data Science & Santé Publique*
