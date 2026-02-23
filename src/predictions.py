#  EpiSight — Modèle prédictif
#  Algorithme : Prophet (Meta) — spécialisé séries temporelles

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def preparer_donnees_prophet(df_tests_nat: pd.DataFrame, 
                              colonne: str = 'cas_mm7') -> pd.DataFrame:
    """
    Prophet exige un format précis : 2 colonnes exactement
    - 'ds' : dates (DatetimeIndex)
    - 'y'  : valeurs à prédire (float, positives)
    """
    df = df_tests_nat[['jour', colonne]].copy()
    df = df.rename(columns={'jour': 'ds', colonne: 'y'})
    df = df.dropna()
    df = df[df['y'] >= 0]  # Prophet n'accepte pas les valeurs négatives
    return df


def entrainer_et_predire(df_tests_nat: pd.DataFrame,
                          jours_prediction: int = 7) -> tuple:
    """
    Entraînement du modèle Prophet sur les données historiques et prédit les jours suivants
    
    Retourne : (dataframe_historique_avec_prediction, dataframe_prediction_seule)
    """
    try:
        from prophet import Prophet
    except ImportError:
        raise ImportError("Prophet non installé. Exécute : pip install prophet")
    
    # Préparation des données
    df_prophet = preparer_donnees_prophet(df_tests_nat)
    
    print(f"Entraînement sur {len(df_prophet)} jours de données...")
    print(f"Période : {df_prophet['ds'].min().date()} → {df_prophet['ds'].max().date()}")
    
    # Configuration du modèle
    modele = Prophet(
        changepoint_prior_scale=0.15,  # Sensibilité aux changements de tendance
        seasonality_prior_scale=10,    # Importance des effets saisonniers
        yearly_seasonality=True,       # Patterns annuels (vagues saisonnières)
        weekly_seasonality=True,       # Patterns hebdomadaires (effet week-end)
        daily_seasonality=False,       # Pas pertinent avec données quotidiennes agrégées
        interval_width=0.95            # Intervalle de confiance à 95%
    )
    
    # Entraînement
    modele.fit(df_prophet)
    
    # Création du dataframe futur
    futur = modele.make_future_dataframe(periods=jours_prediction)
    
    # Prédiction
    prediction = modele.predict(futur)
    
    # Extraction des prédictions futures uniquement
    derniere_date_reelle = df_prophet['ds'].max()
    prediction_future = prediction[
        prediction['ds'] > derniere_date_reelle
    ][['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    
    # Arrondir et éviter les valeurs négatives
    for col in ['yhat', 'yhat_lower', 'yhat_upper']:
        prediction_future[col] = prediction_future[col].clip(lower=0).round(0)
    
    prediction_future.columns = ['date', 'prediction', 'borne_basse', 'borne_haute']
    
    print(f"\nPrédictions pour les {jours_prediction} prochains jours :")
    print(prediction_future.to_string(index=False))
    
    return prediction, prediction_future, modele


def sauvegarder_predictions(prediction_future: pd.DataFrame, 
                             dossier_processed: Path) -> Path:
    chemin = dossier_processed / "predictions_7j.csv"
    prediction_future.to_csv(chemin, index=False)
    print(f"\nPrédictions sauvegardées : {chemin}")
    return chemin


if __name__ == "__main__":
    # Test standalone du module
    PROCESSED = Path(__file__).parent.parent / "data" / "processed"
    tests_nat = pd.read_csv(PROCESSED / "indicateurs_tests.csv", parse_dates=['jour'])
    
    prediction_complete, prediction_future, modele = entrainer_et_predire(tests_nat)
    sauvegarder_predictions(prediction_future, PROCESSED)