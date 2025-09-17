from flask import Flask,request,render_template
import numpy as np
import pandas as pd

import pickle
import logging, traceback
logging.basicConfig(level=logging.INFO)
from sklearn.preprocessing import StandardScaler
from src.pipeline.predict_pipeline import CustomData,PredictPipeline
import logging
logging.basicConfig(level=logging.INFO)


application=Flask(__name__ )

app = application

## Route for a home page

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predictdata', methods=['GET','POST'])
def predict_datapoint():
    if request.method=='GET':
        return render_template('home.html')
    else:
        data=CustomData(
            gender = request.form.get('gender'),
            race_ethnicity = request.form.get('race_ethnicity'),
            parental_level_of_education = request.form.get('parental_level_of_education'),
            lunch = request.form.get('lunch'),
            test_preparation_course = request.form.get('test_preparation_course'),
            reading_score = request.form.get('reading_score'),
            writing_score = request.form.get('writing_score') 
        )
        pred_df = data.get_data_as_data_frame()
        # Sanitize/typer les données avant prédiction
        for col in ['reading_score', 'writing_score']:
            try:
                pred_df[col] = pd.to_numeric(pred_df[col], errors='coerce')
            except Exception:
                pass

        for col in ['gender','race_ethnicity','parental_level_of_education','lunch','test_preparation_course']:
            if col in pred_df.columns:
                pred_df[col] = pred_df[col].fillna('Unknown')

        app.logger.info("Row for predict: %s", pred_df.to_dict(orient='records')[0] if not pred_df.empty else pred_df)

        print(pred_df)

        predict_pipeline = PredictPipeline()

        try:
            results = predict_pipeline.predict(pred_df)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            app.logger.error("Predict failed: %s\n%s", e, tb)
    # TEMP: renvoie l’erreur à l’écran pour qu’on la voie (retire ensuite)
            return render_template('home.html', error=f"Predict error: {e}\n{tb}"), 500


        return render_template('home.html', results=results[0])
    
@app.route('/_version')
def version():
    import sys, sklearn, numpy, pandas
    return {
        "python": sys.version,
        "sklearn": sklearn.__version__,
        "numpy": numpy.__version__,
        "pandas": pandas.__version__,
    }

@app.errorhandler(500)
def handle_500(e):
    app.logger.error("Internal error: %s", e, exc_info=True)
    return render_template('home.html', error="Erreur pendant la prédiction (voir logs)."), 500
if __name__ == "__main__":

    app.run(host="0.0.0.0")

