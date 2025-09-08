import sys
import pandas as pd
from src.exception import CustomException
from src.utils import load_object

# AJOUTER
import os, pathlib, logging, numpy as np
logging.basicConfig(level=logging.INFO)

import os, logging
logging.info("Exists model? %s", os.path.exists("artefact/model.pkl"))
logging.info("Exists preproc? %s", os.path.exists("artefact/preprocessor.pkl"))

# Permet de surcharger les chemins via variables d'env en prod (EB)
MODEL_PATH_ENV = os.getenv("MODEL_PATH")
PREPROC_PATH_ENV = os.getenv("PREPROC_PATH")


class PredictPipeline:
    def __init__(self):
        pass
    

    def predict(self, features):
        try:
            model_path = 'artefact\model.pkl'
            preprocessor_path = 'artefact\preprocessor.pkl'
                        # AJOUTER — sécuriser/résoudre les chemins des artefacts
            try:
                # 1) Variables d'environnement (prioritaires si définies)
                if MODEL_PATH_ENV:
                    model_path = MODEL_PATH_ENV
                if PREPROC_PATH_ENV:
                    preprocessor_path = PREPROC_PATH_ENV

                # 2) Normaliser les séparateurs (Windows -> Linux)
                model_path = model_path.replace("\\", "/")
                preprocessor_path = preprocessor_path.replace("\\", "/")

                # 3) Résolution vers des chemins absolus si les fichiers ne sont pas trouvés
                if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
                    # /var/app/current (Elastic Beanstalk) ou racine du projet en local
                    here = pathlib.Path(__file__).resolve()
                    project_root = here.parents[2]  # src/pipeline/ -> src -> <racine>
                    candidates = [
                        project_root / "artifacts" / "model.pkl",
                        project_root / "artefact" / "model.pkl",               # fallback si ton dossier s'appelle 'artefact'
                        pathlib.Path("/var/app/current/artifacts/model.pkl"),  # EB
                        pathlib.Path("/var/app/current/artefact/model.pkl"),
                    ]
                    for c in candidates:
                        if c.exists():
                            model_path = str(c)
                            break

                    candidates = [
                        project_root / "artifacts" / "preprocessor.pkl",
                        project_root / "artefact" / "preprocessor.pkl",
                        pathlib.Path("/var/app/current/artifacts/preprocessor.pkl"),
                        pathlib.Path("/var/app/current/artefact/preprocessor.pkl"),
                    ]
                    for c in candidates:
                        if c.exists():
                            preprocessor_path = str(c)
                            break

                logging.info(f"Using model_path={model_path}")
                logging.info(f"Using preprocessor_path={preprocessor_path}")
            except Exception:
                # on ignore la résolution avancée si problème, les chemins initiaux seront tentés
                pass

            model = load_object(file_path=model_path)
            preprocessor = load_object(file_path=preprocessor_path)
            # AJOUTER — sanitation minimale des features pour éviter les 500
            features = features.copy()

            # caster proprement les numériques (NaN si invalide)
            for col in ["reading_score", "writing_score"]:
                if col in features.columns:
                    features[col] = pd.to_numeric(features[col], errors="coerce")

            # remplacer les catégorielles manquantes par 'Unknown'
            for col in ["gender", "race_ethnicity", "parental_level_of_education", "lunch", "test_preparation_course"]:
                if col in features.columns:
                    features[col] = features[col].replace({None: np.nan, "None": np.nan, "": np.nan}).fillna("Unknown")

            logging.info("Predict features row: %s", features.to_dict(orient="records")[0] if not features.empty else features)

            data_scaled = preprocessor.transform(features)
            preds = model.predict(data_scaled)
            return preds
        except Exception as e:
            raise CustomException(e,sys)
class CustomData:
    def __init__( self,
        gender: str,
        race_ethnicity: str,
        parental_level_of_education,
        lunch: str,
        test_preparation_course: str,
        reading_score: int,
        writing_score: int):

        self.gender = gender

        self.race_ethnicity = race_ethnicity

        self.parental_level_of_education = parental_level_of_education

        self.lunch = lunch

        self.test_preparation_course = test_preparation_course

        self.reading_score = reading_score

        self.writing_score = writing_score


    def get_data_as_data_frame(self):
        try:
            custom_data_input_dict= {
                "gender": [self.gender],
                "race_ethnicity": [self.race_ethnicity],
                "parental_level_of_education": [self.parental_level_of_education],
                "lunch": [self.lunch],
                "test_preparation_course": [self.test_preparation_course],
                "reading_score": [self.reading_score],
                "writing_score": [self.writing_score],
            }

            return pd.DataFrame(custom_data_input_dict)
        
        except Exception as e:
            raise CustomException(e,sys)
